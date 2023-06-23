from bs4 import BeautifulSoup

from data.database.database import DataBase
from data.schemas.update_anime_schema import UserUpdateItem
from external_services.api_service import ApiService


class ScraperDataFetcher:
    def __init__(self, api: ApiService, db: DataBase):
        self.api = api
        self.db = db

    async def get_all_pages(self, url):
        page = await self.api.get_all_html_pages(url)
        doc = BeautifulSoup(page, 'html.parser')
        return doc

    async def get_page(self, link: str):
        page = await self.api.get_html_page(link)
        doc = BeautifulSoup(page, 'html.parser')
        return doc

    def get_anime_update_id(self, anime_name: str):
        id_response = self.db.select_anime_id_by_name(anime_name=anime_name.upper())
        anime_id = None
        if id_response is not None:
            anime_id = id_response.id

        return anime_id

    def get_anime_update_subscribers(self, anime_id: int) -> list[dict]:
        subscribers_response = self.db.select_subscribers_by_title_id(anime_id)
        anime_update_subs: [dict] = [
            UserUpdateItem(
                user_id=sub.user_id,
                status=False
            ).__dict__ for sub in subscribers_response
        ]

        return anime_update_subs
