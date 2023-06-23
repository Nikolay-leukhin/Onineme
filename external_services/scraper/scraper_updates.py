import re

from data.schemas.update_anime_schema import UpdateSchema
from external_services.scraper.scraper_data_fetcher import ScraperDataFetcher


class ScraperUpdates:
    def __init__(self, data_fetcher: ScraperDataFetcher):
        self.data_fetcher = data_fetcher

    async def parse_anime_updates_list(self, link: str) -> list[UpdateSchema]:
        doc = await self.data_fetcher.get_page(link)
        updates = doc.find('div', {'id': 'slide-toggle-1'})\
            .findAll('div', {"class": 'last-update-item'})
        anime_update_list: list[UpdateSchema] = list(filter(
            lambda update: update is not None,
            map(lambda item: self.parse_anime_update_item(item), updates)
        ))

        return anime_update_list

    def parse_anime_update_item(self, doc):
        name: str = self.get_anime_update_name(doc)
        info = doc.find('div', {'class': 'text-right'})
        new_scene: int = self.get_anime_update_scene(info)
        sound: str = self.get_anime_update_sound(info)
        anime_id = self.data_fetcher.get_anime_update_id(anime_name=name)

        if anime_id is None:
            return

        anime_update_subs: [dict] = self.data_fetcher.get_anime_update_subscribers(anime_id)

        anime_update: UpdateSchema = UpdateSchema(
            anime_id=anime_id,
            sound=sound,
            user_list=anime_update_subs,
            scene=new_scene,
        )
        return anime_update

    def get_anime_update_name(self, doc) -> str:
        return doc.find('span', {'class': 'last-update-title'}).text

    def get_anime_update_sound(self, info) -> str:
        return info.find(string=re.compile('\(.*\)'))

    def get_anime_update_scene(self, info) -> int:
        return int(info.find(string=re.compile('.*\с\е\р\и\я'))[:-6])
