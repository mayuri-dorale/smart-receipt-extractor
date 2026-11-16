import json
import os
import re

from dotenv import load_dotenv
from openai import OpenAI

from app.schemas import Receipt

load_dotenv()

client = OpenAI(
    api_key=os.getenv("LLM_API_KEY"),
    base_url=os.getenv("LLM_BASE_URL"),
)
MODEL = os.getenv("LLM_MODEL", "gemini-2.5-flash")

SYSTEM_PROMPT = """You extract structured data from noisy OCR text of receipts.
The text may contain OCR mistakes; fix obvious ones using context.
Return ONLY a JSON object with these keys:
merchant_name, merchant_address, date (YYYY-MM-DD), time, currency (e.g. INR, USD),
items (list of {name, quantity, unit_price, total_price}),
subtotal, tax, tip, total, payment_method.
Use null for anything not present. Numbers must be plain numbers (no currency symbols).
Do not invent data. No explanations, no markdown."""


def _parse_json(content: str) -> dict:
    """Parse JSON even if the model wraps it in markdown fences."""
    content = content.strip()
    content = re.sub(r"^```(?:json)?|```$", "", content, flags=re.MULTILINE).strip()
    return json.loads(content)


def extract_receipt(raw_text: str) -> Receipt:
    if not raw_text.strip():
        raise ValueError("No text found in the image.")

    response = client.chat.completions.create(
        model=MODEL,
        temperature=0,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"OCR text:\n\n{raw_text}"},
        ],
    )
    data = _parse_json(response.choices[0].message.content)
    return Receipt(**data)