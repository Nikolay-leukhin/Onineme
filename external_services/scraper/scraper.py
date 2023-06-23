from data.database.database import DataBase
from external_services.api_service import ApiService
from external_services.scraper.scraper_anime_collection import ScraperAnimeCollection
from external_services.scraper.scraper_data_fetcher import ScraperDataFetcher
from external_services.scraper.scraper_updates import ScraperUpdates


class Scraper:
    def __init__(self, api: ApiService, db: DataBase):
        self.api = api
        self.db = db
        self.data_fetcher: ScraperDataFetcher = ScraperDataFetcher(db=self.db, api=self.api)
        self.collector: ScraperAnimeCollection = ScraperAnimeCollection(data_fetcher=self.data_fetcher)
        self.updater: ScraperUpdates = ScraperUpdates(data_fetcher=self.data_fetcher)

    async def parse_anime_collection(self, link: str):
        return await self.collector.parse_anime_collection(link)

    async def parse_anime_updates_list(self, link: str):
        return await self.updater.parse_anime_updates_list(link)










