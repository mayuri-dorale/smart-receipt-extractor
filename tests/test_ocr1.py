import shutil
from io import BytesIO

import pytest
from PIL import Image, ImageDraw, ImageFont

from app.ocr import extract_text

WIN_PATH = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
has_tesseract = shutil.which("tesseract") or shutil.which(WIN_PATH)


@pytest.mark.skipif(not has_tesseract, reason="Tesseract not installed")
def test_ocr_reads_simple_text():
    img = Image.new("RGB", (800, 300), "white")
    draw = ImageDraw.Draw(img)
    try:
        font = ImageFont.load_default(size=48)
    except TypeError:
        font = ImageFont.load_default()
    draw.text((30, 40), "MILK 1.50", fill="black", font=font)
    draw.text((30, 140), "TOTAL 1.50", fill="black", font=font)

    buf = BytesIO()
    img.save(buf, format="PNG")

    text = extract_text(buf.getvalue()).upper()
    assert "MILK" in text
    assert "TOTAL" in text