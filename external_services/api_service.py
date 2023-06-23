import asyncio
import requests
from loguru import logger


class ApiService:
    async def get_html_page(self, url: str) -> str:
        try:
            response = requests.get(url)
            if response.status_code != 200:
                logger.error(response.status_code)
                return ""

            return response.text

        except requests.exceptions.RequestException as ex:
            raise ex

    async def get_all_html_pages(self, url: str) -> str:
        duration = 2
        pages = ''
        index = 1
        while True:
            try:
                response = requests.get(f"{url}&page={index}")
                if '<p class="error-404 display-3">404</p>' in response.text:
                    break

                print(f"---PAGE {index} PARSED ---")
                index += 1
                pages += response.text
                await asyncio.sleep(duration)
            except requests.exceptions.RequestException as ex:
                raise ex
        return pages
