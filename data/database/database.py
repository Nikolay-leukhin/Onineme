from config_data.config import DatabaseConfig
from data.database.data_acces import DataAccess
from data.database.database_connection import DatabaseConnection
from data.database.database_schema_manager import DatabaseSchemaManager
from data.schemas.anime_subscription_schema import AnimeSubscriptionSchema
from data.schemas.anime_title_schema import AnimeTitleSchema
from data.schemas.user_schema import UserSchema


class DataBase:
    __instance = None

    def __new__(cls, *args, **kwargs):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)
        return cls.__instance

    def __init__(self, config: DatabaseConfig):
        self.config = config

        self.conn: DatabaseConnection = DatabaseConnection(config)
        self.db_access: DataAccess = DataAccess(self.conn)
        self.schema_manager: DatabaseSchemaManager = DatabaseSchemaManager(self.conn)

    def delete_subscription(self, chat_id: int, anime_id: int):
        return self.db_access.delete_subscription(chat_id, anime_id)

    def register_subscription(self, subscription: AnimeSubscriptionSchema):
        return self.db_access.register_subscription(subscription)

    def is_user_exist(self, chat_id: int) -> bool:
        return self.db_access.is_user_exist(chat_id)

    def select_all_animes(self) -> list[AnimeTitleSchema]:
        return self.db_access.select_all_animes()

    def select_all_not_ended_animes(self) -> list[AnimeTitleSchema]:
        return self.db_access.select_all_not_ended_animes()

    def select_user_subscriptions(self, chat_id) -> list:
        return self.db_access.select_user_subscriptions(chat_id)

    def register_user(self, user_model: UserSchema):
        return self.db_access.register_user(user_model)

    def select_anime_id_by_name(self, anime_name: str):
        return self.db_access.select_anime_id_by_name(anime_name)

    def select_subscribers_by_title_id(self, anime_id: int):
        return self.db_access.select_subscribers_by_title_id(anime_id)

    def write_animes_to_base(self, animes: list[AnimeTitleSchema]):
        return self.db_access.write_animes_to_base(animes)

    def select_anime_by_id(self, anime_id: int):
        return self.db_access.select_anime_by_id(anime_id)

    def update_anime_new_scene(self, anime_id: int, new_scene: int):
        return self.db_access.update_anime_new_scene(anime_id, new_scene)

    def update_anime_status(self, anime_id: int, status: bool):
        return self.db_access.update_anime_status(anime_id, status)
