import asyncio

from loguru import logger

from data.schemas.anime_title_schema import AnimeTitleSchema
from external_services.scraper.scraper_data_fetcher import ScraperDataFetcher


class ScraperAnimeCollection:
    def __init__(self, data_fetcher: ScraperDataFetcher):
        self.data_fetcher = data_fetcher

    async def parse_anime_collection(self, link) -> list[AnimeTitleSchema]:
        links = await self.parse_anime_link(link)
        anime_titles = [await self.parse_anime_main_page(link) for link in links]
        logger.info(f'--anime *{len(anime_titles)}* pages have parsed---')
        return anime_titles

    async def parse_anime_link(self, link) -> list[str]:
        doc = await self.data_fetcher.get_all_pages(link)
        items = doc.findAll('div', {'class': 'animes-list-item'})
        links = []
        for item in items:
            link = item.find('div', {'class': 'media-body'}).findChild('a')
            links.append(link['href'])
        return links

    async def parse_anime_main_page(self, link: str) -> AnimeTitleSchema:
        await asyncio.sleep(1)  # made to avoid 429 http error
        doc = await self.data_fetcher.get_page(link)

        name: str = self.get_anime_name(doc)
        start, end = self.get_scenes_info(doc)
        image_path: str = self.get_anime_image(doc)
        is_ended: bool = self.get_ending_status(start, end)

        item: AnimeTitleSchema = AnimeTitleSchema(
            name=name,
            start=start,
            end=end,
            image_path=image_path,
            is_ended=is_ended,
            link=link
        )
        return item

    def get_anime_image(self, doc) -> str:
        raw_image = doc.find('div', {'class': 'anime-poster'}).findChild('img')['srcset']
        image_path = raw_image[:19] + raw_image[46:]
        return image_path

    def get_anime_name(self, doc) -> str:
        return doc.find('div', {'class': 'anime-title'}).findChild('h1').text.upper()

    def get_scenes_info(self, doc) -> tuple:
        raw_timeframes = doc.find('div', {'class': 'anime-info'}).findChild('dt', string='Эпизоды')
        if raw_timeframes is None:
            return 0, 0

        timeframes = tuple(
            map(lambda item: int(item) if item.isnumeric() else None,
                raw_timeframes.nextSibling.text.split(
                    ' / '))
        )

        if timeframes.__len__() == 1:
            return timeframes, timeframes

        return timeframes

    def get_ending_status(self, start, end) -> bool:
        return start == end if start is not None else False

