from loguru import logger
import pymongo

from config_data.config import Config


class UpdatesConnection:
    def __init__(self, config: Config):
        self.client = pymongo.MongoClient(config.mongo_db.URL)
        self.db = self.client[config.mongo_db.NAME]
        self.collection = self.db['updates_db']

        logger.info('SUCCESS MONGO CONNECTION')
