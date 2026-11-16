import os

import openai
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from app.extractor import extract_receipt
from app.ocr import extract_text
from app.schemas import ExtractionResponse

MAX_UPLOAD_MB = 10
ALLOWED_TYPES = {"image/jpeg", "image/png", "image/webp"}

app = FastAPI(
    title="Smart Receipt Extractor",
    description="Snap a receipt, get clean, structured data.",
    version="1.0.0",
)

# Allow the frontend (Vercel) to call this API. Tighten this after deploying.
origins = os.getenv("ALLOWED_ORIGINS", "*").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {"status": "ok", "service": "smart-receipt-extractor"}


@app.get("/health")
def health():
    return {"status": "healthy"}


@app.post("/extract", response_model=ExtractionResponse)
def extract(file: UploadFile = File(...)):
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(400, "Upload a JPG, PNG, or WEBP image.")

    image_bytes = file.file.read()
    if len(image_bytes) > MAX_UPLOAD_MB * 1024 * 1024:
        raise HTTPException(413, f"Image too large (max {MAX_UPLOAD_MB} MB).")

    try:
        raw_text = extract_text(image_bytes)
    except Exception:
        raise HTTPException(422, "Could not read that image. Try a clearer photo.")

    if not raw_text:
        raise HTTPException(422, "No text found. Try a sharper, well-lit photo.")

    try:
        receipt = extract_receipt(raw_text)
    except openai.RateLimitError:
        raise HTTPException(429, "AI service is busy. Try again in a minute.")
    except (openai.APIError, ValueError):
        raise HTTPException(502, "Could not structure the receipt. Try again.")

    return ExtractionResponse(receipt=receipt, raw_text=raw_text)