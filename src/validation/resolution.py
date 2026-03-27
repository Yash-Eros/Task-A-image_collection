import os
from PIL import Image


class ResolutionSorter:

    def __init__(self, base_dir):
        self.base_dir = base_dir

    def get_bucket(self, image_path):
        img = Image.open(image_path)
        w, h = img.size

        short = min(w, h)

        # ✅ STRICT RULES
        if 256 <= short < 512:
            return "256"
        elif 512 <= short <= 1024:
            return "512"
        elif 1024 <= short < 2048:
            return "1024"
        elif short >= 2048:
            return "2048"
        else:
            return None  # ❌ Reject if <256

    def move(self, image_path, bucket_name):
        res = self.get_bucket(image_path)

        # ❌ Reject very small images
        if res is None:
            reject_path = os.path.join(
                "data/rejected/too_small",
                os.path.basename(image_path)
            )
            os.makedirs(os.path.dirname(reject_path), exist_ok=True)
            os.rename(image_path, reject_path)
            return None, None

        dest = os.path.join(self.base_dir, bucket_name, res)
        os.makedirs(dest, exist_ok=True)

        filename = os.path.basename(image_path)
        final_path = os.path.join(dest, filename)

        os.rename(image_path, final_path)

        return final_path, res