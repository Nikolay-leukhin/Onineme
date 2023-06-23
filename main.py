import asyncio

from aiogram import Bot, Dispatcher
from config_data.config import load_config, Config
from data.database.database import DataBase
from life_cycles.collection.collection_manager import CollectionManager
from life_cycles.update.update_controller import UpdateController
from data.updates_db.updates_connection import UpdatesConnection
from external_services.api_service import ApiService
from external_services.scraper.scraper import Scraper
from bot.keyboards.menu_keys import menu_commands

from bot.handlers.user_handlers import router as user_router
from bot.handlers.callback_handlers import router as callback_router


async def main():
    config: Config = load_config()

    database: DataBase = DataBase(config=config.db)

    updates_store: UpdatesConnection = UpdatesConnection(config=config)
    scraper: Scraper = Scraper(api=ApiService(), db=database)
    bot: Bot = Bot(config.tg_bot.token)

    updater: UpdateController = UpdateController(update_store=updates_store, scraper=scraper, bot=bot, db=database)
    collection_manager: CollectionManager = CollectionManager(scraper=scraper, database=database)

    dp: Dispatcher = Dispatcher()

    dp.include_router(user_router)
    dp.include_router(callback_router)

    await bot.set_my_commands(menu_commands)
    await bot.delete_webhook(drop_pending_updates=True)

    bot_task = asyncio.create_task(dp.start_polling(bot))
    ongoing_task = asyncio.create_task(collection_manager.start_updating_collection_loop())
    update_task = asyncio.create_task(updater.start_mailing_update_loop())

    await asyncio.gather(bot_task, ongoing_task, update_task)


if __name__ == '__main__':
    asyncio.run(main())
