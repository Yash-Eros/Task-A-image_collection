from .base import BaseSource
from config import EUROPEANA_API_KEY
import time


class EuropeanaAPI(BaseSource):

    def __init__(self):
        super().__init__("europeana")

    def paginate(self, query, limit):
        url = "https://api.europeana.eu/record/v2/search.json"

        headers = {
            "User-Agent": "IndianDatasetBot/1.0"
        }

        page = 1
        collected = 0
        consecutive_errors = 0
        MAX_CONSECUTIVE_ERRORS = 3

        while collected < limit:

            params = {
                "query": query,
                "wskey": EUROPEANA_API_KEY,
                "rows": 100,
                "start": (page - 1) * 100,
                "media": "true"
            }

            try:
                # ✅ FIX: pass headers with better error handling
                data = self.get(url, headers=headers, params=params)

                items = data.get("items", [])

                if not items:
                    break

                consecutive_errors = 0  # Reset error counter on success

                for item in items:

                    image_url = item.get("edmIsShownBy") or (
                        item.get("edmPreview")[0] if item.get("edmPreview") else None
                    )

                    if not image_url:
                        continue

                    yield {
                        "url": image_url,
                        "source": "europeana",
                        "id": item.get("id", "")
                    }

                    collected += 1

                    if collected >= limit:
                        return

                page += 1

                # 🔥 RATE LIMIT
                time.sleep(1)
                
            except Exception as e:
                consecutive_errors += 1
                if consecutive_errors >= MAX_CONSECUTIVE_ERRORS:
                    print(f"⚠️ Europeana: Too many errors ({consecutive_errors}), stopping pagination for this query")
                    break
                print(f"⚠️ Europeana error on page {page}: {str(e)[:100]}")
                time.sleep(2)  # Longer wait before retry
                continue