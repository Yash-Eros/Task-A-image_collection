"""
Full Eros pipeline:
Download → Extract Frames → Remove Watermark

Usage:
python eros_pipeline.py --url "<YOUTUBE_URL>" --interval 3 --method opencv
python eros_pipeline.py --video "movies/raw_video/movie.mp4" --interval 3 --method lama
"""

import argparse
import os
import subprocess
import cv2
import numpy as np
import glob
import re
from simple_lama_inpainting import SimpleLama
from PIL import Image, ImageDraw


# ✅ YOUR WATERMARK REGION
WM_REGION = (44, 109, 89, 27)  # (x, y, w, h)


# -------------------------
# Step 1: Download video
# -------------------------
def download_video(url, output_dir="data/eros_frames/raw_video"):

    os.makedirs(output_dir, exist_ok=True)

    before = set(glob.glob(f"{output_dir}/*"))

    cmd = [
        "python", "-m", "yt_dlp",
        url,
        "--format", "bestvideo[height<=720]",
        "--output", f"{output_dir}/%(title)s.%(ext)s"
    ]

    print("⬇Downloading video...")
    subprocess.run(cmd, check=True)

    after = set(glob.glob(f"{output_dir}/*"))

    new_files = list(after - before)

    if not new_files:
        raise Exception("Could not detect downloaded video")

    video_path = new_files[0]

    print(f"Downloaded: {video_path}")

    return video_path


# -------------------------
# Step 2: Extract frames
# -------------------------
def extract_frames(video_path, output_dir, every_n_seconds=3):
    os.makedirs(output_dir, exist_ok=True)

    cap = cv2.VideoCapture(video_path)

    if not cap.isOpened():
        raise Exception(f" Error: Cannot open video {video_path}")

    fps = cap.get(cv2.CAP_PROP_FPS)
    interval = int(fps * every_n_seconds)

    count = 0
    saved = 0

    print(f"FPS: {fps}")
    print(f"Extracting every {every_n_seconds} sec")

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        if count % interval == 0:
            path = f"{output_dir}/frame_{saved:06d}.jpg"
            cv2.imwrite(path, frame)
            saved += 1

        count += 1

    cap.release()

    print(f"Extracted {saved} frames")
    return saved


# -------------------------
# Step 3: Remove watermark (OpenCV)
# -------------------------
def remove_opencv(frames_dir, out_dir):

    os.makedirs(out_dir, exist_ok=True)

    x, y, w, h = WM_REGION

    paths = sorted(glob.glob(f"{frames_dir}/*.jpg"))

    print(f"Removing watermark using OpenCV from {len(paths)} frames...")

    for i, path in enumerate(paths):
        img = cv2.imread(path)

        if img is None:
            continue

        mh, mw = img.shape[:2]

        # ✅ Step 1: Create mask
        mask = np.zeros((mh, mw), dtype=np.uint8)
        mask[y:y+h, x:x+w] = 255

        # ✅ Step 2: Expand mask slightly (VERY IMPORTANT)
        kernel = np.ones((5, 5), np.uint8)
        mask = cv2.dilate(mask, kernel, iterations=2)

        # ✅ Step 3: Smooth edges
        mask = cv2.GaussianBlur(mask, (11, 11), 0)

        # ✅ Step 4: Stronger inpainting
        result = cv2.inpaint(img, mask, 5, cv2.INPAINT_TELEA)

        out_path = f"{out_dir}/{os.path.basename(path)}"
        cv2.imwrite(out_path, result)

        if i % 100 == 0:
            print(f"Processed {i}/{len(paths)}")

    print("OpenCV watermark removal completed")


def remove_lama(frames_dir, out_dir):

    os.makedirs(out_dir, exist_ok=True)

    # ✅ use YOUR watermark region
    x, y, w, h = WM_REGION

    print("Loading LaMa model...")
    lama = SimpleLama()

    paths = sorted(glob.glob(f"{frames_dir}/*.jpg"))

    print(f"Removing watermark using LaMa on {len(paths)} frames...")

    for i, path in enumerate(paths):
        img = Image.open(path).convert("RGB")

        # ✅ Create mask
        mask = Image.new("L", (img.width, img.height), 0)
        draw = ImageDraw.Draw(mask)

        # 🔥 Expand ONLY for LaMa
        pad = 15  # try 15–20 if needed

        x1 = max(0, x - pad)
        y1 = max(0, y - pad)
        x2 = min(img.width, x + w + pad)
        y2 = min(img.height, y + h + pad)
        draw.rectangle([x1, y1, x2, y2], fill=255)

        mask_np = np.array(mask)
        mask_np = cv2.GaussianBlur(mask_np, (21, 21), 0)

        mask = Image.fromarray(mask_np)

        # ✅ Inpaint
        result = lama(img, mask)

        out_path = os.path.join(out_dir, os.path.basename(path))
        result.save(out_path, quality=95)

        if i % 20 == 0:
            print(f"LaMa processed {i}/{len(paths)}")

    print("LaMa watermark removal completed")


# -------------------------
# MAIN PIPELINE
# -------------------------
if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument("--url", type=str, help="YouTube URL")
    parser.add_argument("--video", type=str, help="Local video path")
    parser.add_argument("--interval", type=int, default=3)
    parser.add_argument("--method", choices=["opencv", "lama"], default="opencv")

    args = parser.parse_args()

    # Step 1: Get video
    if args.url:
        video = download_video(args.url)
    elif args.video:
        video = args.video
    else:
        raise Exception("Provide either --url or --video")

    # Step 2: Setup paths
    name = os.path.splitext(os.path.basename(video))[0]
    name = re.sub(r'[^a-zA-Z0-9]+', '_', name.lower())

    frames_dir = f"data/eros_frames/raw_frames/{name}"
    clean_dir = f"data/eros_frames/clean/{name}"

    print(f"Frames will be saved to: {frames_dir}")
    print(f"Clean frames will be saved to: {clean_dir}")

    # Step 3: Extract frames
    extract_frames(video, frames_dir, args.interval)

    # Step 4: Remove watermark
    if args.method == "lama":
        remove_lama(frames_dir, clean_dir)
    else:
        remove_opencv(frames_dir, clean_dir)

    print(f"\n DONE → Clean frames saved at: {clean_dir}")