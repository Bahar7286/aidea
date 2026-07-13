"""End-to-end vertical slice: register → farm → data → AI → scenarios → irrigation."""

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


def test_vertical_slice_happy_path():
    email = "happy-path@example.com"
    password = "Secret12"

    reg = client.post(
        "/auth/register",
        json={
            "name": "Happy Farmer",
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
            "name": "Demo Sera",
            "soil_type": "tinli",
            "crop_type": "domates",
            "growth_stage": "ciceklenme",
            "area": 2.0,
            "irrigation_type": "damla",
        },
    )
    assert farm.status_code == 201, farm.text
    farm_id = farm.json()["id"]

    datasets = client.get("/datasets", headers=headers)
    assert datasets.status_code == 200
    assert any(d["id"] == "drought_risk" for d in datasets.json())

    loaded = client.post(
        "/datasets/load",
        headers=headers,
        json={"farm_id": farm_id, "scenario": "drought_risk"},
    )
    assert loaded.status_code == 201, loaded.text
    assert loaded.json()["source_type"] == "test_dataset"

    sim = client.post(
        "/iot/simulate",
        headers=headers,
        json={"farm_id": farm_id, "scenario": "drought_risk"},
    )
    assert sim.status_code == 201, sim.text
    assert sim.json()["source_type"] == "simulation"

    pred = client.post(
        f"/predict/irrigation?farm_id={farm_id}",
        headers=headers,
    )
    assert pred.status_code == 200, pred.text
    assert "confidence_score" in pred.json()
    prediction_id = pred.json()["id"]

    scenarios = client.post(
        "/simulate/scenario",
        headers=headers,
        json={
            "farm_id": farm_id,
            "scenarios": ["irrigate_now", "wait_24h"],
        },
    )
    assert scenarios.status_code == 200, scenarios.text
    assert len(scenarios.json()["results"]) >= 2

    detail = client.get(
        f"/recommendations/detail/{prediction_id}",
        headers=headers,
    )
    assert detail.status_code == 200, detail.text

    hub = client.get(f"/hub/{farm_id}", headers=headers)
    assert hub.status_code == 200, hub.text
    assert hub.json()["farm_id"] == farm_id

    status = client.get(f"/irrigation/status/{farm_id}", headers=headers)
    assert status.status_code == 200, status.text

    confidence = pred.json()["confidence_score"]
    if confidence >= 60 and pred.json().get("irrigation_needed"):
        start = client.post(
            "/irrigation/start",
            headers=headers,
            json={
                "farm_id": farm_id,
                "user_approved": True,
                "virtual_session": True,
                "duration_minutes": 12,
            },
        )
        assert start.status_code == 201, start.text
        event_id = start.json()["event"]["id"]
        stop = client.post(
            "/irrigation/stop",
            headers=headers,
            json={"farm_id": farm_id, "event_id": event_id},
        )
        assert stop.status_code == 200, stop.text
    else:
        # Still verify approval gate rejects without user_approved.
        denied = client.post(
            "/irrigation/start",
            headers=headers,
            json={"farm_id": farm_id, "user_approved": False},
        )
        assert denied.status_code == 400

    # Soft-delete blocks mutations; restore works.
    deleted = client.delete(f"/farms/{farm_id}", headers=headers)
    assert deleted.status_code == 204
    blocked = client.post(
        f"/predict/irrigation?farm_id={farm_id}",
        headers=headers,
    )
    assert blocked.status_code == 403

    restored = client.put(
        f"/farms/{farm_id}",
        headers=headers,
        json={"is_active": True},
    )
    assert restored.status_code == 200
    assert restored.json()["is_active"] is True

    listed = client.get("/farms?include_inactive=true", headers=headers)
    assert listed.status_code == 200
    assert any(f["id"] == farm_id for f in listed.json())
