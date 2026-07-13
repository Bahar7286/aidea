"""Farm coordinate resolution — defaults + soft Nominatim geocode."""

from __future__ import annotations

import logging
from typing import Any

import httpx

logger = logging.getLogger(__name__)

# Turkey geographic center (approx)
TURKEY_CENTER = (39.0, 35.0)

# Demo Domates Serası — Antalya / Serik
SERIK_COORDS = (36.9167, 31.1000)

LOCATION_DEFAULTS: dict[str, tuple[float, float]] = {
    "antalya": SERIK_COORDS,
    "serik": SERIK_COORDS,
    "konya": (37.8714, 32.4846),
    "karapınar": (37.7147, 33.5506),
    "karapinar": (37.7147, 33.5506),
    "ankara": (39.9334, 32.8597),
    "izmir": (38.4192, 27.1287),
}


def coords_for_farm(
    *,
    latitude: float | None,
    longitude: float | None,
    location: str | None,
    farm_name: str | None = None,
) -> tuple[float, float, str]:
    """Return (lat, lng, source) where source is stored|default|geocode|turkey."""
    if latitude is not None and longitude is not None:
        return float(latitude), float(longitude), "stored"

    name_l = (farm_name or "").lower()
    if "domates" in name_l:
        return (*SERIK_COORDS, "default_demo")

    loc = (location or "").strip().lower()
    for key, coords in LOCATION_DEFAULTS.items():
        if key in loc:
            return (*coords, "location_hint")

    geo = soft_geocode(location)
    if geo:
        return (*geo, "geocode")

    return (*TURKEY_CENTER, "turkey_center")


def soft_geocode(location: str | None) -> tuple[float, float] | None:
    if not location or len(location.strip()) < 3:
        return None
    try:
        with httpx.Client(timeout=4.0) as client:
            resp = client.get(
                "https://nominatim.openstreetmap.org/search",
                params={
                    "q": f"{location}, Turkey",
                    "format": "json",
                    "limit": 1,
                },
                headers={
                    "User-Agent": "AgriTwinAI/0.5 (demo; contact: demo@agritwin.local)",
                    "Accept-Language": "tr",
                },
            )
            if resp.status_code != 200:
                return None
            data: list[Any] = resp.json()
            if not data:
                return None
            return float(data[0]["lat"]), float(data[0]["lon"])
    except Exception as exc:  # noqa: BLE001 — soft fallback
        logger.debug("Nominatim geocode skipped: %s", exc)
        return None
