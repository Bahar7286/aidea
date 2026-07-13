"""Focused CRUD coverage for newly completed update/delete paths."""

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


def _auth_headers(email: str, role: str = "farmer") -> dict[str, str]:
    password = "Secret12"
    reg = client.post(
        "/auth/register",
        json={
            "name": "CRUD Tester",
            "email": email,
            "password": password,
            "role": role,
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


def _create_farm(headers: dict, name: str = "CRUD Farm") -> int:
    res = client.post(
        "/farms",
        headers=headers,
        json={
            "name": name,
            "soil_type": "tinli",
            "crop_type": "domates",
            "growth_stage": "ciceklenme",
            "area": 1.5,
        },
    )
    assert res.status_code == 201, res.text
    return res.json()["id"]


def test_auth_me_update_and_farm_soft_delete():
    headers = _auth_headers("crud-auth@example.com")

    me = client.patch(
        "/auth/me",
        headers=headers,
        json={"name": "Guncel Ad", "phone": "05321234567"},
    )
    assert me.status_code == 200, me.text
    assert me.json()["name"] == "Guncel Ad"
    assert me.json()["phone"] == "05321234567"

    farm_id = _create_farm(headers)
    listed = client.get("/farms", headers=headers)
    assert listed.status_code == 200
    assert any(f["id"] == farm_id for f in listed.json())

    deleted = client.delete(f"/farms/{farm_id}", headers=headers)
    assert deleted.status_code == 204

    listed2 = client.get("/farms", headers=headers)
    assert all(f["id"] != farm_id for f in listed2.json())

    # Soft-deleted farm still readable by id for restore.
    got = client.get(f"/farms/{farm_id}", headers=headers)
    assert got.status_code == 200
    assert got.json()["is_active"] is False

    restored = client.put(
        f"/farms/{farm_id}",
        headers=headers,
        json={"is_active": True, "crop_type": ""},
    )
    assert restored.status_code == 200, restored.text
    assert restored.json()["is_active"] is True
    assert restored.json()["crops"] == []

    # Inactive farm mutations are blocked until restored.
    client.delete(f"/farms/{farm_id}", headers=headers)
    blocked = client.post(
        "/iot/simulate",
        headers=headers,
        json={"farm_id": farm_id, "scenario": "normal"},
    )
    assert blocked.status_code == 403
    inactive_listed = client.get("/farms?include_inactive=true", headers=headers)
    assert any(
        f["id"] == farm_id and f["is_active"] is False for f in inactive_listed.json()
    )


def test_zone_device_lab_delete_update():
    headers = _auth_headers("crud-entities@example.com")
    farm_id = _create_farm(headers, "Entity Farm")

    zone = client.post(
        "/zones",
        headers=headers,
        json={"farm_id": farm_id, "name": "Kuzey", "notes": "eski"},
    )
    assert zone.status_code == 201, zone.text
    zone_id = zone.json()["id"]

    updated = client.put(
        f"/zones/detail/{zone_id}",
        headers=headers,
        json={"name": "Kuzey-2", "notes": "yeni not"},
    )
    assert updated.status_code == 200, updated.text
    assert updated.json()["name"] == "Kuzey-2"

    device = client.post(
        "/devices",
        headers=headers,
        json={
            "farm_id": farm_id,
            "device_name": "Nem-1",
            "device_type": "soil_moisture",
            "zone_id": zone_id,
        },
    )
    assert device.status_code == 201, device.text
    device_id = device.json()["id"]

    lab = client.post(
        "/lab-reports",
        headers=headers,
        json={
            "farm_id": farm_id,
            "zone_id": zone_id,
            "lab_name": "Demo Lab",
            "source_type": "lab_manual",
            "user_confirmed": True,
            "parameters": [
                {"parameter_code": "ph", "value": 6.8, "unit": ""},
            ],
        },
    )
    # Empty unit rejected by schema (422) or router validation (400).
    assert lab.status_code in {400, 422}

    lab = client.post(
        "/lab-reports",
        headers=headers,
        json={
            "farm_id": farm_id,
            "zone_id": zone_id,
            "lab_name": "Demo Lab",
            "source_type": "lab_manual",
            "user_confirmed": True,
            "parameters": [
                {"parameter_code": "ph", "value": 6.8, "unit": "pH"},
                {"parameter_code": "ec", "value": 1.2, "unit": "dS/m"},
            ],
        },
    )
    assert lab.status_code == 201, lab.text
    report_id = lab.json()["id"]

    sim = client.post(
        "/iot/simulate",
        headers=headers,
        json={"farm_id": farm_id, "scenario": "normal", "device_id": device_id},
    )
    assert sim.status_code == 201, sim.text

    del_lab = client.delete(f"/lab-reports/detail/{report_id}", headers=headers)
    assert del_lab.status_code == 204
    assert (
        client.get(f"/lab-reports/detail/{report_id}", headers=headers).status_code
        == 404
    )

    del_dev = client.delete(f"/devices/detail/{device_id}", headers=headers)
    assert del_dev.status_code == 204
    assert client.get(f"/devices/detail/{device_id}", headers=headers).status_code == 404

    # Readings remain after device delete.
    readings = client.get(f"/sensor-readings/{farm_id}", headers=headers)
    assert readings.status_code == 200
    assert len(readings.json()) >= 1

    del_zone = client.delete(f"/zones/detail/{zone_id}", headers=headers)
    assert del_zone.status_code == 204
    assert client.get(f"/zones/detail/{zone_id}", headers=headers).status_code == 404


def test_admin_farm_device_ticket_patch_delete():
    # Promote admin first so bootstrap works even after other modules ran,
    # or reuse existing admin permission via DB if shared SQLite already has one.
    admin = _auth_headers("crud-admin@example.com")
    boot = client.post("/admin/bootstrap", headers=admin)
    if boot.status_code == 403:
        gen = app.dependency_overrides[get_db]()
        db = next(gen)
        try:
            from app.models import User

            u = db.query(User).filter(User.email == "crud-admin@example.com").first()
            assert u is not None
            u.role = "admin"
            db.commit()
        finally:
            db.close()
    else:
        assert boot.status_code == 200, boot.text

    farmer = _auth_headers("crud-farmer@example.com")
    farm_id = _create_farm(farmer, "Admin Target Farm")

    device = client.post(
        "/devices",
        headers=farmer,
        json={
            "farm_id": farm_id,
            "device_name": "AdminDev",
            "device_type": "soil_moisture",
        },
    )
    assert device.status_code == 201
    device_id = device.json()["id"]

    ticket = client.post(
        "/admin/tickets",
        headers=farmer,
        json={"subject": "Cihaz baglantisi", "priority": "high", "farm_id": farm_id},
    )
    assert ticket.status_code == 201, ticket.text
    ticket_id = ticket.json()["id"]

    farm_patch = client.patch(
        f"/admin/farms/{farm_id}",
        headers=admin,
        json={"is_active": False, "name": "Admin Renamed"},
    )
    assert farm_patch.status_code == 200, farm_patch.text
    assert farm_patch.json()["is_active"] is False
    assert farm_patch.json()["name"] == "Admin Renamed"

    device_patch = client.patch(
        f"/admin/devices/{device_id}",
        headers=admin,
        json={"connection_status": "offline", "battery_percent": 12},
    )
    assert device_patch.status_code == 200, device_patch.text
    assert device_patch.json()["connection_status"] == "offline"
    assert device_patch.json()["battery_percent"] == 12

    ticket_del = client.delete(f"/admin/tickets/{ticket_id}", headers=admin)
    assert ticket_del.status_code == 204
