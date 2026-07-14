"""Crop history CRUD + next-crop suggestion rules."""

from datetime import datetime, timedelta
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app

engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base.metadata.create_all(bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


def _auth_headers(email: str = "crop-hist@example.com") -> tuple[dict, int]:
    password = "Secret12"
    reg = client.post(
        "/auth/register",
        json={
            "name": "Crop Hist Farmer",
            "email": email,
            "password": password,
            "role": "farmer",
        },
    )
    assert reg.status_code == 201, reg.text
    code = reg.json().get("demo_code") or "123456"
    verify = client.post("/auth/verify", json={"email": email, "code": code})
    assert verify.status_code == 200, verify.text
    token = verify.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    farm = client.post(
        "/farms",
        headers=headers,
        json={
            "name": "Rotasyon Tarlası",
            "soil_type": "tinli",
            "crop_type": "domates",
            "area": 1.5,
            "irrigation_type": "damla",
        },
    )
    assert farm.status_code == 201, farm.text
    return headers, farm.json()["id"]


def test_crop_history_crud_and_suggestions():
    headers, farm_id = _auth_headers()

    # Empty list
    empty = client.get(f"/farms/{farm_id}/crop-history", headers=headers)
    assert empty.status_code == 200, empty.text
    assert empty.json()["items"] == []
    assert empty.json()["current_crop"] is None

    plant = (datetime.utcnow() - timedelta(days=120)).isoformat()
    harvest = (datetime.utcnow() - timedelta(days=40)).isoformat()

    created = client.post(
        f"/farms/{farm_id}/crop-history",
        headers=headers,
        json={
            "crop_type": "Domates",
            "planting_date": plant,
            "harvest_date": harvest,
            "status": "harvested",
            "yield_amount": 3500,
            "yield_unit": "kg/da",
            "notes": "test sezon",
        },
    )
    assert created.status_code == 201, created.text
    body = created.json()
    assert body["crop_type"] == "domates"
    assert body["source_type"] == "manual"
    assert body["status"] == "harvested"
    assert body["days_since_harvest"] is not None
    assert body["days_since_harvest"] >= 39
    hist_id = body["id"]

    listed = client.get(f"/farms/{farm_id}/crop-history", headers=headers)
    assert listed.status_code == 200
    data = listed.json()
    assert len(data["items"]) == 1
    assert data["last_harvested"]["id"] == hist_id
    assert data["days_since_harvest"] >= 39

    # Sensor reading for moisture context
    reading = client.post(
        f"/sensor-readings/{farm_id}",
        headers=headers,
        json={
            "soil_moisture": 36.0,
            "air_temperature": 28.0,
            "rainfall_probability": 10.0,
            "last_irrigation_hours_ago": 24.0,
            "source_type": "manual",
        },
    )
    assert reading.status_code == 201, reading.text

    sug = client.get(f"/farms/{farm_id}/crop-suggestions", headers=headers)
    assert sug.status_code == 200, sug.text
    sbody = sug.json()
    assert sbody["previous_crop"] == "domates"
    assert sbody["previous_family"] == "solanaceae"
    assert sbody["current_crop"] is None
    assert sbody["engine"] == "rule"
    assert len(sbody["suggestions"]) >= 1
    # Same family should be discouraged until long fallow; cereals/legumes preferred
    codes = {s["crop_type"]: s for s in sbody["suggestions"]}
    if "bugday" in codes:
        assert codes["bugday"]["score"] >= codes.get("domates", {"score": 0})["score"] or not codes[
            "domates"
        ]["suitable_now"]
    assert "gübre reçete" not in sbody["explanation"].lower()

    # Growing blocks new plantings advice
    growing = client.post(
        f"/farms/{farm_id}/crop-history",
        headers=headers,
        json={
            "crop_type": "marul",
            "planting_date": (datetime.utcnow() - timedelta(days=10)).isoformat(),
            "status": "growing",
        },
    )
    assert growing.status_code == 201, growing.text
    grow_id = growing.json()["id"]

    sug2 = client.get(f"/farms/{farm_id}/crop-suggestions", headers=headers)
    assert sug2.status_code == 200
    assert sug2.json()["current_crop"] == "marul"
    assert sug2.json()["fallow_ok"] is False
    assert all(not s["suitable_now"] for s in sug2.json()["suggestions"])

    # Update → harvest growing crop
    updated = client.put(
        f"/crop-history/{grow_id}",
        headers=headers,
        json={
            "status": "harvested",
            "harvest_date": datetime.utcnow().isoformat(),
        },
    )
    assert updated.status_code == 200, updated.text
    assert updated.json()["status"] == "harvested"

    deleted = client.delete(f"/crop-history/{hist_id}", headers=headers)
    assert deleted.status_code == 204

    final = client.get(f"/farms/{farm_id}/crop-history", headers=headers)
    assert final.status_code == 200
    assert all(i["id"] != hist_id for i in final.json()["items"])


def test_cannot_create_second_growing_season():
    headers, farm_id = _auth_headers("crop-grow2@example.com")
    plant = (datetime.utcnow() - timedelta(days=5)).isoformat()
    first = client.post(
        f"/farms/{farm_id}/crop-history",
        headers=headers,
        json={"crop_type": "biber", "planting_date": plant, "status": "growing"},
    )
    assert first.status_code == 201
    second = client.post(
        f"/farms/{farm_id}/crop-history",
        headers=headers,
        json={"crop_type": "domates", "planting_date": plant, "status": "growing"},
    )
    assert second.status_code == 400


def test_harvested_requires_date():
    headers, farm_id = _auth_headers("crop-req@example.com")
    bad = client.post(
        f"/farms/{farm_id}/crop-history",
        headers=headers,
        json={
            "crop_type": "arpa",
            "planting_date": (datetime.utcnow() - timedelta(days=90)).isoformat(),
            "status": "harvested",
        },
    )
    assert bad.status_code == 400
