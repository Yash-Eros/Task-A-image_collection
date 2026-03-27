from .base import BaseSource
import time


class WikimediaAPI(BaseSource):

    def __init__(self):
        super().__init__("wikimedia")

    def paginate(self, query, limit):
        url = "https://commons.wikimedia.org/w/api.php"

        headers = {
            "User-Agent": "IndianDatasetBot/1.0"
        }

        page = 0
        collected = 0

        # 🔥 FIX: limit pages to prevent infinite loop
        max_pages = 5

        while collected < limit and page < max_pages:

            params = {
                "action": "query",
                "generator": "search",
                "gsrsearch": query,
                "gsrlimit": 50,
                "prop": "imageinfo",
                "iiprop": "url",
                "format": "json"
            }

            try:
                data = self.get(url, headers=headers, params=params)
            except Exception as e:
                print(f"⚠️ Wikimedia request failed: {e}")
                break

            # 🔥 FIX: stop if no valid data
            if not data or "query" not in data:
                print("⚠️ Wikimedia no data, stopping...")
                break

            pages = data.get("query", {}).get("pages", {})

            if not pages:
                break

            for page_data in pages.values():
                try:
                    url_img = page_data["imageinfo"][0]["url"]

                    yield {
                        "url": url_img,
                        "source": "wikimedia",
                        "id": page_data["pageid"]
                    }

                    collected += 1

                    if collected >= limit:
                        return

                except:
                    continue

            page += 1

            # 🔥 RATE LIMIT (safe now)
            print("⏳ Wikimedia rate limit sleep...")
            time.sleep(1)

        # 🔥 FINAL SAFETY EXIT
        print("⚠️ Wikimedia stopped (limit reached or no more data)")