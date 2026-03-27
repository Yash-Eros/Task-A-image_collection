from .base import BaseSource
from config import PEXELS_API_KEY
import time


class PexelsAPI(BaseSource):

    def __init__(self):
        super().__init__("pexels")
        self.api_key = PEXELS_API_KEY

    def paginate(self, query, limit):
        url = "https://api.pexels.com/v1/search"

        headers = {
            "Authorization": self.api_key,
            "User-Agent": "IndianDatasetBot/1.0"
        }

        page = 1
        per_page = 80
        collected = 0

        while collected < limit:

            params = {
                "query": query,
                "per_page": per_page,
                "page": page
            }

            data = self.get(url, headers=headers, params=params)

            if "photos" not in data or len(data["photos"]) == 0:
                break

            for photo in data["photos"]:

                yield {
                    "url": photo["src"]["original"],
                    "source": "pexels",
                    "id": photo["id"]
                }

                collected += 1

                if collected >= limit:
                    return

            page += 1

            # 🔥 RATE LIMIT
            print("⏳ Pexels rate limit sleep...")
            time.sleep(1)