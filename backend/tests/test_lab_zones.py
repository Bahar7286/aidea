"""Lab reports, zones, and IoT ingest API tests."""

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


def _auth_headers(email: str) -> dict[str, str]:
    password = "Secret12"
    reg = client.post(
        "/auth/register",
        json={
            "name": "Lab Tester",
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
            "name": "Domates Serasi",
            "soil_type": "tinli",
            "crop_type": "domates",
            "growth_stage": "ciceklenme",
        },
    )
    assert res.status_code == 201, res.text
    return res.json()["id"]


def test_zone_and_lab_report_flow():
    headers = _auth_headers("lab@example.com")
    farm_id = _create_farm(headers)

    zone = client.post(
        "/zones",
        headers=headers,
        json={"farm_id": farm_id, "name": "Bolge A"},
    )
    assert zone.status_code == 201, zone.text
    zone_id = zone.json()["id"]

    denied = client.post(
        "/lab-reports",
        headers=headers,
        json={
            "farm_id": farm_id,
            "zone_id": zone_id,
            "lab_name": "Toros Lab",
            "source_type": "lab_manual",
            "user_confirmed": False,
            "parameters": [{"parameter_code": "ph", "value": 7.1, "unit": "pH"}],
        },
    )
    # Draft with only pH → missing status (needs pH + another value for verify)
    assert denied.status_code == 201, denied.text
    assert denied.json()["status"] == "missing"
    assert denied.json()["user_confirmed"] is False

    ok = client.post(
        "/lab-reports",
        headers=headers,
        json={
            "farm_id": farm_id,
            "zone_id": zone_id,
            "lab_name": "Toros Lab",
            "source_type": "lab_manual",
            "user_confirmed": True,
            "parameters": [
                {"parameter_code": "ph", "value": 7.1, "unit": "pH"},
                {"parameter_code": "om", "value": 2.4, "unit": "%"},
                {"parameter_code": "p", "value": 18, "unit": "ppm"},
                {"parameter_code": "k", "value": 220, "unit": "ppm"},
            ],
        },
    )
    assert ok.status_code == 201, ok.text
    body = ok.json()
    assert body["user_confirmed"] is True
    assert len(body["parameters"]) == 4

    listed = client.get(f"/lab-reports/{farm_id}", headers=headers)
    assert listed.status_code == 200
    assert len(listed.json()) >= 1

    summary = client.get(f"/lab-reports/{farm_id}/summary", headers=headers)
    assert summary.status_code == 200
    assert summary.json()["total"] >= 2

    report_id = ok.json()["id"]
    detail = client.get(f"/lab-reports/detail/{report_id}", headers=headers)
    assert detail.status_code == 200
    assert "ai_summary" in detail.json()
    assert detail.json()["report"]["ph"] == 7.1

    demo = client.get("/lab-reports/extract-demo", headers=headers)
    assert demo.status_code == 200
    assert demo.json()["extraction_confidence"] > 50

    draft = client.post(
        "/lab-reports",
        headers=headers,
        json={
            "farm_id": farm_id,
            "lab_name": "Demo Lab",
            "source_type": "lab_report",
            "user_confirmed": False,
            "extraction_confidence": demo.json()["extraction_confidence"],
            "parameters": demo.json()["parameters"],
        },
    )
    assert draft.status_code == 201
    assert draft.json()["status"] == "pending"
    conf = client.post(
        f"/lab-reports/{draft.json()['id']}/confirm",
        headers=headers,
        json={"confirmed": True},
    )
    assert conf.status_code == 200
    assert conf.json()["status"] == "verified"
    assert conf.json()["user_confirmed"] is True


def test_iot_ingest_dual_moisture():
    headers = _auth_headers("ingest@example.com")
    farm_id = _create_farm(headers)

    res = client.post(
        "/iot/ingest",
        headers=headers,
        json={
            "device_id": "AT-FN-001",
            "farm_id": farm_id,
            "simulation": True,
            "measurements": {
                "soil_moisture_20cm": {"value": 31.4, "unit": "percent_vwc"},
                "soil_moisture_40cm": {"value": 38.1, "unit": "percent_vwc"},
                "soil_temperature": {"value": 24.6, "unit": "celsius"},
                "air_temperature": {"value": 32.2, "unit": "celsius"},
                "air_humidity": {"value": 41.0, "unit": "percent"},
            },
            "battery": 82,
            "status": "normal",
        },
    )
    assert res.status_code == 201, res.text
    data = res.json()
    assert data["source_type"] == "simulation"
    assert data["soil_moisture"] == 31.4
    assert data["soil_moisture_deep"] == 38.1
    assert data["is_validated"] is True
