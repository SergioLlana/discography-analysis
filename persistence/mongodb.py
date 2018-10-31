from pymongo import MongoClient
import logging


class MongoDBDriver:
    def __init__(self, config):
        uri = config["server_uri"].format(config["username"],
                                          config["password"])
        client = MongoClient(uri)
        self._db = client[config["database"]]
        self._logger = logging.getLogger(__name__)
        self._logger.debug("MongoDB driver initialized")

    def clean_db(self):
        self._db.songs.delete_many({})
        self._logger.debug("Wipping out MongoDB")

    def add_discography(self, artist_name, df):
        df["artist"] = artist_name
        self._db.songs.insert(df.to_dict("records"))

    """
    def get_discography(self, artist_name):
        return self._db.inventory.find({"artist": artist_name})
    """
