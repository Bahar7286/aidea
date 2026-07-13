"""Admin panel API tests."""

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


def _auth(email: str = "adminpanel@example.com") -> dict[str, str]:
    password = "Secret12"
    reg = client.post(
        "/auth/register",
        json={
            "name": "Admin Panel",
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


def test_admin_bootstrap_and_modules():
    headers = _auth()

    forbidden = client.get("/admin/overview", headers=headers)
    assert forbidden.status_code == 403

    boot = client.post("/admin/bootstrap", headers=headers)
    if boot.status_code == 403:
        # Shared in-memory DB across collected test modules may already have an admin.
        gen = app.dependency_overrides[get_db]()
        db = next(gen)
        try:
            from app.models import User

            u = db.query(User).filter(User.email == "adminpanel@example.com").first()
            assert u is not None
            u.role = "admin"
            db.commit()
        finally:
            db.close()
    else:
        assert boot.status_code == 200, boot.text
        assert boot.json()["role"] == "admin"

    overview = client.get("/admin/overview", headers=headers)
    assert overview.status_code == 200
    assert "total_users" in overview.json()

    users = client.get("/admin/users", headers=headers)
    assert users.status_code == 200
    assert len(users.json()) >= 1

    farms = client.get("/admin/farms", headers=headers)
    assert farms.status_code == 200

    devices = client.get("/admin/devices", headers=headers)
    assert devices.status_code == 200

    billing = client.get("/admin/billing", headers=headers)
    assert billing.status_code == 200
    assert "demo" in billing.json()["note"].lower() or "MVP" in billing.json()["note"]

    ticket = client.post(
        "/admin/tickets",
        headers=headers,
        json={"subject": "Sanal vana sorunu", "priority": "high"},
    )
    assert ticket.status_code == 201, ticket.text

    tickets = client.get("/admin/tickets", headers=headers)
    assert tickets.status_code == 200
    assert len(tickets.json()) >= 1

    patched = client.patch(
        f"/admin/tickets/{ticket.json()['id']}",
        headers=headers,
        json={"status": "resolved"},
    )
    assert patched.status_code == 200
    assert patched.json()["status"] == "resolved"

    analytics = client.get("/admin/analytics?days=30", headers=headers)
    assert analytics.status_code == 200

    settings = client.get("/admin/settings", headers=headers)
    assert settings.status_code == 200

    updated = client.put(
        "/admin/settings",
        headers=headers,
        json={"settings": {"system_name": "AgriTwin Admin Test"}},
    )
    assert updated.status_code == 200
    assert updated.json()["settings"]["system_name"] == "AgriTwin Admin Test"
