"""Open-Meteo weather client — free, no API key."""

from __future__ import annotations

import logging
from datetime import datetime
from typing import Any

import httpx

from app.location_utils import coords_for_farm

logger = logging.getLogger(__name__)


def fetch_open_meteo(lat: float, lng: float) -> dict[str, Any]:
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lng,
        "current": "temperature_2m,relative_humidity_2m,precipitation",
        "hourly": "precipitation_probability",
        "forecast_days": 1,
        "timezone": "auto",
    }
    with httpx.Client(timeout=8.0) as client:
        resp = client.get(url, params=params)
        resp.raise_for_status()
        payload = resp.json()

    current = payload.get("current") or {}
    hourly = payload.get("hourly") or {}
    probs = hourly.get("precipitation_probability") or []
    precip_prob = float(probs[0]) if probs else None

    return {
        "provider": "open-meteo",
        "latitude": lat,
        "longitude": lng,
        "temperature_c": current.get("temperature_2m"),
        "humidity_pct": current.get("relative_humidity_2m"),
        "precipitation_mm": current.get("precipitation"),
        "precip_probability_pct": precip_prob,
        "fetched_at": datetime.utcnow().isoformat() + "Z",
        "raw_time": current.get("time"),
    }


def weather_for_farm(farm: Any) -> dict[str, Any]:
    lat, lng, source = coords_for_farm(
        latitude=getattr(farm, "latitude", None),
        longitude=getattr(farm, "longitude", None),
        location=getattr(farm, "location", None),
        farm_name=getattr(farm, "name", None),
    )
    try:
        data = fetch_open_meteo(lat, lng)
        data["coord_source"] = source
        data["location"] = getattr(farm, "location", None)
        return data
    except Exception as exc:  # noqa: BLE001
        logger.warning("Open-Meteo failed: %s", exc)
        return {
            "provider": "open-meteo",
            "latitude": lat,
            "longitude": lng,
            "coord_source": source,
            "location": getattr(farm, "location", None),
            "temperature_c": None,
            "humidity_pct": None,
            "precipitation_mm": None,
            "precip_probability_pct": None,
            "error": "Hava durumu alınamadı",
            "fetched_at": datetime.utcnow().isoformat() + "Z",
        }
