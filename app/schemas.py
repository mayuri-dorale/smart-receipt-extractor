from typing import List, Optional

from pydantic import BaseModel, Field


class LineItem(BaseModel):
    name: str
    quantity: float = 1
    unit_price: Optional[float] = None
    total_price: Optional[float] = None


class Receipt(BaseModel):
    merchant_name: Optional[str] = None
    merchant_address: Optional[str] = None
    date: Optional[str] = Field(None, description="YYYY-MM-DD if possible")
    time: Optional[str] = None
    currency: Optional[str] = None
    items: List[LineItem] = []
    subtotal: Optional[float] = None
    tax: Optional[float] = None
    tip: Optional[float] = None
    total: Optional[float] = None
    payment_method: Optional[str] = None


class ExtractionResponse(BaseModel):
    receipt: Receipt
    raw_text: str