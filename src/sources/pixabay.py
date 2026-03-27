from .base import BaseSource
from config import PIXABAY_API_KEY
import time


class PixabayAPI(BaseSource):

    def __init__(self):
        super().__init__("pixabay")

    def paginate(self, query, limit):
        url = "https://pixabay.com/api/"

        headers = {
            "User-Agent": "IndianDatasetBot/1.0"
        }

        page = 1
        per_page = 200
        collected = 0

        while collected < limit:

            params = {
                "key": PIXABAY_API_KEY,
                "q": query,
                "image_type": "photo",
                "per_page": per_page,
                "page": page,
                "min_width": 256
            }

            # 🔥 FIX: pass headers
            data = self.get(url, headers=headers, params=params)

            if "hits" not in data or len(data["hits"]) == 0:
                break

            for img in data["hits"]:

                yield {
                    "url": img["largeImageURL"],
                    "source": "pixabay",
                    "id": img["id"]
                }

                collected += 1

                if collected >= limit:
                    return

            page += 1

            # 🔥 RATE LIMIT
            print("⏳ Pixabay rate limit sleep...")
            time.sleep(1)