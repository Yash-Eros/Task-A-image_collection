import os
import requests
import uuid
import asyncio
import shutil

class ImageDownloader:
    def __init__(self, save_dir):
        self.save_dir = save_dir
        os.makedirs(save_dir, exist_ok=True)

  

    async def download(self, img):
        url = img.get("url")
        is_local = img.get("is_local", False)

        if not url:
            return None

        # ✅ Handle local files (from web scrapers like Bing)
        if is_local:
            if not os.path.exists(url):
                print(f"❌ Local file not found: {url}")
                return None
            
            try:
                ext = os.path.splitext(url)[1] or ".jpg"
                filename = f"{uuid.uuid4()}{ext}"
                path = os.path.join(self.save_dir, filename)
                
                shutil.copy2(url, path)
                
                print("✅ Copied local file:", path)
                return path
            except Exception as e:
                print(f"❌ Error copying local file: {e}")
                return None

        # ✅ Handle remote URLs (from APIs)
        headers = {
            "User-Agent": "Mozilla/5.0"
        }

        for attempt in range(3):  # retry 3 times
            try:
                response = requests.get(url, headers=headers, timeout=10, stream=True)

                if response.status_code == 429:
                    print("⏳ Rate limited, sleeping...")
                    await asyncio.sleep(2 + attempt)  # backoff
                    continue

                if response.status_code != 200:
                    print("❌ Bad status:", response.status_code)
                    return None

                if "image" not in response.headers.get("Content-Type", ""):
                    return None

                ext = "jpg"
                filename = f"{uuid.uuid4()}.{ext}"
                path = os.path.join(self.save_dir, filename)

                with open(path, "wb") as f:
                    for chunk in response.iter_content(1024):
                        f.write(chunk)

                await asyncio.sleep(1)  # 🔥 IMPORTANT: slow down

                print("✅ Downloaded:", path)
                return path

            except Exception as e:
                print("❌ Download error:", e)

        return None