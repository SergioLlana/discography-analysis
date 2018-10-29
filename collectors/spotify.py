from spotipy.oauth2 import SpotifyClientCredentials
import pandas as pd
import spotipy


class SpotifyCollector:
    def __init__(self, config):
        client_id = config["client_id"]
        secret = config["client_secret"]
        manager = SpotifyClientCredentials(client_id=client_id,
                                           client_secret=secret)
        self._client = spotipy.Spotify(client_credentials_manager=manager)

    def collect(self, artist_name, album_blacklist=[], store_csv=False):
        query = "artist:" + artist_name
        query_result = self._client.search(q=query, type="artist")
        artist_id = query_result["artists"]["items"][0]["id"]
        artist_albums = self._client.artist_albums(artist_id,
                                                   album_type="album")
        albums = {x["name"]: {"id": x["id"], "year": x["release_date"][:4]}
                  for x in artist_albums["items"]}

        # Delete unwanted albums
        for album_name in album_blacklist:
            del albums[album_name]

        # DataFrame creation
        group_df = pd.DataFrame()
        for title, album_info in albums.items():
            album_id = album_info["id"]
            df = pd.DataFrame(self._client.album_tracks(album_id)["items"])
            df["album"] = title
            df["year"] = album_info["year"]
            group_df = pd.concat([group_df, df]) if group_df.shape[0] \
                       else pd.DataFrame(df)

        group_df.drop(columns=["artists", "available_markets", "explicit",
                               "external_urls", "href", "is_local", "type",
                               "preview_url", "disc_number", "duration_ms"],
                      inplace=True)
        group_df.reset_index(inplace=True)

        # Adding audio_analysis and audio_features information
        for idx, row in group_df.iterrows():
            analysis = self._client.audio_analysis(row["id"])
            features = self._client.audio_features([row["id"]])[0]
            group_df.at[idx, "duration_s"] = analysis["track"]["duration"]
            group_df.at[idx, "acousticness"] = features["acousticness"]
            group_df.at[idx, "danceability"] = features["danceability"]
            group_df.at[idx, "energy"] = features["energy"]
            group_df.at[idx, "key"] = features["key"]
            group_df.at[idx, "tempo"] = features["tempo"]
            group_df.at[idx, "time_signature"] = features["time_signature"]
            group_df.at[idx, "valence"] = features["valence"]
            group_df.at[idx, "mode"] = features["mode"]

        if store_csv:
            group_df.to_csv("data/spotify.csv", header=True, index=False,
                            encoding="utf-8")

        return group_df
