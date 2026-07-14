"""Soil-lab acceptance gate + sample report extraction tests."""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.lab_interpret import extract_from_file, score_soil_document
from app.main import app

SAMPLE = (
    ROOT / "ai" / "datasets" / "sample_soil_lab_report.txt"
).read_text(encoding="utf-8")

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
            "name": "Soil Gate Tester",
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
            "name": "Soil Gate Farm",
            "soil_type": "tinli",
            "crop_type": "domates",
            "growth_stage": "ciceklenme",
        },
    )
    assert res.status_code == 201, res.text
    return res.json()["id"]


def test_reject_non_soil_invoice_text():
    invoice = (
        "FATURA / INVOICE\n"
        "Sipariş No: 998877\n"
        "Ödeme bildirimi\n"
        "Kredi kartı tahsilatı: 1.250,00 TL\n"
        "Hava durumu: güneşli\n"
    )
    gate = score_soil_document(invoice)
    assert gate.accepted is False
    rows, avg, mode, msg, gate2 = extract_from_file(
        invoice.encode("utf-8"), "fatura.txt", use_ai=False
    )
    assert mode == "rejected"
    assert rows == []
    assert avg == 0.0
    assert gate2.accepted is False
    assert "toprak" in msg.lower() or "kabul" in msg.lower() or "görünmüyor" in msg.lower()


def test_accept_sample_soil_lab_report():
    gate = score_soil_document(SAMPLE)
    assert gate.accepted is True
    assert gate.score >= 40
    rows, avg, mode, msg, gate2 = extract_from_file(
        SAMPLE.encode("utf-8"),
        "sample_soil_lab_report.txt",
        use_ai=False,
    )
    assert gate2.accepted is True
    assert mode == "parsed"
    assert len(rows) >= 4
    codes = {r["parameter_code"] for r in rows}
    assert "ph" in codes
    assert "om" in codes
    assert avg > 0


def test_upload_rejects_invoice_accepts_sample():
    headers = _auth_headers("soil-gate@example.com")
    farm_id = _create_farm(headers)

    bad = client.post(
        "/lab-reports/upload",
        headers=headers,
        data={"farm_id": str(farm_id)},
        files={
            "file": (
                "fatura.txt",
                b"FATURA\nInvoice total 500 TL\nKredi karti odeme\n",
                "text/plain",
            )
        },
    )
    assert bad.status_code == 201, bad.text
    badj = bad.json()
    assert badj["accepted"] is False
    assert badj["extraction_mode"] == "rejected"
    assert badj["parameters"] == []
    assert badj["rejection_reason"]

    # Cannot create lab_report from rejected invoice file
    fake = client.post(
        "/lab-reports",
        headers=headers,
        json={
            "farm_id": farm_id,
            "lab_name": "Fake",
            "source_type": "lab_report",
            "file_name": badj["file_name"],
            "parameters": [
                {"parameter_code": "ph", "value": 7.0, "unit": "pH"},
                {"parameter_code": "om", "value": 2.0, "unit": "%"},
            ],
        },
    )
    assert fake.status_code == 400

    good = client.post(
        "/lab-reports/upload",
        headers=headers,
        data={"farm_id": str(farm_id)},
        files={
            "file": (
                "sample_soil_lab_report.txt",
                SAMPLE.encode("utf-8"),
                "text/plain",
            )
        },
    )
    assert good.status_code == 201, good.text
    gj = good.json()
    assert gj["accepted"] is True
    assert gj["extraction_mode"] in {"parsed", "ai"}
    assert len(gj["parameters"]) >= 2
    assert gj["rejection_reason"] is None

    draft = client.post(
        "/lab-reports",
        headers=headers,
        json={
            "farm_id": farm_id,
            "lab_name": "Antalya Toprak Lab",
            "source_type": "lab_report",
            "file_name": gj["file_name"],
            "extraction_confidence": gj["extraction_confidence"],
            "parameters": gj["parameters"],
            "user_confirmed": False,
        },
    )
    assert draft.status_code == 201, draft.text
    assert draft.json()["status"] == "pending"
    assert draft.json()["user_confirmed"] is False
