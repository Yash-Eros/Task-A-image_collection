import os
import sys
from pathlib import Path


# =========================================================
# ✅ FIX PATHS (VERY IMPORTANT)
# =========================================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(BASE_DIR, "../../"))

# Add .vendor/watermark-detection to Python path
VENDOR_PATH = os.path.join(PROJECT_ROOT, ".vendor", "watermark-detection")

if VENDOR_PATH not in sys.path:
    sys.path.insert(0, VENDOR_PATH)


# =========================================================
# MAIN CLASS
# =========================================================
class WatermarkValidator:
    def __init__(self):
        print("[Watermark] Using boomb0om trained model (ConvNeXt)")

        try:
            from validator import Validator

            self.validator = Validator(
                watermark_threshold=0.4,   # 🔥 LOWERED (better for faint logos like EROS)
                min_blur_variance=100.0,
                max_dimension=4096,
                blur_tolerance=10.0,
                watermark_model_name="convnext-tiny",
                watermark_model_cache_dir=os.path.join(PROJECT_ROOT, ".model_cache"),
                watermark_device="auto",
            )

            print("[Watermark] Model loaded successfully ✅")

        except Exception as e:
            print("[Watermark ERROR] Model load failed:", e)
            self.validator = None

    # =========================================================
    # MAIN FUNCTION
    # =========================================================
    def is_watermarked(self, image_path):
        try:
            if self.validator is None:
                return False, 0.0

            result = self.validator.validate(Path(image_path))

            score = float(result.watermark_score)

            # =================================================
            # 🔥 CUSTOM DECISION LOGIC (IMPORTANT)
            # =================================================
            # Instead of blindly trusting "reason",
            # we use score threshold (more stable across systems)

            is_marked = score >= 0.4

            # =================================================
            # 🔍 DEBUG (REMOVE LATER)
            # =================================================
            print(f"[DEBUG] {image_path} → score={score:.4f} | reason={result.reason}")

            return is_marked, round(score, 4)

        except Exception as e:
            print(f"[Watermark ERROR] {e}")
            return False, 0.0

    # =========================================================
    # OPTIONAL COMPATIBILITY
    # =========================================================
    def validate(self, image_path):
        score_full = self._predict(image)

        h, w = image.shape[:2]
        corner_crop = image[int(h*0.7):h, int(w*0.7):w]

        score_crop = self._predict(corner_crop)


        # take best score
        score = max(score_full, score_crop)


        if score > 0.6:
            if is_text_like_patch(image):
                return 0.3, "text_not_watermark"

        return score, "watermark_detected" if score > 0.6 else "clean"        

    

    def is_text_like_patch(img):
        """
        Detects if image is likely normal text (not watermark)
        based on density + edge structure
        """
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # Edge detection
        edges = cv2.Canny(gray, 50, 150)

        edge_density = edges.mean()

        # Text tends to have strong structured edges
        if edge_density > 20:
            return True

        return False    