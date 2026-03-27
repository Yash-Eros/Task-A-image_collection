import csv
import os


class StatsManager:

    def __init__(self):
        self.file = "collection_stats.csv"

        # { (bucket, source): {256: x, 512: x, 1024: x, 2048: x} }
        self.stats = {}

        if os.path.exists(self.file):
            self.load()

    def update(self, bucket, source, resolution):
        key = (bucket, source)

        if key not in self.stats:
            self.stats[key] = {
                "256": 0,
                "512": 0,
                "1024": 0,
                "2048": 0
            }

        # ✅ normalize resolution safely
        try:
            res = int(resolution)
        except:
            return

        if res <= 256:
            self.stats[key]["256"] += 1
        elif res <= 512:
            self.stats[key]["512"] += 1
        elif res <= 1024:
            self.stats[key]["1024"] += 1
        else:
            self.stats[key]["2048"] += 1

        # ✅ save after every update (safe)
        self.save()

    def save(self):
        try:
            with open(self.file, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)

                writer.writerow([
                    "bucket",
                    "source",
                    "count_256",
                    "count_512",
                    "count_1024",
                    "count_2048",
                    "total"
                ])

                for (bucket, source), res_counts in self.stats.items():
                    total = sum(res_counts.values())

                    writer.writerow([
                        bucket,
                        source,
                        res_counts["256"],
                        res_counts["512"],
                        res_counts["1024"],
                        res_counts["2048"],
                        total
                    ])

        except Exception as e:
            print(f"⚠️ Stats save error: {e}")

    def load(self):
        try:
            with open(self.file, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)

                for row in reader:
                    key = (row["bucket"], row["source"])

                    self.stats[key] = {
                        "256": int(row.get("count_256", 0)),
                        "512": int(row.get("count_512", 0)),
                        "1024": int(row.get("count_1024", 0)),
                        "2048": int(row.get("count_2048", 0))
                    }

        except Exception as e:
            print(f"⚠️ Stats load error (starting fresh): {e}")
            self.stats = {}