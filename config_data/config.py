import os
from dataclasses import dataclass
from dotenv import load_dotenv
from loguru import logger

load_dotenv()


@dataclass
class TelegramConfig:
    token: str


@dataclass
class DatabaseConfig:
    HOST: str
    PASSWORD: str
    USER: str
    PORT: str
    NAME: str


@dataclass
class MongoConfig:
    URL: str
    NAME: str


@dataclass
class Config:
    __instance = None

    def __new__(cls, *args, **kwargs):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)
        return cls.__instance

    tg_bot: TelegramConfig
    db: DatabaseConfig
    mongo_db: MongoConfig


def load_config() -> Config:
    logger.info("config loading")
    config = Config(
        tg_bot=TelegramConfig(token=os.environ.get('TELEGRAM_TOKEN')),
        db=DatabaseConfig(
            HOST=os.environ.get('DB_HOST'),
            PASSWORD=os.environ.get('DB_PASSWORD'),
            USER=os.environ.get('DB_USER'),
            PORT=os.environ.get('DB_PORT'),
            NAME=os.environ.get('DB_NAME'),
        ),
        mongo_db=MongoConfig(
            os.environ.get('MONGO_URL'),
            os.environ.get('MONGO_NAME')
        )
    )

    return config
