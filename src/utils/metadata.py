import os
from datetime import datetime


def create_metadata(image_path, meta,bucket=None):
    """
    Saves metadata .txt file alongside image.

    Args:
        image_path (str): Path to image file
        meta (dict): Metadata dictionary from scraper
    """

    try:
        txt_path = os.path.splitext(image_path)[0] + ".txt"

        # ✅ SAFE extraction with fallback
        title = meta.get("title", "N/A")
        source = meta.get("source", "unknown")
        url = meta.get("url", "N/A")
        author = meta.get("author", "unknown")

        # 🔥 FIX: dynamic license (NOT hardcoded)
        license_name = meta.get("license") or meta.get("licence") or "unknown"

        downloaded_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        with open(txt_path, "w", encoding="utf-8") as f:
            f.write(f"Title: {title}\n")
            f.write(f"Source: {source}\n")
            f.write(f"Author: {author}\n")
            f.write(f"URL: {url}\n")
            f.write(f"License: {license_name}\n")
            f.write(f"Downloaded: {downloaded_at}\n")

    except Exception as e:
        print(f"❌ Metadata write failed: {e}")