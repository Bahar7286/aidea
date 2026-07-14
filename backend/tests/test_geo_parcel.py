"""TKGM parcel normalize + /geo proxy (mocked upstream)."""

from pathlib import Path
import sys
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app
from app.tkgm_client import (
    TkgmNotFound,
    clear_tkgm_cache,
    normalize_parcel,
)

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


SAMPLE_PARCEL = {
    "type": "Feature",
    "geometry": {
        "type": "Polygon",
        "coordinates": [
            [
                [31.1000, 36.9160],
                [31.1010, 36.9160],
                [31.1010, 36.9170],
                [31.1000, 36.9170],
                [31.1000, 36.9160],
            ]
        ],
    },
    "properties": {
        "adaNo": "101",
        "parselNo": "12",
        "mahalleAd": "Belek",
        "alan": "2450.5",
    },
}


def _auth_headers(suffix: str):
    email = f"geo-parsel-{suffix}@example.com"
    password = "Secret12"
    reg = client.post(
        "/auth/register",
        json={"name": "Geo", "email": email, "password": password, "role": "farmer"},
    )
    assert reg.status_code == 201, reg.text
    code = reg.json().get("demo_code") or "123456"
    verify = client.post("/auth/verify", json={"email": email, "code": code})
    assert verify.status_code == 200, verify.text
    return {"Authorization": f"Bearer {verify.json()['access_token']}"}


def test_normalize_parcel_centroid_and_area_da():
    out = normalize_parcel(
        SAMPLE_PARCEL,
        mahalle_id=43484,
        ada="101",
        parsel="12",
    )
    assert out["ada"] == "101"
    assert out["parsel"] == "12"
    assert out["mahalle"] == "Belek"
    assert out["area_da"] == 2.4505
    assert abs(out["centroid"]["lat"] - 36.9165) < 0.001
    assert abs(out["centroid"]["lng"] - 31.1005) < 0.001
    assert out["geometry"]["type"] == "Polygon"
    assert len(out["geometry"]["coordinates"][0]) == 5


def test_geo_parcel_endpoint_mocked():
    clear_tkgm_cache()
    headers = _auth_headers("mock")
    with patch("app.routers.geo.fetch_parcel") as mocked:
        mocked.return_value = normalize_parcel(
            SAMPLE_PARCEL, mahalle_id=43484, ada="101", parsel="12"
        )
        res = client.get(
            "/geo/parcel",
            params={"mahalle_id": 43484, "ada": "101", "parsel": "12"},
            headers=headers,
        )
    assert res.status_code == 200, res.text
    body = res.json()
    assert body["area_da"] == 2.4505
    assert body["centroid"]["lat"]
    assert body["geometry"]["type"] == "Polygon"


def test_geo_parcel_not_found_turkish():
    clear_tkgm_cache()
    headers = _auth_headers("404")
    with patch("app.routers.geo.fetch_parcel", side_effect=TkgmNotFound("yok")):
        res = client.get(
            "/geo/parcel",
            params={"mahalle_id": 1, "ada": "1", "parsel": "1"},
            headers=headers,
        )
    assert res.status_code == 404
    assert "Parsel bulunamadı" in res.json()["detail"]


def test_farm_persists_parcel_fields():
    headers = _auth_headers("farm")
    geojson = '{"type":"Polygon","coordinates":[[[31.1,36.9],[31.2,36.9],[31.2,37.0],[31.1,37.0],[31.1,36.9]]]}'
    farm = client.post(
        "/farms",
        headers=headers,
        json={
            "name": "Parsel Arazi",
            "latitude": 36.9165,
            "longitude": 31.1005,
            "area": 2.45,
            "parcel_ada": "101",
            "parcel_parsel": "12",
            "parcel_mahalle_id": 43484,
            "geometry_geojson": geojson,
        },
    )
    assert farm.status_code == 201, farm.text
    data = farm.json()
    assert data["parcel_ada"] == "101"
    assert data["parcel_parsel"] == "12"
    assert data["parcel_mahalle_id"] == 43484
    assert data["geometry_geojson"] == geojson
