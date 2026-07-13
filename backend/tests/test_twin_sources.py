"""Twin view and data sources API."""

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


def _auth(email: str) -> dict[str, str]:
    password = "Secret12"
    client.post(
        "/auth/register",
        json={"name": "Twin", "email": email, "password": password},
    )
    verify = client.post("/auth/verify", json={"email": email, "code": "123456"})
    return {"Authorization": f"Bearer {verify.json()['access_token']}"}


def test_twin_and_data_sources():
    headers = _auth("twin@example.com")
    farm = client.post(
        "/farms",
        headers=headers,
        json={"name": "Domates Serasi", "crop_type": "domates", "soil_type": "tinli"},
    )
    assert farm.status_code == 201
    farm_id = farm.json()["id"]

    client.post(
        "/zones",
        headers=headers,
        json={"farm_id": farm_id, "name": "Kuzey"},
    )
    client.post(
        f"/sensor-readings/{farm_id}",
        headers=headers,
        json={
            "soil_moisture": 28,
            "air_temperature": 30,
            "rainfall_probability": 10,
            "last_irrigation_hours_ago": 20,
            "source_type": "manual",
        },
    )

    twin = client.get(f"/farms/{farm_id}/twin", headers=headers)
    assert twin.status_code == 200, twin.text
    body = twin.json()
    assert len(body["zones"]) >= 1
    assert body["latest_reading"]["soil_moisture"] == 28
    assert body["source_label"] == "manual"

    sources = client.get(f"/farms/{farm_id}/data-sources", headers=headers)
    assert sources.status_code == 200
    keys = {s["key"] for s in sources.json()}
    assert "manual" in keys
    assert "lab" in keys
    manual = next(s for s in sources.json() if s["key"] == "manual")
    assert manual["record_count"] >= 1
    assert manual["status"] == "active"
