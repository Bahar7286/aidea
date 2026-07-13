"""Agro material catalog + farm association API tests."""

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
            "name": "Agro Tester",
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


def test_catalog_list_and_farm_associate():
    headers = _auth_headers("agro-mat@example.com")

    catalog = client.get("/agro-materials", headers=headers)
    assert catalog.status_code == 200, catalog.text
    rows = catalog.json()
    assert len(rows) >= 10
    assert any(r["code"] == "fert_map" for r in rows)
    assert any(r["kind"] == "plant_protection" for r in rows)
    fert_only = client.get("/agro-materials?kind=fertilizer", headers=headers)
    assert fert_only.status_code == 200
    assert all(r["kind"] == "fertilizer" for r in fert_only.json())

    pick = [r["id"] for r in rows if r["code"] in {"fert_kno3", "pp_fungicide"}]
    assert len(pick) == 2

    farm = client.post(
        "/farms",
        headers=headers,
        json={
            "name": "Malzeme Profili Tarla",
            "soil_type": "tinli",
            "crop_type": "domates",
            "material_ids": pick,
        },
    )
    assert farm.status_code == 201, farm.text
    body = farm.json()
    farm_id = body["id"]
    assert len(body.get("material_uses") or []) == 2

    listed = client.get(f"/farms/{farm_id}/materials", headers=headers)
    assert listed.status_code == 200
    assert len(listed.json()) == 2

    synced = client.put(
        f"/farms/{farm_id}/materials",
        headers=headers,
        json={
            "items": [
                {
                    "material_id": pick[0],
                    "notes": "K fertigasyon",
                    "frequency": "weekly",
                }
            ]
        },
    )
    assert synced.status_code == 200, synced.text
    data = synced.json()
    assert len(data) == 1
    assert data[0]["notes"] == "K fertigasyon"
    assert data[0]["frequency"] == "weekly"
    assert data[0]["material"]["code"] == "fert_kno3"

    detail = client.get(f"/farms/{farm_id}", headers=headers)
    assert detail.status_code == 200
    assert len(detail.json()["material_uses"]) == 1


def test_create_farm_with_materials_payload():
    headers = _auth_headers("agro-mat2@example.com")
    catalog = client.get("/agro-materials", headers=headers)
    mid = catalog.json()[0]["id"]
    farm = client.post(
        "/farms",
        headers=headers,
        json={
            "name": "Rich Materials Farm",
            "materials": [{"material_id": mid, "frequency": "seasonal", "notes": "demo"}],
        },
    )
    assert farm.status_code == 201, farm.text
    uses = farm.json()["material_uses"]
    assert len(uses) == 1
    assert uses[0]["frequency"] == "seasonal"
