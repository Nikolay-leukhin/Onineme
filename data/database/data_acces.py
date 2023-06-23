from loguru import logger
from sqlalchemy import and_

from data.database.database_connection import DatabaseConnection
from data.models.models import Titles, Users, UsersTitles
from data.schemas.anime_subscription_schema import AnimeSubscriptionSchema
from data.schemas.anime_title_schema import AnimeTitleSchema
from data.schemas.user_schema import UserSchema
from project_enums.status import Status


class DataAccess:
    def __init__(self, conn: DatabaseConnection):
        self.conn = conn

    def write_animes_to_base(self, anime_list: list[AnimeTitleSchema]) -> None:
        existed_items = [item.name for item in self.select_all_animes()]
        items_to_add = [Titles(**anime.__dict__) for anime in anime_list if anime.name not in existed_items]
        with self.conn.SQLSession() as session:
            try:
                session.add_all(items_to_add)
                session.commit()

                logger.info("animes were written")
            except Exception as ex:
                logger.error(ex)

    def register_user(self, user: UserSchema) -> None:
        with self.conn.SQLSession() as session:
            request = session.add(Users(**user.__dict__))
            session.commit()

            logger.info(f'USER ADDED {user}')

    def register_subscription(self, subscription: AnimeSubscriptionSchema) -> Status:
        subscription_exist: bool = self.is_subscription_exist(
            chat_id=subscription.user_id,
            anime_id=subscription.title_id
        )
        logger.info(f"EXISTING CHECK FOR {subscription}\nRESULT: {subscription_exist}")
        if subscription_exist:
            return Status.failed

        with self.conn.SQLSession() as session:
            request = session.add(UsersTitles(**subscription.__dict__))
            session.commit()
            logger.info(f'SUBSCRIPTION EXECUTED {subscription}')
            return Status.success

    def delete_subscription(self, chat_id: int, anime_id: int) -> None:
        with self.conn.SQLSession() as session:
            delete_query = session.query(UsersTitles) \
                .where(and_(UsersTitles.user_id == chat_id, UsersTitles.title_id == anime_id)).delete()
            session.commit()
            logger.info(f'success deleting of {anime_id} for {chat_id}')

    def is_user_exist(self, chat: int) -> bool:
        with self.conn.SQLSession() as session:
            users = session.query(Users).where(Users.chat_id == chat).all()
            return users != []

    def select_user_subscriptions(self, chat_id: int) -> list:
        with self.conn.SQLSession() as session:
            response = session.query(Titles).join(UsersTitles).filter(UsersTitles.user_id == chat_id).all()
            return response

    def select_anime_id_by_name(self, anime_name: str):
        with self.conn.SQLSession() as session:
            response = session.query(Titles.id).filter(Titles.name == anime_name.upper()).first()
            return response

    def select_subscribers_by_title_id(self, anime_id: int) -> list:
        with self.conn.SQLSession() as session:
            subs = session.query(UsersTitles.user_id).filter(UsersTitles.title_id == anime_id).all()
            return subs

    def select_anime_by_id(self, anime_id: int):
        with self.conn.SQLSession() as session:
            response = session.query(Titles).filter(Titles.id == anime_id).first()
            return response

    def select_all_animes(self) -> list[AnimeTitleSchema]:
        with self.conn.SQLSession() as session:
            response = session.query(Titles).all()
            anime_titles: list[AnimeTitleSchema] = [
                AnimeTitleSchema(
                    id=item.id,
                    image_path=item.image_path[:-3],
                    is_ended=item.is_ended,
                    start=item.scenes_went,
                    end=item.scenes_total,
                    name=item.name,
                    link=item.link,
                ) for item in response
            ]

            return anime_titles

    def is_subscription_exist(self, chat_id: int, anime_id: int) -> bool:
        logger.info(f"{chat_id}, {anime_id} anime and user ----")
        with self.conn.SQLSession() as session:
            response = session.query(UsersTitles) \
                .where(and_(UsersTitles.user_id == chat_id, UsersTitles.title_id == anime_id)).all()
            return response.__len__() >= 1

    def select_all_not_ended_animes(self) -> list[AnimeTitleSchema]:
        with self.conn.SQLSession() as session:
            response = session.query(Titles).filter(Titles.is_ended == False).all()
            anime_titles: list[AnimeTitleSchema] = [
                AnimeTitleSchema(
                    id=item.id,
                    image_path=item.image_path[:-3],
                    is_ended=item.is_ended,
                    start=item.scenes_went,
                    end=item.scenes_total,
                    name=item.name,
                    link=item.link,
                ) for item in response
            ]

            return anime_titles

    def update_anime_new_scene(self, anime_id: int, new_scene: int):
        with self.conn.SQLSession() as session:
            request = session.query(Titles)\
                .filter(Titles.id == anime_id)\
                .update({'scenes_went': new_scene})
            session.commit()

            logger.success(f"UPDATE SCENES_WENT FOR {anime_id} - scene {new_scene}")

    def update_anime_status(self, anime_id: int, status: bool):
        with self.conn.SQLSession() as session:
            requests = session.query(Titles)\
                .filter(Titles.id == anime_id)\
                .update({'is_ended': status})
            session.commit()
            logger.success(f"{anime_id} status updates to {status}")
