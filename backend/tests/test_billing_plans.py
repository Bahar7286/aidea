"""Billing plans (farmer-facing demo subscription)."""

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
            "name": "Plan Tester",
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


def test_billing_plans_list_and_select():
    headers = _auth_headers("billing-plan@example.com")
    listed = client.get("/billing/plans", headers=headers)
    assert listed.status_code == 200, listed.text
    body = listed.json()
    assert body["current_plan"] == "free"
    assert any(p["id"] == "pro" for p in body["plans"])
    assert any("AI" in f or "ai" in f.lower() for p in body["plans"] for f in p["features"])

    selected = client.put(
        "/billing/plan",
        headers=headers,
        json={"plan_id": "pro"},
    )
    assert selected.status_code == 200, selected.text
    assert selected.json()["subscription_plan"] == "pro"

    again = client.get("/billing/plans", headers=headers)
    assert again.json()["current_plan"] == "pro"
