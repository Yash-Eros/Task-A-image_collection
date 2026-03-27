from .base import BaseSource
from config import NYPL_API_KEY
import time


class NYPLAPI(BaseSource):

    def __init__(self):
        super().__init__("nypl")

    def paginate(self, query, limit):
        url = "https://api.repo.nypl.org/api/v1/items/search"

        headers = {
            "Authorization": f"Token {NYPL_API_KEY}",
            "User-Agent": "IndianDatasetBot/1.0"
        }

        page = 1
        collected = 0

        while collected < limit:

            params = {
                "q": query,
                "page": page
            }

            data = self.get(url, headers=headers, params=params)

            docs = data.get("nyplAPI", {}).get("response", {}).get("docs", [])

            if not docs:
                break

            for doc in docs:

                if "imageID" not in doc:
                    continue

                image_url = f"https://images.nypl.org/index.php?id={doc['imageID']}&t=w"

                yield {
                    "url": image_url,
                    "source": "nypl",
                    "id": doc.get("uuid", "")
                }

                collected += 1

                if collected >= limit:
                    return

            page += 1

            # 🔥 RATE LIMIT
            print("⏳ NYPL rate limit sleep...")
            time.sleep(1)