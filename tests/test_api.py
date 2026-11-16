from fastapi.testclient import TestClient

from app import main
from app.schemas import LineItem, Receipt

client = TestClient(main.app)

FAKE_RECEIPT = Receipt(
    merchant_name="Test Mart",
    items=[LineItem(name="Milk", quantity=1, total_price=1.5)],
    total=1.5,
)


def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "healthy"}


def test_rejects_non_image():
    r = client.post("/extract", files={"file": ("a.txt", b"hello", "text/plain")})
    assert r.status_code == 400


def test_extract_success(monkeypatch):
    monkeypatch.setattr(main, "extract_text", lambda b: "Test Mart\nMilk 1.50\nTotal 1.50")
    monkeypatch.setattr(main, "extract_receipt", lambda t: FAKE_RECEIPT)

    r = client.post("/extract", files={"file": ("r.jpg", b"fake", "image/jpeg")})
    assert r.status_code == 200
    body = r.json()
    assert body["receipt"]["merchant_name"] == "Test Mart"
    assert body["receipt"]["total"] == 1.5
    assert "Milk" in body["raw_text"]


def test_no_text_found(monkeypatch):
    monkeypatch.setattr(main, "extract_text", lambda b: "")
    r = client.post("/extract", files={"file": ("r.jpg", b"fake", "image/jpeg")})
    assert r.status_code == 422