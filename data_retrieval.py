from persistence.mongodb import MongoDBDriver
from collectors.spotify import SpotifyCollector
from collectors.genius import GeniusCollector
from collectors.chords import ChordCollector
import pandas as pd
import utils


def main():
    config = utils.read_json("config/config.json")

    artist_name = config["artist_name"]
    mongo_driver = MongoDBDriver(config["mongodb"])
    chord_collector = ChordCollector(config["chords"])
    genius_collector = GeniusCollector(config["genius"])
    spotify_collector = SpotifyCollector(config["spotify"])

    mongo_driver.clean_db()

    genius_df = genius_collector.collect(config["artist_id"], store_json=True)
    spotify_df = spotify_collector.collect(artist_name,
                                           config["album_blacklist"],
                                           store_json=True)

    left_key = spotify_df["name"].apply(utils.simplify_str)
    right_key = genius_df["title"].apply(utils.simplify_str)
    df = pd.merge(spotify_df, genius_df, how='left', left_on=left_key,
                  right_on=right_key, suffixes=("_spotify", "_genius"),
                  validate="one_to_one").drop(columns=["key_0", "title"])

    df["chords"] = df.apply(lambda x: chord_collector.collect(artist_name,
                                                              x["name"]),
                            axis=1)

    mongo_driver.add_discography(artist_name, df)
    utils.write_json("data/data.json", df.to_dict("records"))


if __name__ == "__main__":
    main()
