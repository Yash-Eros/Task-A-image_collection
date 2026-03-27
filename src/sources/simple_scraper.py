import requests
from bs4 import BeautifulSoup
import uuid


class SimpleScraper:
    def __init__(self):
        self.name = "simple_scraper"

    def paginate(self, query, limit=10):
    

        results = []

        # ✅ MAP QUERY → CATEGORY (important)
        category_map = {
            "dosa": "Dosa",
            "biryani": "Biryani",
            "paneer": "Paneer dishes",
            "samosa": "Samosas",
            "jalebi": "Jalebi",
            "gulab jamun": "Gulab jamun",
            "indian food": "Indian cuisine",
            "chai": "Tea in India",
            "street food": "Street food in India"
        }

        clean_query = query.lower()

        category = "Indian cuisine"  # default

        for key in category_map:
            if key in clean_query:
                category = category_map[key]
                break

        url = "https://commons.wikimedia.org/w/api.php"

        params = {
            "action": "query",
            "generator": "categorymembers",
            "gcmtitle": f"Category:{category}",
            "gcmlimit": limit,
            "prop": "imageinfo",
            "iiprop": "url",
            "format": "json"
        }

        headers = {
            "User-Agent": "Mozilla/5.0"
        }

        try:
            res = requests.get(url, params=params, headers=headers, timeout=10)

            data = res.json()

            pages = data.get("query", {}).get("pages", {})

            for page in pages.values():
                if "imageinfo" not in page:
                    continue

                img_url = page["imageinfo"][0]["url"]

                if not img_url.lower().endswith((".jpg", ".jpeg", ".png")):
                    continue

                results.append({
                    "id": str(uuid.uuid4()),
                    "url": img_url,
                    "source": self.name,
                    "title":query,
                    "tags":query.split(),
                    "description": query

                })

                if len(results) >= limit:
                    break

        except Exception as e:
            print(f"⚠️ SimpleScraper error: {e}")

        print(f"[SimpleScraper] Found {len(results)} images for query: {query} (category: {category})")

        return results