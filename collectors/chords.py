from bs4 import BeautifulSoup
import requests
import utils
import json
import re


class EchordsCollector:
    def __init__(self, config):
        self._base_uri = config["base_uri"]

    def _get_html(self, url, params=None, headers=None):
        response = requests.get(url=url, params=params, headers=headers)
        response.raise_for_status()
        return response.content

    def _format(self, str):
        words = utils.simplify_str(str).split(" ")
        return "-".join(words)

    def collect(self, artist_name, song_name):
        url = self._base_uri.format(self._format(artist_name),
                                    self._format(song_name))
        html_content = self._get_html(url)
        soup = BeautifulSoup(html_content, 'html.parser')
        return [chord.text for chord in soup.select('#core u')]


class UltimateGuitarCollector:
    def __init__(self, config):
        self._base_uri = config["base_uri"]
        self._chord_pattern = r"(\[ch\])([A-G]+)(\/[A-G]*[b#])*([(?m)|(?m\d)" + \
                               "|(?b\d)|(?#\d)|(?maj\d)|(?add\d)|(?sus\d)|" + \
                               "(?aug)|(?aug\d)|(?dim)|(?dim\d)]*)" + \
                               "(\/[A-G]*[b#])*(\[\/ch\])"

    def _get_dict(self, url):
        response = requests.get(url=url)
        soup = BeautifulSoup(response.content, 'html.parser')
        script = soup.find('script', text=re.compile('window.UGAPP.store.page'))
        json_text = re.search(r'^\s*window\.UGAPP\.store\.page\s*=\s*({.*?})\s*;\s*$', \
                              script.string, flags=re.DOTALL | re.MULTILINE).group(1)
        return json.loads(json_text)

    def _format_uri(self, artist_name, song_name):
        artist = "+".join(artist_name.lower().split(" "))
        song = "+".join(song_name.lower().split(" "))
        artist_and_song = artist + "+" + song
        return self._base_uri.format(artist_and_song)

    def collect(self, artist_name, song_name):
        data = self._get_dict(self._format_uri(artist_name, song_name))

        if not data["data"].get("not_found", False):
            tabs = [tab for tab in data["data"]["results"]
                    if not tab.get("marketing_type")
                    and tab.get("type_name", "Other") == "Chords"]
        else:
            tabs = []

        for tab in tabs:
            chord_data = self._get_dict(tab["tab_url"])
            raw_chords = chord_data['data']['tab_view']['wiki_tab']['content']
            prog = re.compile(self._chord_pattern)
            result = prog.findall(raw_chords)

            chords = result
            for i in range(len(result)):
                chords[i] = result[i][1] + result[i][2] + result[i][3] + result[i][4]

            if [c.lower() for c in chords[:6]] == ["e", "a", "d", "g", "b", "e"]:
                chords = chords[6:]

            if chords:
                return chords

        return []
