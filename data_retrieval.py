from persistence.mongodb import MongoDBDriver
from collectors.spotify import SpotifyCollector
from collectors.genius import GeniusCollector
import pandas as pd
import utils
import re


def simplify_str(str):
    return re.sub(r'[^\w\s]','',str).lower()


def main():
    config = utils.read_json("config/config.json")

    mongo_driver = MongoDBDriver(config["mongodb"])
    genius_collector = GeniusCollector(config["genius"])
    spotify_collector = SpotifyCollector(config["spotify"])

    mongo_driver.clean_db()

    genius_df = genius_collector.collect(config["artist_id"], store_json=True)
    spotify_df = spotify_collector.collect(config["artist_name"],
                                           config["album_blacklist"],
                                           store_json=True)

    left_key = spotify_df["name"].apply(simplify_str)
    right_key = genius_df["title"].apply(simplify_str)
    df = pd.merge(spotify_df, genius_df, how='left', left_on=left_key,
                  right_on=right_key, suffixes=("_spotify", "_genius"),
                  validate="one_to_one").drop(columns=["key_0", "title"])

    mongo_driver.add_discography(config["artist_name"], df)
    utils.write_json("data/data.json", df.to_dict("records"))


if __name__ == "__main__":
    main()
