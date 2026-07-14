"""Device management API tests (F18–F21)."""

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


def _auth_headers(email: str = "devices@example.com") -> dict[str, str]:
    password = "Secret12"
    reg = client.post(
        "/auth/register",
        json={
            "name": "Device Tester",
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
        assert login.status_code == 200, login.text
        token = login.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def _create_farm(headers: dict) -> int:
    res = client.post(
        "/farms",
        headers=headers,
        json={
            "name": "Domates Serasi Devices",
            "soil_type": "tinli",
            "crop_type": "domates",
            "growth_stage": "ciceklenme",
            "area": 2.0,
        },
    )
    assert res.status_code == 201, res.text
    return res.json()["id"]


def test_device_lifecycle_summary_calibrate():
    headers = _auth_headers()
    farm_id = _create_farm(headers)

    create = client.post(
        "/devices",
        headers=headers,
        json={
            "farm_id": farm_id,
            "device_name": "Toprak Nemi Sensörü",
            "device_type": "soil_moisture",
            "serial_number": "SN-1001",
            "region_name": "Kuzey",
            "depth_cm": 20,
            "connection_type": "lora",
            "sampling_minutes": 15,
            "capabilities": ["soil_moisture", "soil_temperature", "ec"],
        },
    )
    assert create.status_code == 201, create.text
    device = create.json()
    assert device["serial_number"] == "SN-1001"
    assert device["connection_type"] == "lora"
    assert device["calibration_due"] is True
    assert device["source_label"] == "simulation"
    assert "soil_moisture" in device["capabilities"]
    assert "ec" in device["capabilities"]
    device_id = device["id"]

    # Ölçüm al / simulate for device
    sim = client.post(
        "/iot/simulate",
        headers=headers,
        json={
            "farm_id": farm_id,
            "scenario": "drought_risk",
            "device_id": device_id,
        },
    )
    assert sim.status_code == 201, sim.text
    assert sim.json()["source_type"] == "simulation"
    assert sim.json()["device_id"] == device_id
    assert sim.json()["soil_moisture"] is not None

    detail_after = client.get(f"/devices/detail/{device_id}", headers=headers)
    assert detail_after.status_code == 200
    assert detail_after.json()["device"]["last_moisture"] is not None

    summary = client.get(f"/devices/{farm_id}/summary", headers=headers)
    assert summary.status_code == 200, summary.text
    s = summary.json()
    assert s["total"] == 1
    assert s["online"] == 1
    assert s["calibration_pending"] == 1

    listed = client.get(f"/devices/{farm_id}", headers=headers)
    assert listed.status_code == 200
    assert len(listed.json()) == 1

    sim = client.post(
        "/iot/simulate",
        headers=headers,
        json={"farm_id": farm_id, "scenario": "drought_risk", "device_id": device_id},
    )
    assert sim.status_code == 201, sim.text
    raw = sim.json()["soil_moisture"]

    detail = client.get(f"/devices/detail/{device_id}", headers=headers)
    assert detail.status_code == 200, detail.text
    body = detail.json()
    assert body["device"]["id"] == device_id
    assert len(body["recent_readings"]) >= 1
    assert body["device"]["last_moisture"] is not None

    cal = client.post(
        f"/devices/detail/{device_id}/calibrate",
        headers=headers,
        json={"reference_value": float(raw) + 0.3},
    )
    assert cal.status_code == 200, cal.text
    result = cal.json()
    assert result["status"] in {"good", "ok", "needs_attention"}
    assert abs(result["deviation"] - (-0.3)) < 0.01

    detail2 = client.get(f"/devices/detail/{device_id}", headers=headers)
    assert detail2.json()["device"]["calibration_due"] is False
    assert detail2.json()["device"]["last_calibration_at"] is not None

    test = client.post(
        "/devices/test-connection",
        headers=headers,
        json={"device_id": device_id},
    )
    assert test.status_code == 200
    assert test.json()["signal_dbm"] is not None
