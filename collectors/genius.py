from bs4 import BeautifulSoup
import pandas as pd
import requests
import utils
import re


class GeniusCollector:
    def __init__(self, config):
        self._base_uri = config["base_uri"]
        self._client_token = config["client_token"]
        self._section_headers = config["section_headers"]

    def _get(self, path, params=None, headers=None):
        url = '/'.join([self._base_uri, path])
        token = "Bearer {}".format(self._client_token)
        if headers:
            headers['Authorization'] = token
        else:
            headers = {"Authorization": token}
        response = requests.get(url=url, params=params, headers=headers)
        response.raise_for_status()
        return response.json()

    def _get_artist_songs(self, artist_id):
        current_page = 1
        next_page = True
        songs = []
        while next_page:
            path = "artists/{0}/songs/".format(artist_id)
            params = {'page': current_page}
            data = self._get(path, params=params)
            page_songs = data['response']['songs']
            if page_songs:
                songs += page_songs
                current_page += 1
            else:
                next_page = False
        return songs

    def _scrape_lyrics(self, url):
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        lyrics = soup.find("div", {"class": "lyrics"}).get_text()
        if not self._section_headers:
            lyrics = re.sub('(\[.*?\])*', '', lyrics)
            lyrics = re.sub('\n{2}', '\n', lyrics)
        return lyrics.strip('\n')

    def collect(self, artist_id, store_json=False):
        songs = [song for song in self._get_artist_songs(artist_id)
                 if song['primary_artist']['id'] == artist_id]

        songs_df = pd.DataFrame(songs)
        songs_df["lyrics"] = songs_df["url"].apply(self._scrape_lyrics)
        songs_df.drop(columns=["annotation_count", "api_path", "full_title",
                               "header_image_thumbnail_url", "stats",
                               "header_image_url", "lyrics_owner_id",
                               "title_with_featured", "primary_artist",
                               "pyongs_count", "lyrics_state", "path",
                               "song_art_image_thumbnail_url"], inplace=True)

        if store_json:
            utils.write_json("data/genius.json", songs_df.to_dict("records"))

        return songs_df

    def _get_song_url(self, song_title, artist_name):
        path = "search"
        params = {"q": song_title + " " + artist_name}
        data = self._get(path, params=params)
        if (len(data['response']['hits']) == 0):
            return None
        return data['response']['hits'][0]['result']['url']

    def collect_song_lyrics(self, song_title, artist_name):
        try:
            song_url = self._get_song_url(song_title, artist_name)
            if (song_url):
                return self._scrape_lyrics(song_url)
            return None
        except Exception:
            return None
