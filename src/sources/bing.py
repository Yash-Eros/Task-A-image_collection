from icrawler.builtin import BingImageCrawler
import os
import uuid
import time

class BingCrawler:

    def __init__(self):
        self.name = "bing"
        self.storage_dir = "temp/bing"

        os.makedirs(self.storage_dir, exist_ok=True)

    def paginate(self, query, limit):
        crawler = BingImageCrawler(
            storage={"root_dir": self.storage_dir}
        )

        crawler.crawl(
            keyword=query,
            max_num=limit,
            filters={"license": "commercial,modify"}  # IMPORTANT
        )

        # After download → yield local files
        for file in os.listdir(self.storage_dir):
            file_path = os.path.join(self.storage_dir, file)

            yield {
                "url": file_path,   # local path instead of URL
                "source": "bing",
                "id": str(uuid.uuid4()),
                "is_local": True    # VERY IMPORTANT FLAG
            }

     # 🔥 RATE LIMIT
            print("⏳ Bing rate limit sleep...")
            time.sleep(1)        