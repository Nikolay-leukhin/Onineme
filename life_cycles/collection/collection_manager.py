import asyncio

from loguru import logger

from data.database.database import DataBase
from external_services.scraper.scraper import Scraper
from project_enums.urls import DataLinks


class CollectionManager:
    duration = 86400
    retry_duration = 3600

    def __init__(self, scraper: Scraper, database: DataBase):
        self.scraper = scraper
        self.database = database

    async def update_collection(self):
        anime_list1 = await self.scraper.parse_anime_collection(DataLinks.ongoing_page.value)
        anime_list2 = await self.scraper.parse_anime_collection(DataLinks.season_page.value)
        list_to_add = [
                          item for item in anime_list2 if item not in anime_list1
                      ] + anime_list1

        self.database.write_animes_to_base(list_to_add)

    async def start_updating_collection_loop(self):
        while True:
            try:
                await self.update_collection()
            except Exception:
                logger.exception(f"anime list update failed | retry in {self.retry_duration}s")
                await asyncio.sleep(self.retry_duration)
                continue

            logger.success(f"anime list updated | waiting {self.duration} for next update".upper())
            await asyncio.sleep(self.duration)
