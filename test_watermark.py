import os
from src.validation.watermark import WatermarkValidator

# =========================================================
# INIT
# =========================================================
wm = WatermarkValidator()

folder = "test_images"

if not os.path.exists(folder):
    print(f"[ERROR] Folder not found: {folder}")
    exit()

print(f"\n[INFO] Testing images in: {folder}\n")

total = 0
marked_count = 0
clean_count = 0

# =========================================================
# PROCESS IMAGES
# =========================================================
for filename in os.listdir(folder):
    if filename.lower().endswith((".jpg", ".jpeg", ".png")):
        img_path = os.path.join(folder, filename)

        try:
            is_marked, score = wm.is_watermarked(img_path)

            status = "WATERMARK ❌" if is_marked else "CLEAN ✅"

            print(f"{filename:20s} → {status} | score={score:.4f}")

            total += 1
            if is_marked:
                marked_count += 1
            else:
                clean_count += 1

        except Exception as e:
            print(f"{filename:20s} → ERROR: {e}")

# =========================================================
# SUMMARY
# =========================================================
print("\n================ SUMMARY ================")
print(f"Total images   : {total}")
print(f"Watermarked    : {marked_count}")
print(f"Clean images   : {clean_count}")
print("========================================\n")