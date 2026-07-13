"""Recommendations, custom simulate, and hub API tests."""

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


def _auth_headers(email: str = "rec@example.com") -> dict[str, str]:
    password = "Secret12"
    reg = client.post(
        "/auth/register",
        json={
            "name": "Rec Tester",
            "email": email,
            "password": password,
            "role": "farmer",
        },
    )
    if reg.status_code == 201:
        verify = client.post(
            "/auth/verify",
            json={"email": email, "code": "123456"},
        )
        assert verify.status_code == 200, verify.text
        token = verify.json()["access_token"]
    else:
        login = client.post(
            "/auth/login",
            json={"email": email, "password": password},
        )
        assert login.status_code == 200
        token = login.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def _farm_with_reading(headers: dict) -> int:
    farm = client.post(
        "/farms",
        headers=headers,
        json={
            "name": "Domates AI",
            "soil_type": "tinli",
            "crop_type": "domates",
            "growth_stage": "ciceklenme",
            "area": 2.0,
        },
    )
    assert farm.status_code == 201, farm.text
    farm_id = farm.json()["id"]
    reading = client.post(
        f"/sensor-readings/{farm_id}",
        headers=headers,
        json={
            "soil_moisture": 22,
            "air_temperature": 32,
            "rainfall_probability": 10,
            "last_irrigation_hours_ago": 36,
            "source_type": "manual",
        },
    )
    assert reading.status_code == 201, reading.text
    return farm_id


def test_recommendations_custom_hub_and_virtual_session():
    headers = _auth_headers()
    farm_id = _farm_with_reading(headers)

    pred = client.post(f"/predict/irrigation?farm_id={farm_id}", headers=headers)
    assert pred.status_code == 200, pred.text
    prediction_id = pred.json()["id"]

    rec = client.get(f"/recommendations/{farm_id}", headers=headers)
    assert rec.status_code == 200, rec.text
    body = rec.json()
    assert body["total"] >= 1
    assert any(i.get("prediction_id") == prediction_id for i in body["items"])

    detail = client.get(
        f"/recommendations/detail/{prediction_id}", headers=headers
    )
    assert detail.status_code == 200
    assert "factors" in detail.json()
    assert "data_sources" in detail.json()

    custom = client.post(
        "/simulate/custom",
        headers=headers,
        json={
            "farm_id": farm_id,
            "duration_minutes": 45,
            "target_moisture": 40,
            "name": "Test senaryo",
        },
    )
    assert custom.status_code == 200, custom.text
    assert len(custom.json()["forecast"]) == 6

    hub = client.get(f"/hub/{farm_id}", headers=headers)
    assert hub.status_code == 200
    assert hub.json()["farm_id"] == farm_id
    assert len(hub.json()["reports"]) >= 3
    keys = {r["key"] for r in hub.json()["reports"]}
    assert "water_savings" in keys
    assert "irrigation" in keys

    overview = client.get(f"/farms/{farm_id}/overview", headers=headers)
    assert overview.status_code == 200
    assert "water_savings_liters" in overview.json()

    status = client.get(f"/irrigation/status/{farm_id}", headers=headers)
    assert status.status_code == 200
    assert "pump_status" in status.json()
    assert "remaining_seconds" in status.json()

    denied = client.post(
        "/irrigation/start",
        headers=headers,
        json={"farm_id": farm_id, "user_approved": False},
    )
    assert denied.status_code == 400

    started = client.post(
        "/irrigation/start",
        headers=headers,
        json={
            "farm_id": farm_id,
            "user_approved": True,
            "duration_minutes": 20,
            "virtual_session": True,
        },
    )
    assert started.status_code == 201, started.text
    assert started.json()["event"]["status"] == "running"

    status = client.get(f"/irrigation/status/{farm_id}", headers=headers)
    assert status.status_code == 200
    assert status.json()["valve_status"] == "açık"

    stopped = client.post(
        "/irrigation/stop",
        headers=headers,
        json={"farm_id": farm_id},
    )
    assert stopped.status_code == 200
    assert stopped.json()["status"] in {"stopped", "completed"}
