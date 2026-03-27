
import json
import os
from datetime import datetime


class DownloadLogger:

    def __init__(self, path="data/download_log.json"):
        self.path = path

        if not os.path.exists(self.path):
            with open(self.path, "w") as f:
                json.dump([], f)

    def log(self, meta, bucket, file_path):
        entry = {
            "id": meta.get("id"),
            "source": meta.get("source"),
            "url": meta.get("url"),
            "bucket": bucket,
            "file_path": file_path,
            "timestamp": datetime.now().isoformat()
        }

        with open(self.path, "r+") as f:
            data = json.load(f)
            data.append(entry)
            f.seek(0)
            json.dump(data, f, indent=2)