from .base import BaseSource
from config import SMITHSONIAN_API_KEY
import time


class SmithsonianAPI(BaseSource):

    def __init__(self):
        super().__init__("smithsonian")

    def paginate(self, query, limit):
        url = "https://api.si.edu/openaccess/api/v1.0/search"

        headers = {
            "User-Agent": "IndianDatasetBot/1.0"
        }

        page = 0
        collected = 0

        while collected < limit:

            params = {
                "api_key": SMITHSONIAN_API_KEY,
                "q": query,
                "start": page * 100,
                "rows": 100
            }

            # ✅ FIX: pass headers
            data = self.get(url, headers=headers, params=params)

            items = data.get("response", {}).get("rows", [])

            if not items:
                break

            for item in items:
                try:
                    media_list = item["content"]["descriptiveNonRepeating"]["online_media"]["media"]

                    for media in media_list:
                        image_url = media.get("content")

                        if not image_url:
                            continue

                        yield {
                            "url": image_url,
                            "source": "smithsonian",
                            "id": item.get("id", "")
                        }

                        collected += 1

                        if collected >= limit:
                            return

                except:
                    continue

            page += 1

            # 🔥 RATE LIMIT
            print("⏳ Smithsonian rate limit sleep...")
            time.sleep(1)