"""Resolve ai/datasets for local (repo root) and Render (backend root only)."""

from __future__ import annotations

import json
from pathlib import Path

# Bundled under backend/ for Render Root Directory=backend
_BACKEND_DATASETS = Path(__file__).resolve().parents[1] / "ai" / "datasets"
# Monorepo layout when working from full checkout
_REPO_DATASETS = Path(__file__).resolve().parents[2] / "ai" / "datasets"

# Fallback if JSON files are missing at deploy time
BUILTIN_SCENARIOS: dict[str, dict] = {
    "drought_risk": {
        "id": "drought_risk",
        "name": "Kuruma riski — Domates Serası demo",
        "description": "Nem düşük, sıcaklık yüksek, yağış yok",
        "reading": {
            "soil_moisture": 28,
            "soil_temperature": 25,
            "air_temperature": 33,
            "air_humidity": 42,
            "rainfall_probability": 5,
            "ph": 6.8,
            "ec": 1.1,
            "salinity": 0.7,
            "last_irrigation_hours_ago": 36,
        },
    },
    "normal": {
        "id": "normal",
        "name": "Normal nem",
        "description": "Hedef aralıkta nem",
        "reading": {
            "soil_moisture": 32,
            "soil_temperature": 24,
            "air_temperature": 28,
            "air_humidity": 50,
            "rainfall_probability": 15,
            "last_irrigation_hours_ago": 18,
        },
    },
    "over_irrigation": {
        "id": "over_irrigation",
        "name": "Aşırı sulama",
        "description": "Nem çok yüksek",
        "reading": {
            "soil_moisture": 72,
            "soil_temperature": 22,
            "air_temperature": 26,
            "air_humidity": 65,
            "rainfall_probability": 40,
            "last_irrigation_hours_ago": 4,
        },
    },
    "sensor_anomaly": {
        "id": "sensor_anomaly",
        "name": "Sensör anomalisi",
        "description": "Anormal değerler",
        "reading": {
            "soil_moisture": 5,
            "soil_temperature": 40,
            "air_temperature": 42,
            "air_humidity": 20,
            "rainfall_probability": 0,
            "last_irrigation_hours_ago": 72,
        },
    },
    "salinity_risk": {
        "id": "salinity_risk",
        "name": "Tuzluluk riski",
        "description": "Yüksek EC",
        "reading": {
            "soil_moisture": 35,
            "soil_temperature": 26,
            "air_temperature": 30,
            "air_humidity": 45,
            "rainfall_probability": 10,
            "ec": 3.2,
            "salinity": 2.1,
            "last_irrigation_hours_ago": 20,
        },
    },
    "post_irrigation_anomaly": {
        "id": "post_irrigation_anomaly",
        "name": "Sulama sonrası anomali",
        "description": "Sulama sonrası beklenmeyen nem",
        "reading": {
            "soil_moisture": 18,
            "soil_temperature": 27,
            "air_temperature": 31,
            "air_humidity": 48,
            "rainfall_probability": 5,
            "last_irrigation_hours_ago": 2,
        },
    },
}


def resolve_datasets_dir() -> Path | None:
    for path in (_BACKEND_DATASETS, _REPO_DATASETS):
        if path.is_dir() and any(path.glob("*.json")):
            return path
    return None


def list_scenario_metas() -> list[dict]:
    root = resolve_datasets_dir()
    items: list[dict] = []
    seen: set[str] = set()
    if root:
        for path in sorted(root.glob("*.json")):
            try:
                with path.open(encoding="utf-8") as f:
                    meta = json.load(f)
            except (OSError, json.JSONDecodeError):
                meta = {}
            sid = path.stem
            seen.add(sid)
            items.append(
                {
                    "id": sid,
                    "name": str(meta.get("name") or sid),
                    "description": meta.get("description"),
                }
            )
    for sid, meta in BUILTIN_SCENARIOS.items():
        if sid not in seen:
            items.append(
                {
                    "id": sid,
                    "name": str(meta.get("name") or sid),
                    "description": meta.get("description"),
                }
            )
    return sorted(items, key=lambda x: x["id"])


def load_scenario(scenario: str) -> dict:
    root = resolve_datasets_dir()
    if root:
        path = root / f"{scenario}.json"
        if path.exists():
            with path.open(encoding="utf-8") as f:
                return json.load(f)
    if scenario in BUILTIN_SCENARIOS:
        return BUILTIN_SCENARIOS[scenario]
    available = [m["id"] for m in list_scenario_metas()]
    raise FileNotFoundError(
        f"Senaryo bulunamadı: {scenario}. Mevcut: {', '.join(available)}"
    )
