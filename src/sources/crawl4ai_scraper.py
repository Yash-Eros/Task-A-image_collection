import asyncio
from crawl4ai import AsyncWebCrawler


class Crawl4AIScraper:
    name = "crawl4ai"

    def __init__(self):
        self.targets = [
            "https://www.rawpixel.com/search/",
            "https://www.flickr.com/search/"
        ]

    async def paginate(self, query, limit=20):
            import requests
            from bs4 import BeautifulSoup

            url = f"https://www.bing.com/images/search?q={query}"

            try:
                res = requests.get(url, timeout=10)
                soup = BeautifulSoup(res.text, "html.parser")

                images = soup.find_all("img")

                count = 0

                for img in images:
                    src = img.get("src")

                    if src and "http" in src:
                        yield {
                            "id": src,
                            "url": src
                        }

                        count += 1
                        if count >= limit:
                            break

            except Exception as e:
                print(f"❌ Crawl4AI error: {e}")