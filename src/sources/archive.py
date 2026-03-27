from .base import BaseSource
import time


class InternetArchiveAPI(BaseSource):

    def __init__(self):
        super().__init__("archive")

    def paginate(self, query, limit):
        url = "https://archive.org/advancedsearch.php"

        headers = {
            "User-Agent": "IndianDatasetBot/1.0"
        }

        page = 1
        collected = 0

        while collected < limit:

            params = {
                "q": query,
                "fl[]": "identifier",
                "rows": 100,
                "page": page,
                "output": "json"
            }

            # ✅ FIX: pass headers
            data = self.get(url, headers=headers, params=params)

            docs = data.get("response", {}).get("docs", [])

            if not docs:
                break

            for doc in docs:
                identifier = doc["identifier"]

                img_url = f"https://archive.org/download/{identifier}/{identifier}_itemimage.jpg"

                yield {
                    "url": img_url,
                    "source": "archive",
                    "id": identifier
                }

                collected += 1

                if collected >= limit:
                    return

            page += 1

            # 🔥 RATE LIMIT
            print("⏳ Archive rate limit sleep...")
            time.sleep(1)