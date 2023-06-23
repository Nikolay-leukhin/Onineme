from loguru import logger

from data.database.database_connection import DatabaseConnection
from data.models.models import Base


class DatabaseSchemaManager:
    def __init__(self, conn: DatabaseConnection):
        self.conn = conn

    def drop_all_schemas(self) -> None:
        logger.warning("database deleting started")
        Base.metadata.drop_all(self.conn.engine)  # maybe it should be fixed but idk how(about Base import)

    def create_all_schemas(self) -> None:
        logger.warning("database creation started")
        Base.metadata.create_all(bind=self.conn.engine)
