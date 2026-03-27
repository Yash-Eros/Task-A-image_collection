import requests
from bs4 import BeautifulSoup
import time
import hashlib


class RawpixelScraper:

    def __init__(self):
        self.name = "rawpixel"
        self.base_url = "https://www.rawpixel.com/search/"

        # ✅ FIXED User-Agent
        self.headers = {
            "User-Agent": "IndianDatasetBot/1.0"
        }

    def generate_id(self, url):
        return hashlib.md5(url.encode()).hexdigest()

    def paginate(self, query, limit):
        collected = 0
        page = 1

        while collected < limit:
            try:
                url = f"{self.base_url}{query}?page={page}"

                response = requests.get(
                    url,
                    headers=self.headers,
                    timeout=10
                )

                soup = BeautifulSoup(response.text, "html.parser")
                images = soup.find_all("img")

                if not images:
                    break

                for img in images:

                    if collected >= limit:
                        break

                    src = img.get("src") or img.get("data-src")

                    if not src:
                        continue

                    # Skip icons/logos
                    if any(x in src.lower() for x in ["icon", "logo"]):
                        continue

                    yield {
                        "id": self.generate_id(src),
                        "url": src,
                        "source": self.name,
                        "query": query
                    }

                    collected += 1

                page += 1

                # 🔥 RATE LIMIT
                print("⏳ Rawpixel rate limit sleep...")
                time.sleep(1.5)

            except Exception as e:
                print(f"[Rawpixel ERROR] {e}")
                break