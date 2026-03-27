import imagehash
from PIL import Image
import os

class Deduplicator:

    def __init__(self):
        self.hashes = set()

    def is_duplicate(self, image_path):
        try:
            img = Image.open(image_path)
            h = str(imagehash.phash(img))

            if h in self.hashes:
                return True

            self.hashes.add(h)
            return False

        except:
            return True