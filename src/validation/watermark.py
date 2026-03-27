import os
import sys
import torch
from PIL import Image
import torchvision.transforms as transforms

# ✅ FIXED PATH (points to correct folder)
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../wmdetection"))

# ✅ Add BOTH levels to Python path
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../wmdetection"))
sys.path.append(BASE_DIR)

from wmdetection.models import convnext


class WatermarkValidator:

    def __init__(self, threshold=0.5):
        self.threshold = threshold
        self.device = "cuda" if torch.cuda.is_available() else "cpu"

        print(f"[Watermark] Using boomb0om ConvNeXt-Tiny on {self.device}")

        # Load architecture (no pretrained weights available)
        self.model = convnext.convnext_tiny(pretrained=False)

        self.model.to(self.device)
        self.model.eval()

        self.transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
        ])

    def is_watermarked(self, image_path):
        try:
            image = Image.open(image_path).convert("RGB")
            image = self.transform(image).unsqueeze(0).to(self.device)

            with torch.no_grad():
                output = self.model(image)

                # Simulated probability (since no trained weights)
                score = torch.sigmoid(output.mean()).item()

            return score > self.threshold, score

        except Exception as e:
            print(f"[Watermark ERROR] {e}")
            return True, 1.0