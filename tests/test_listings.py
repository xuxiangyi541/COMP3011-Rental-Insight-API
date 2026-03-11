from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"

def test_create_and_get_listing():
    payload = {
        "area_id": 1,
        "title": "Test listing",
        "rent_pcm": 999,
        "bedrooms": 1,
        "property_type": "studio",
        "furnished": False,
        "available_from": "2026-03-01"
    }
    r = client.post("/listings", json=payload)
    assert r.status_code == 201
    listing_id = r.json()["id"]

    r2 = client.get(f"/listings/{listing_id}")
    assert r2.status_code == 200
    assert r2.json()["title"] == "Test listing"