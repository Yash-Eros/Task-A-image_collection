import json
import os

class CheckpointManager:

    def __init__(self, bucket):
        self.file = f"checkpoint/{bucket}.json"
        os.makedirs("checkpoint", exist_ok=True)

    def load(self):
        if os.path.exists(self.file):
            with open(self.file, "r") as f:
                return json.load(f)
        return {
            "collected": 0,
            "seen_ids": [],
            "last_source": 0
        }

    def save(self, state):
        with open(self.file, "w") as f:
            json.dump(state, f, indent=2)