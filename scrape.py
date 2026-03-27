import argparse
import asyncio
import os
import random
import shutil
import json
import hashlib
from PIL import Image
from io import BytesIO


from config import BUCKET_QUERIES
from src.scraper.manager import SourceManager
from src.utils.downloader import ImageDownloader
from src.utils.checkpoint import CheckpointManager
from src.utils.deduplicator import Deduplicator
from src.utils.logger import ProgressLogger

from src.validation.watermark import WatermarkValidator
from src.validation.resolution import ResolutionSorter
from src.validation.blur import is_blurry
from src.utils.metadata import create_metadata
from src.utils.logger_json import DownloadLogger
from src.utils.stats import StatsManager


# ================= FILTER =================
def is_relevant(meta):
    text = str(meta).lower()

    blacklist = [
        "horse", "animal", "wildlife",
        "camera", "dslr", "lens",
        "product", "gear"
    ]

    return not any(word in text for word in blacklist)


# ================= SAFE MOVE =================
def safe_move(src, dst_folder):
    os.makedirs(dst_folder, exist_ok=True)

    filename = os.path.basename(src)
    dst = os.path.join(dst_folder, filename)

    if os.path.exists(dst):
        base, ext = os.path.splitext(filename)
        dst = os.path.join(dst_folder, f"{base}_{random.randint(1000,9999)}{ext}")

    shutil.move(src, dst)


