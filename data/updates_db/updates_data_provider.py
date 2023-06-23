from bson import ObjectId
from loguru import logger

from data.database.database import DataBase
from data.schemas.update_anime_schema import UpdateSchema
from data.updates_db.updates_connection import UpdatesConnection
from external_services.scraper.scraper import Scraper
from project_enums.urls import DataLinks


class UpdateDataProvider:
    def __init__(self,
                 update_store: UpdatesConnection,
                 scraper: Scraper,
                 db: DataBase):
        self.update_store = update_store
        self.scraper = scraper
        self.db = db

    def get_store_data(self):
        store_data = self.update_store.collection.find({}, {"_id": False, 'user_list': False})
        return store_data

    async def get_raw_updates(self) -> list[UpdateSchema]:
        return await self.scraper.parse_anime_updates_list(DataLinks.main_page.value)

    async def get_unhandled_updates(self) -> list[dict]:
        store = list(self.get_store_data())
        raw_updates = self.get_raw_updates()
        new_updates = [item.__dict__ for item in await raw_updates if {'anime_id': item.anime_id, 'scene': item.scene, 'sound': item.sound} not in store]
        logger.info(f"UPDATES {new_updates}")
        return new_updates

    async def write_updates_to_store(self) -> list[ObjectId]:
        update_items = await self.get_unhandled_updates()
        if update_items:
            return self.update_store.collection.insert_many(
                update_items
            ).inserted_ids

        return []

    def update_user_mail_status(self, update_id: ObjectId, chat_id: int):
        self.update_store.collection.update_one(
            {"_id": update_id, 'user_list.user_id': chat_id},
            {"$set": {'user_list.$.status': True}}
        )

    def get_update_item(self, update_id: ObjectId):
        return self.update_store.collection.find_one({'_id': update_id})

    def update_anime_scene_number(self, anime_item, new_scene):
        db_scene = anime_item.scenes_went
        if db_scene > new_scene:
            return

        if anime_item.scenes_total == new_scene:
            self.db.update_anime_status(anime_item.id, status=True)

        self.db.update_anime_new_scene(anime_id=anime_item.id, new_scene=new_scene)