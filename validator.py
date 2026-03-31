from __future__ import annotations
# pyright: reportMissingImports=false

import importlib
import logging
import subprocess
import sys
import warnings
from pathlib import Path

import numpy as np
from PIL import Image



LOGGER = logging.getLogger(__name__)

from dataclasses import dataclass

@dataclass
class ValidationResult:
    is_valid: bool
    reason: str
    width: int
    height: int
    blur_variance: float
    watermark_score: float


class Validator:
    def __init__(
        self,
        watermark_threshold: float,
        min_blur_variance: float,
        max_dimension: int,
        blur_tolerance: float,
        watermark_model_name: str,
        watermark_model_cache_dir: str,
        watermark_device: str,
    ) -> None:
        # =========================================================
        # ✅ FORCE MENTOR REQUIREMENT
        # =========================================================
        self.watermark_threshold = 0.5# STRICT (mentor requirement)
        self.min_blur_variance = min_blur_variance
        self.max_dimension = max_dimension
        self.blur_tolerance = max(0.0, blur_tolerance)

        if watermark_model_name != "convnext-tiny":
            raise ValueError("Only convnext-tiny is supported.")

        # Suppress noisy deprecation warnings from third-party deps
        warnings.filterwarnings("ignore", category=FutureWarning, module=r"timm\.models\.")
        warnings.filterwarnings(
            "ignore",
            category=UserWarning,
            message=r"The `force_filename` argument is deprecated and ignored in `hf_hub_download`",
        )

        import torch

        try:
            wmdetection_models = importlib.import_module("wmdetection.models")
        except ModuleNotFoundError:
            wmdetection_models = self._clone_and_import_wmdetection()

        get_model = getattr(wmdetection_models, "get_watermarks_detection_model")

        if watermark_device == "auto":
            device = "cuda:0" if torch.cuda.is_available() else "cpu"
        else:
            device = watermark_device

        LOGGER.info(f"[Validator] Loading watermark model on {device}")

        model, transforms = get_model(
            watermark_model_name,
            device=device,
            fp16=False,
            pretrained=True,
            cache_dir=watermark_model_cache_dir,
        )

        self._torch = torch
        self._wm_model = model
        self._wm_transforms = transforms
        self._wm_device = device

    # =========================================================
    # MAIN VALIDATION
    # =========================================================
    def validate(self, image_path: Path) -> ValidationResult:
        try:
            with Image.open(image_path) as image:
                image = image.convert("RGB")
                width, height = image.size

                # ✅ FAST FILTER
                if width < 256 or height < 256:
                    return ValidationResult(False, "too_small", width, height, 0.0, 0.0)

                if width > self.max_dimension or height > self.max_dimension:
                    return ValidationResult(
                        False,
                        f"pixel_limit_exceeded:max_{self.max_dimension}",
                        width,
                        height,
                        0.0,
                        0.0,
                    )

                array = np.asarray(image, dtype=np.float32)
                blur_variance = self._blur_variance(array)

                # =========================================================
                # ✅ SAFE WATERMARK CALL
                # =========================================================
                try:
                    watermark_score = self._watermark_score(image)
                except Exception as wm_error:
                    LOGGER.warning(f"Watermark model failed: {wm_error}")
                    watermark_score = 0.0  # fallback (do NOT reject blindly)

                LOGGER.debug(
                    f"Validation: size=({width},{height}) "
                    f"blur={blur_variance:.2f} "
                    f"wm={watermark_score:.3f}"
                )

        except Exception as exc:
            return ValidationResult(
                False,
                f"unreadable_image:{exc}",
                0,
                0,
                0.0,
                0.0,
            )

        # =========================================================
        # ✅ STRICT WATERMARK RULE (FINAL)
        # =========================================================
        if watermark_score >= 0.5:
            return ValidationResult(
                False,
                "watermark_detected",
                width,
                height,
                blur_variance,
                watermark_score,
            )

        # =========================================================
        # BLUR CHECK
        # =========================================================
        relaxed_blur_min = self.min_blur_variance - self.blur_tolerance

        if blur_variance < self.min_blur_variance:
            if blur_variance >= relaxed_blur_min:
                return ValidationResult(
                    True,
                    "ok_blur_tolerated",
                    width,
                    height,
                    blur_variance,
                    watermark_score,
                )

            return ValidationResult(
                False,
                "blurry",
                width,
                height,
                blur_variance,
                watermark_score,
            )

        return ValidationResult(
            True,
            "ok",
            width,
            height,
            blur_variance,
            watermark_score,
        )

    # =========================================================
    # BLUR
    # =========================================================
    @staticmethod
    def _blur_variance(rgb: np.ndarray) -> float:
        gray = rgb[:, :, 0] * 0.299 + rgb[:, :, 1] * 0.587 + rgb[:, :, 2] * 0.114
        dx = np.diff(gray, axis=1)
        dy = np.diff(gray, axis=0)
        grad = np.concatenate([dx.ravel(), dy.ravel()])
        return float(np.var(grad))

    # =========================================================
    # WATERMARK
    # =========================================================
    def _watermark_score(self, image: Image.Image) -> float:
        with self._torch.no_grad():
            tensor = self._wm_transforms(image).float().unsqueeze(0).to(self._wm_device)
            logits = self._wm_model(tensor)
            probs = self._torch.softmax(logits, dim=1)
            return float(probs[0, 1].item())

    # =========================================================
    # CLONE MODEL
    # =========================================================
    @staticmethod
    def _clone_and_import_wmdetection():
        project_root = Path(__file__).resolve().parents[1]
        vendor_repo = project_root / ".vendor" / "watermark-detection"
        vendor_package = vendor_repo / "wmdetection"

        if not vendor_package.exists():
            vendor_repo.parent.mkdir(parents=True, exist_ok=True)
            subprocess.run(
                [
                    "git",
                    "clone",
                    "https://github.com/boomb0om/watermark-detection.git",
                    str(vendor_repo),
                ],
                check=True,
            )

        repo_path = str(vendor_repo)
        if repo_path not in sys.path:
            sys.path.insert(0, repo_path)

        return importlib.import_module("wmdetection.models")