# ================= SCRAPER =================
class ImageScraper:

    def __init__(self, bucket, target):

        print(f"\n🚀 Starting scraping for {bucket}, target={target}")

        self.bucket = bucket
        self.target = target

        self.res_counts = {"256": 0, "512": 0, "1024": 0, "2048": 0}
        self.min_per_res = max(20, self.target // 10)

        self.base_dir = "data/indian_cultural_sorted"
        os.makedirs(self.base_dir, exist_ok=True)

        os.makedirs("data/rejected/watermarked", exist_ok=True)
        os.makedirs("data/rejected/blurry", exist_ok=True)

        self.watermark = WatermarkValidator()
        self.resolution = ResolutionSorter(self.base_dir)

        self.sources = SourceManager().get_sources()

        if bucket not in BUCKET_QUERIES:
            raise ValueError(f"❌ Bucket '{bucket}' not found")

        self.queries = BUCKET_QUERIES[bucket]

        self.checkpoint = CheckpointManager(bucket)
        self.state = self.checkpoint.load()

        self.seen_ids = set(self.state["seen_ids"])

        self.collected = self.get_existing_count()

        print(f"📂 Found {self.collected} existing images in {self.bucket}")

        self.dedup = Deduplicator()
        self.downloader = ImageDownloader("data/temp")
        self.logger = ProgressLogger(target)

        self.json_logger = DownloadLogger()
        self.stats = StatsManager()

        self.source_counts = {}
        self.priority_sources = ["pexels", "pixabay", "unsplash"]

        self.hash_file = "hashes.json"
        self.hashes = self.load_hashes()

    def get_existing_count(self):
        folder = os.path.join(self.base_dir, self.bucket)
        if not os.path.exists(folder):
            return 0

        return len([
            f for f in os.listdir(folder)
            if f.lower().endswith((".jpg", ".jpeg", ".png"))
        ])

    def load_hashes(self):
        if os.path.exists(self.hash_file):
            try:
                with open(self.hash_file, "r") as f:
                    return set(json.load(f))
            except:
                return set()
        return set()

    def save_hashes(self):
        with open(self.hash_file, "w") as f:
            json.dump(list(self.hashes), f)

    def compute_hash(self, path):
        try:
            img = Image.open(path).convert("L").resize((16, 16))
            pixels = list(img.getdata())
            avg = sum(pixels) / len(pixels)

            bits = ''.join(['1' if px > avg else '0' for px in pixels])
            return hex(int(bits, 2))
        except:
            return None

    def get_balanced_sources(self):
        def sort_key(source):
            name = source.name
            priority_score = 0 if name in self.priority_sources else 1
            usage = self.source_counts.get(name, 0)
            return (priority_score, usage)

        return sorted(self.sources, key=sort_key)

    def expand_queries(self):
        # Simplified query expansion to avoid encoding issues
        # Only add minimal modifiers to prevent API errors
        modifiers = ["indoor", "outdoor"]

        expanded = []
        for q in self.queries:
            # Sanitize query: strip whitespace and ensure clean encoding
            q = q.strip()
            if not q:
                continue
            
            expanded.append(q)
            
            # Add only selective modifiers to avoid overly long queries
            for m in modifiers:
                expanded.append(f"{q} {m}")

        random.shuffle(expanded)
        return expanded
    
    def sanitize_query(self, query):
        """Clean query string to prevent encoding issues"""
        # Remove extra spaces, control characters, and normalize
        query = ' '.join(query.split())  # Normalize whitespace
        query = query.strip()
        return query

    # ================= MAIN LOOP =================
    # ================= MAIN LOOP =================
    async def run(self):
        print(f"🚀 Starting scraping for {self.bucket}, target={self.target}")

        queries = self.expand_queries()

        source_failures = {}
        MAX_FAILURES = 5

        try:
            for source in self.sources:

                if self.collected >= self.target:
                    print("✅ Target reached!")
                    self.save_hashes()
                    return

                if source_failures.get(source.name, 0) >= MAX_FAILURES:
                    print(f"⛔ Skipping {source.name} (too many failures)")
                    continue

                print(f"\n📡 Using source: {source.name}")

                for query in queries:

                    if self.collected >= self.target:
                        print("✅ Target reached!")
                        self.save_hashes()
                        return

                    # Sanitize query before use
                    query = self.sanitize_query(query)
                    print(f"🔍 Query: {query}")

                    remaining = self.target - self.collected

                    try:
                        batch = []

                        # ✅ HANDLE ALL CASES (sync + async + coroutine)
                        paginator = source.paginate(query, remaining)

                        # ✅ CASE 1: coroutine (Playwright FIX)
                        if hasattr(paginator, "__await__"):
                            paginator = await paginator

                        # ✅ CASE 2: async generator
                        if hasattr(paginator, "__aiter__"):
                            async for img in paginator:

                                if self.collected >= self.target:
                                    break

                                if img["id"] in self.seen_ids:
                                    continue

                                self.seen_ids.add(img["id"])
                                batch.append(img)

                                if len(batch) >= 10:
                                    await self.process_batch(batch, source, 0)
                                    batch = []

                        # ✅ CASE 3: normal iterator
                        else:
                            for img in paginator:

                                if self.collected >= self.target:
                                    break

                                if img["id"] in self.seen_ids:
                                    continue

                                self.seen_ids.add(img["id"])
                                batch.append(img)

                                if len(batch) >= 10:
                                    await self.process_batch(batch, source, 0)
                                    batch = []

                        if batch:
                            await self.process_batch(batch, source, 0)

                        # ✅ reset failures on success
                        source_failures[source.name] = 0

                    except Exception as e:
                        print(f"⚠️ Error in {source.name}: {e}")

                        source_failures[source.name] = source_failures.get(source.name, 0) + 1

                        if source_failures[source.name] >= MAX_FAILURES:
                            print(f"❌ Disabling {source.name}")
                            self.sources = [s for s in self.sources if s.name != source.name]

                        continue

            print("✅ Finished all sources")
            self.save_hashes()

        except KeyboardInterrupt:
            print("\n🛑 Stopped manually. Saving progress...")
            self.save_hashes()
            return
    async def process_batch(self, images, source, source_idx):

        semaphore = asyncio.Semaphore(5)

        async def process_single(img):
            await asyncio.sleep(1)
            async with semaphore:
               
                try:
                    path = await self.downloader.download(img)

                    if not path or not os.path.exists(path):
                        return

                    meta = img

                    img_hash = self.compute_hash(path)

                    if img_hash and img_hash in self.hashes:
                        print("⚠️ Duplicate skipped (hash)")
                        os.remove(path)
                        return

                    if img_hash:
                        self.hashes.add(img_hash)

                    if self.dedup.is_duplicate(path):
                        print("⚠️ Duplicate")
                        os.remove(path)
                        return

                    if not is_relevant(meta):
                        print("❌ not relevant",meta)
                        os.remove(path)
                        return

                    is_marked, score = self.watermark.is_watermarked(path)
                    print(f"🔎 Watermark check: marked={is_marked}, score={score}")

                    if is_marked and score > 0.7:
                        print(f"❌ Rejected: watermarked (score={score})")
                        safe_move(path, "data/rejected/watermarked")
                        return

                    if is_blurry(path):
                        print("❌ Rejected: blurry")
                        safe_move(path, "data/rejected/blurry")
                        return

                    print(f"✓ Image passed all checks. Moving to bucket...")
                    final_path, res = self.resolution.move(path, self.bucket)

                    if final_path is None:
                        print(f"❌ Resolution check failed: image too small")
                        return

                    print("DEBUG IMG:", img)
                    # ✅ Ensure resolution bucket always exists
                    if res not in self.res_counts:
                        self.res_counts[res] = 0
                    self.res_counts[res] += 1

                    create_metadata(final_path, meta, self.bucket)

                    self.json_logger.log(meta, self.bucket, final_path)
                    self.stats.update(self.bucket, source.name, res)

                    self.source_counts[source.name] = self.source_counts.get(source.name, 0) + 1

                    if self.collected >= self.target:
                        return

                    self.collected += 1

                    self.logger.log(self.bucket, self.collected, source.name)
                    print(f"[{self.bucket}] {self.collected}/{self.target} ({(self.collected/self.target)*100:.1f}%)")

                    print("📊 Source usage:", self.source_counts)

                    self.checkpoint.save({
                        "collected": self.collected,
                        "seen_ids": list(self.seen_ids),
                        "last_source": source_idx
                    })

                except Exception as e:
                    print(f"⚠️ Processing error: {e}")

        await asyncio.gather(*[
            process_single(img)
            for img in images
        ])


# ================= CLI =================
def main():
    parser = argparse.ArgumentParser()

    parser.add_argument("--bucket", type=str)
    parser.add_argument("--count", type=int)

    parser.add_argument("--all", action="store_true")
    parser.add_argument("--count-per-bucket", type=int)

    args = parser.parse_args()

    if args.all:
        for bucket in BUCKET_QUERIES.keys():
            scraper = ImageScraper(bucket, args.count_per_bucket)
            asyncio.run(scraper.run())
    else:
        scraper = ImageScraper(args.bucket, args.count)
        asyncio.run(scraper.run())


if __name__ == "__main__":
    main()