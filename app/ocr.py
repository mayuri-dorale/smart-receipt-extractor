import os
import platform
from io import BytesIO

import cv2
import numpy as np
import pytesseract
from PIL import Image, ImageOps

# On Windows, point directly at Tesseract so PATH problems don't matter.
if platform.system() == "Windows":
    default_path = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
    pytesseract.pytesseract.tesseract_cmd = os.getenv("TESSERACT_CMD", default_path)


def load_image(image_bytes: bytes) -> np.ndarray:
    """Decode uploaded bytes into an OpenCV BGR image, fixing phone rotation."""
    pil_img = Image.open(BytesIO(image_bytes))
    pil_img = ImageOps.exif_transpose(pil_img)  # fix sideways phone photos
    pil_img = pil_img.convert("RGB")
    return cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)


def preprocess(img: np.ndarray) -> np.ndarray:
    """Clean the image so Tesseract reads it better."""
    # Upscale small images; Tesseract likes text ~30px tall.
    h, w = img.shape[:2]
    if max(h, w) < 1500:
        scale = 1500 / max(h, w)
        img = cv2.resize(img, None, fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC)

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = cv2.fastNlMeansDenoising(gray, None, h=10)

    # Adaptive threshold copes with uneven lighting and shadows.
    thresh = cv2.adaptiveThreshold(
        gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 31, 15
    )
    return thresh


def extract_text(image_bytes: bytes) -> str:
    """Full pipeline: bytes -> preprocessed image -> raw OCR text."""
    img = load_image(image_bytes)
    processed = preprocess(img)
    # psm 6 = assume a single uniform block of text, good for receipts.
    config = "--oem 3 --psm 6"
    text = pytesseract.image_to_string(processed, config=config)
    return text.strip()