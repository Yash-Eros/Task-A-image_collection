import requests
import time
from src.sources.base import BaseSource


class UnsplashAPI(BaseSource):

    def __init__(self):
        super().__init__("unsplash")
        from config import UNSPLASH_ACCESS_KEY
        self.api_key = UNSPLASH_ACCESS_KEY

    def safe_request(self, url, headers=None, params=None, retries=3):
        """🔥 Retry + timeout wrapper"""
        for i in range(retries):
            try:
                res = requests.get(url, headers=headers, params=params, timeout=10)

                if res.status_code == 200:
                    return res

                elif res.status_code == 429:
                    print("⏳ Unsplash rate limited, retrying...")
                    time.sleep(2 + i)

                elif res.status_code >= 500:
                    print("⚠️ Unsplash server error, retrying...")
                    time.sleep(2 + i)

                else:
                    print(f"❌ Unsplash error: {res.status_code}")
                    return None

            except Exception as e:
                print(f"⚠️ Unsplash request failed: {e}")
                time.sleep(2)

        return None

    def paginate(self, query, limit):

        url = "https://api.unsplash.com/search/photos"

        headers = {
            "Authorization": f"Client-ID {self.api_key}",
            "User-Agent": "IndianDatasetBot/1.0"
        }

        page = 1
        collected = 0

        while collected < limit:

            params = {
                "query": query,
                "per_page": 30,
                "page": page
            }

            response = self.safe_request(url, headers=headers, params=params)

            if not response:
                break

            data = response.json()

            for img in data.get("results", []):

                if collected >= limit:
                    break

                img_id = img["id"]

                # ✅ REQUIRED: trigger download event (with safety)
                download_url = img["links"]["download_location"]

                try:
                    self.safe_request(download_url, headers=headers)
                    print(f"📥 Unsplash download triggered: {img_id}")
                except Exception as e:
                    print(f"⚠️ Unsplash trigger failed: {e}")

                yield {
                    "id": f"unsplash_{img_id}",
                    "url": img["urls"]["full"],
                    "source": "unsplash",
                    "meta": img
                }

                collected += 1

            page += 1

            # ✅ Rate limiting (safe)
            print("⏳ Unsplash rate limit sleep...")
            time.sleep(1)