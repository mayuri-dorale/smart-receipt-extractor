# 🧾 Smart Receipt Extractor

Snap a receipt. Get clean, structured data.

**Live demo:** https://smart-receipt-extractor-frontend.vercel.app
*(The API sleeps when idle, so the first request can take about a minute.)*

## How it works
Receipt photo → OpenCV cleanup → Tesseract OCR → Gemini LLM → structured JSON

## Tech stack
Python, FastAPI, Tesseract, OpenCV, Pydantic, Docker, Render, Vercel

## Run locally
Requires Python 3.10+ and [Tesseract](https://github.com/UB-Mannheim/tesseract/wiki).

```bash
git clone https://github.com/mayuri-dorale/smart-receipt-extractor.git
cd smart-receipt-extractor
python -m venv venv
venv\Scripts\activate
python -m pip install -r requirements.txt
copy .env.example .env
python -m uvicorn app.main:app --reload
```

Add your own key to `.env` (a free Gemini key works: https://aistudio.google.com/apikey). Then open `frontend/index.html` with a local server: `cd frontend && python -m http.server 5500`.

## API
`POST /extract` with an image file returns the merchant, items, and total as JSON. Docs are at `/docs`.

