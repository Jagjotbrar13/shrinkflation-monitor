from collections.abc import Iterable

from scraper.normalizer import ProductObservation


class GrocerySpider:
    store_name: str

    async def scrape_products(self, urls: Iterable[str]) -> list[ProductObservation]:
        return []
