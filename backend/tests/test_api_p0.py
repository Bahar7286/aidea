"""API integration tests for new backend modules."""

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
from app.scenario_engine import simulate_scenarios
from app.ai_engine import RuleInput


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


def _auth_headers(email: str = "api@example.com") -> dict[str, str]:
    password = "Secret12"
    reg = client.post(
        "/auth/register",
        json={
            "name": "API Tester",
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
            "area": 2.0,
        },
    )
    assert res.status_code == 201, res.text
    return res.json()["id"]


def test_iot_simulate_and_device():
    headers = _auth_headers("iot@example.com")
    farm_id = _create_farm(headers)

    device = client.post(
        "/devices",
        headers=headers,
        json={
            "farm_id": farm_id,
            "device_name": "Nem Sensörü 01",
            "device_type": "soil_moisture",
        },
    )
    assert device.status_code == 201, device.text
    device_id = device.json()["id"]

    test = client.post(
        "/devices/test-connection",
        headers=headers,
        json={"device_id": device_id},
    )
    assert test.status_code == 200
    assert test.json()["connection_status"] == "active"

    sim = client.post(
        "/iot/simulate",
        headers=headers,
        json={"farm_id": farm_id, "scenario": "drought_risk", "device_id": device_id},
    )
    assert sim.status_code == 201, sim.text
    body = sim.json()
    assert body["source_type"] == "simulation"
    assert body["soil_moisture"] == 28


def test_scenario_compare_requires_two():
    headers = _auth_headers("scenario@example.com")
    farm_id = _create_farm(headers)
    client.post(
        f"/sensor-readings/{farm_id}",
        headers=headers,
        json={
            "soil_moisture": 28,
            "air_temperature": 33,
            "rainfall_probability": 5,
            "last_irrigation_hours_ago": 36,
        },
    )
    bad = client.post(
        "/simulate/scenario",
        headers=headers,
        json={"farm_id": farm_id, "scenarios": ["irrigate_now"]},
    )
    assert bad.status_code == 400

    ok = client.post(
        "/simulate/scenario",
        headers=headers,
        json={"farm_id": farm_id, "scenarios": ["irrigate_now", "wait_24h"]},
    )
    assert ok.status_code == 200, ok.text
    data = ok.json()
    assert len(data["results"]) == 2
    assert any(r["recommended"] for r in data["results"])


def test_irrigation_requires_approval_and_updates_moisture():
    headers = _auth_headers("irrig@example.com")
    farm_id = _create_farm(headers)
    client.post(
        f"/sensor-readings/{farm_id}",
        headers=headers,
        json={
            "soil_moisture": 28,
            "air_temperature": 33,
            "rainfall_probability": 5,
            "last_irrigation_hours_ago": 36,
        },
    )
    client.post(f"/predict/irrigation?farm_id={farm_id}", headers=headers)

    denied = client.post(
        "/irrigation/start",
        headers=headers,
        json={"farm_id": farm_id, "user_approved": False},
    )
    assert denied.status_code == 400

    started = client.post(
        "/irrigation/start",
        headers=headers,
        json={"farm_id": farm_id, "user_approved": True, "duration_minutes": 14},
    )
    assert started.status_code == 201, started.text
    body = started.json()
    assert body["updated_moisture"] > 28
    assert body["event"]["status"] == "completed"
    assert body["event"]["valve_status"] == "kapalı"

    history = client.get(f"/irrigation/history/{farm_id}", headers=headers)
    assert history.status_code == 200
    assert len(history.json()) >= 1


def test_scenario_engine_unit():
    recommended, outcomes = simulate_scenarios(
        RuleInput(
            soil_moisture=28,
            air_temperature=33,
            rainfall_probability=5,
            last_irrigation_hours_ago=36,
        ),
        ["irrigate_now", "wait_24h"],
    )
    assert len(outcomes) == 2
    assert recommended in {o.scenario for o in outcomes}
    wait = next(o for o in outcomes if o.scenario == "wait_24h")
    now = next(o for o in outcomes if o.scenario == "irrigate_now")
    assert wait.estimated_moisture < now.estimated_moisture
