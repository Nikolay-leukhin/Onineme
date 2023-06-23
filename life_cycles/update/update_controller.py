import asyncio

from aiogram import Bot
from aiogram.types import InlineKeyboardMarkup
from bson import ObjectId
from loguru import logger

from life_cycles.update.update_mailer import UpdateMailer
from data.updates_db.updates_data_provider import UpdateDataProvider
from data.database.database import DataBase
from data.updates_db.updates_connection import UpdatesConnection
from external_services.scraper.scraper import Scraper
from bot.keyboards.subscribe_key import create_watch_key


class UpdateController:
    duration = 180

    def __init__(self,
                 update_store: UpdatesConnection,
                 db: DataBase,
                 scraper: Scraper,
                 bot: Bot
                 ):
        self.data_provider = UpdateDataProvider(update_store=update_store, scraper=scraper, db=db)
        self.mailer = UpdateMailer(bot=bot)
        self.db = db

    async def start_mailing_updates(self):
        update_ids = await self.data_provider.write_updates_to_store()
        if update_ids:
            for up_id in update_ids:
                await self.process_update(up_id)
            logger.success('update pushed')
        else:
            logger.info('no updates_db => mongo updated declined')

    def create_update_text(self, anime_item, update_item):
        return f"🌵НОВАЯ СЕРИЯ🌵\n\n{anime_item.name}\n{update_item['scene']}-ая серия\n{update_item['sound']}"

    async def process_update(self, up_id: ObjectId):
        update_item = self.data_provider.get_update_item(up_id)
        anime_item = self.db.select_anime_by_id(update_item['anime_id'])

        self.data_provider.update_anime_scene_number(anime_item, update_item['scene'])

        item_text = self.create_update_text(anime_item, update_item)
        watch_keyboard = InlineKeyboardMarkup(
            inline_keyboard=[[create_watch_key(anime_item.link)]]
        )

        for item in update_item['user_list']:
            chat_id: int = item['user_id']
            status: bool = item['status']

            if status is True:
                continue

            await self.mailer.send_update_to_subscriber(
                chat_id=chat_id,
                image_path=anime_item.image_path[:-3],
                text=item_text,
                keyboard=watch_keyboard
            )

            self.data_provider.update_user_mail_status(chat_id=chat_id, update_id=up_id)
            logger.info(f"BOT SENT UPDATE TO {chat_id}\n{anime_item.name}")

    async def start_mailing_update_loop(self):
        while True:
            await self.start_mailing_updates()
            await asyncio.sleep(self.duration)
