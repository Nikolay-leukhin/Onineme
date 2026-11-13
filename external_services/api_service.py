import asyncio
import requests
from loguru import logger


class ApiService:
    request_timeout = 30
    max_pages = 50

    async def _get(self, url: str) -> requests.Response:
        return await asyncio.to_thread(requests.get, url, timeout=self.request_timeout)

    async def get_html_page(self, url: str) -> str:
        try:
            response = await self._get(url)
            if response.status_code != 200:
                logger.error(response.status_code)
                return ""

            return response.text

        except requests.exceptions.RequestException as ex:
            raise ex

    async def get_all_html_pages(self, url: str) -> str:
        duration = 2
        pages = ''
        for index in range(1, self.max_pages + 1):
            try:
                response = await self._get(f"{url}&page={index}")
            except requests.exceptions.RequestException as ex:
                raise ex

            if response.status_code != 200:
                logger.warning(f"page {index} returned {response.status_code}, stop paging")
                break

            if '<p class="error-404 display-3">404</p>' in response.text:
                break

            logger.info(f"---PAGE {index} PARSED ---")
            pages += response.text
            await asyncio.sleep(duration)
        else:
            logger.warning(f"page limit {self.max_pages} reached for {url}")

        return pages
