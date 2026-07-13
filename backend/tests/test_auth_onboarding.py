"""Auth onboarding: register → verify → role → forgot/reset."""

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


def test_register_verify_role_flow():
    email = "onboard@example.com"
    reg = client.post(
        "/auth/register",
        json={
            "name": "Ali Veli",
            "email": email,
            "phone": "5551234567",
            "password": "Secret12",
        },
    )
    assert reg.status_code == 201, reg.text
    body = reg.json()
    assert body["demo_code"] == "123456"
    assert "access_token" not in body

    blocked = client.post(
        "/auth/login",
        json={"email": email, "password": "Secret12"},
    )
    assert blocked.status_code == 403

    verify = client.post(
        "/auth/verify",
        json={"email": email, "code": "123456"},
    )
    assert verify.status_code == 200, verify.text
    token = verify.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    role = client.patch(
        "/auth/me/role",
        headers=headers,
        json={"role": "agronomist"},
    )
    assert role.status_code == 200
    assert role.json()["role"] == "agronomist"
    assert role.json()["email_verified"] is True


def test_forgot_reset_password():
    email = "resetme@example.com"
    client.post(
        "/auth/register",
        json={
            "name": "Reset User",
            "email": email,
            "password": "Secret12",
        },
    )
    client.post("/auth/verify", json={"email": email, "code": "123456"})

    forgot = client.post("/auth/forgot-password", json={"email": email})
    assert forgot.status_code == 200
    assert forgot.json()["demo_code"] == "123456"

    reset = client.post(
        "/auth/reset-password",
        json={
            "email": email,
            "code": "123456",
            "new_password": "NewPass99",
        },
    )
    assert reset.status_code == 200, reset.text

    old = client.post(
        "/auth/login",
        json={"email": email, "password": "Secret12"},
    )
    assert old.status_code == 401

    ok = client.post(
        "/auth/login",
        json={"email": email, "password": "NewPass99"},
    )
    assert ok.status_code == 200


def test_update_me_profile_and_password():
    email = "profile@example.com"
    client.post(
        "/auth/register",
        json={
            "name": "Profil User",
            "email": email,
            "password": "Secret12",
            "role": "farmer",
        },
    )
    verify = client.post("/auth/verify", json={"email": email, "code": "123456"})
    assert verify.status_code == 200
    headers = {"Authorization": f"Bearer {verify.json()['access_token']}"}

    me = client.get("/auth/me", headers=headers)
    assert me.status_code == 200
    assert me.json()["email"] == email

    patched = client.patch(
        "/auth/me",
        headers=headers,
        json={"name": "Yeni Ad", "phone": "5321112233"},
    )
    assert patched.status_code == 200, patched.text
    assert patched.json()["name"] == "Yeni Ad"
    assert patched.json()["phone"] == "5321112233"

    weak = client.patch(
        "/auth/me",
        headers=headers,
        json={"current_password": "Secret12", "new_password": "weakpass1"},
    )
    assert weak.status_code == 400

    bad_current = client.patch(
        "/auth/me",
        headers=headers,
        json={"current_password": "Wrong12", "new_password": "Secret99"},
    )
    assert bad_current.status_code == 400

    changed = client.patch(
        "/auth/me",
        headers=headers,
        json={"current_password": "Secret12", "new_password": "Secret99"},
    )
    assert changed.status_code == 200, changed.text

    old = client.post("/auth/login", json={"email": email, "password": "Secret12"})
    assert old.status_code == 401
    new = client.post("/auth/login", json={"email": email, "password": "Secret99"})
    assert new.status_code == 200


def test_register_rejects_weak_password_and_admin_role_public():
    weak = client.post(
        "/auth/register",
        json={
            "name": "Weak User",
            "email": "weak@example.com",
            "password": "secret12",
        },
    )
    assert weak.status_code == 400

    pending = client.post(
        "/auth/register",
        json={
            "name": "Role User",
            "email": "noroleadmin@example.com",
            "password": "Secret12",
            "role": "admin",
        },
    )
    assert pending.status_code == 201
    verify = client.post(
        "/auth/verify",
        json={"email": "noroleadmin@example.com", "code": "123456"},
    )
    assert verify.status_code == 200
    assert verify.json()["user"]["role"] == "farmer"
