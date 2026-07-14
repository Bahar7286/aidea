"""Unofficial TKGM MEGSIS HTTP client + parcel normalization.

No API key. Continuity/accuracy not guaranteed — see TKGM_PARSEL.md.
"""

from __future__ import annotations

import json
import time
from typing import Any

import httpx
from fastapi import HTTPException

IL_LISTE_PRIMARY = (
    "https://parselsorgu.tkgm.gov.tr/app/modules/"
    "administrativeQuery/data/ilListe.json"
)
IL_LISTE_FALLBACK = (
    "https://cbsapi.tkgm.gov.tr/megsiswebapi.v3.1/api/idariYapi/ilListe"
)
CBS_BASE = "https://cbsapi.tkgm.gov.tr/megsiswebapi.v3.1/api"

USER_AGENT = (
    "Mozilla/5.0 (compatible; AgriTwin/1.0; +https://github.com/Bahar7286/aidea) "
    "AppleWebKit/537.36"
)
HEADERS = {
    "User-Agent": USER_AGENT,
    "Accept": "application/json",
    "Referer": "https://parselsorgu.tkgm.gov.tr/",
}

TIMEOUT = 14.0
# Short in-memory cache for administrative lists only.
_CACHE_TTL_SEC = 3600.0
_cache: dict[str, tuple[float, Any]] = {}


class TkgmUnavailable(Exception):
    """Upstream timeout / network / 5xx."""


class TkgmNotFound(Exception):
    """Parcel or admin unit not found."""


def _cache_get(key: str) -> Any | None:
    row = _cache.get(key)
    if not row:
        return None
    expires, value = row
    if time.monotonic() > expires:
        _cache.pop(key, None)
        return None
    return value


def _cache_set(key: str, value: Any) -> None:
    _cache[key] = (time.monotonic() + _CACHE_TTL_SEC, value)


def clear_tkgm_cache() -> None:
    _cache.clear()


def _get_json(url: str) -> Any:
    try:
        with httpx.Client(timeout=TIMEOUT, headers=HEADERS, follow_redirects=True) as client:
            res = client.get(url)
    except (httpx.TimeoutException, httpx.TransportError) as exc:
        raise TkgmUnavailable(str(exc)) from exc

    if res.status_code == 404:
        raise TkgmNotFound(res.text[:400] if res.text else "not found")
    if res.status_code >= 500:
        raise TkgmUnavailable(f"HTTP {res.status_code}")
    if res.status_code >= 400:
        # TKGM often returns 404-style messages with other codes.
        body = (res.text or "").lower()
        if "bulunamad" in body or "not found" in body:
            raise TkgmNotFound(res.text[:400])
        raise TkgmUnavailable(f"HTTP {res.status_code}: {res.text[:200]}")

    try:
        return res.json()
    except json.JSONDecodeError as exc:
        raise TkgmUnavailable("Geçersiz JSON yanıtı") from exc


def _features_to_options(payload: Any) -> list[dict[str, Any]]:
    features = []
    if isinstance(payload, dict):
        features = payload.get("features") or []
    elif isinstance(payload, list):
        features = payload
    out: list[dict[str, Any]] = []
    for feat in features:
        if not isinstance(feat, dict):
            continue
        props = feat.get("properties") or {}
        if not isinstance(props, dict):
            continue
        raw_id = props.get("id")
        text = props.get("text") or props.get("adi") or props.get("name")
        if raw_id is None or text is None:
            continue
        out.append({"id": int(raw_id) if str(raw_id).isdigit() else raw_id, "name": str(text)})
    out.sort(key=lambda x: str(x["name"]))
    return out


def fetch_provinces() -> list[dict[str, Any]]:
    cached = _cache_get("provinces")
    if cached is not None:
        return cached
    try:
        data = _get_json(IL_LISTE_PRIMARY)
    except TkgmUnavailable:
        data = _get_json(IL_LISTE_FALLBACK)
    options = _features_to_options(data)
    if not options:
        raise TkgmUnavailable("İl listesi boş")
    _cache_set("provinces", options)
    return options


def fetch_districts(il_id: int | str) -> list[dict[str, Any]]:
    key = f"districts:{il_id}"
    cached = _cache_get(key)
    if cached is not None:
        return cached
    data = _get_json(f"{CBS_BASE}/idariYapi/ilceListe/{il_id}")
    options = _features_to_options(data)
    _cache_set(key, options)
    return options


def fetch_neighborhoods(ilce_id: int | str) -> list[dict[str, Any]]:
    key = f"neighborhoods:{ilce_id}"
    cached = _cache_get(key)
    if cached is not None:
        return cached
    data = _get_json(f"{CBS_BASE}/idariYapi/mahalleListe/{ilce_id}")
    options = _features_to_options(data)
    _cache_set(key, options)
    return options


def _ring_centroid(ring: list) -> tuple[float, float] | None:
    """Centroid of a GeoJSON ring [[lng, lat], ...] (ignores hole closing dupes)."""
    if not ring or len(ring) < 3:
        return None
    pts = ring[:-1] if ring[0] == ring[-1] and len(ring) > 3 else ring
    lats: list[float] = []
    lngs: list[float] = []
    for pt in pts:
        if not isinstance(pt, (list, tuple)) or len(pt) < 2:
            continue
        lngs.append(float(pt[0]))
        lats.append(float(pt[1]))
    if not lats:
        return None
    return sum(lats) / len(lats), sum(lngs) / len(lngs)


def geometry_centroid(geometry: dict[str, Any] | None) -> dict[str, float] | None:
    if not geometry or not isinstance(geometry, dict):
        return None
    gtype = geometry.get("type")
    coords = geometry.get("coordinates")
    if not coords:
        return None
    ring = None
    if gtype == "Polygon":
        ring = coords[0] if coords else None
    elif gtype == "MultiPolygon":
        ring = coords[0][0] if coords and coords[0] else None
    elif gtype == "Point":
        return {"lat": float(coords[1]), "lng": float(coords[0])}
    else:
        return None
    c = _ring_centroid(ring or [])
    if not c:
        return None
    return {"lat": c[0], "lng": c[1]}


def _parse_area_m2(props: dict[str, Any]) -> float | None:
    for key in (
        "alan",
        "Alan",
        "area",
        "AREA",
        "yuzolcum",
        "yuzolcumu",
        "m2",
        "alanM2",
        "alan_m2",
    ):
        if key not in props or props[key] is None:
            continue
        raw = props[key]
        if isinstance(raw, (int, float)):
            return float(raw)
        s = str(raw).strip().replace(" ", "").replace(",", ".")
        # strip unit suffixes
        for suffix in ("m2", "m²", "ha", "da"):
            if s.lower().endswith(suffix):
                s = s[: -len(suffix)]
        try:
            return float(s)
        except ValueError:
            continue
    return None


def normalize_parcel(
    raw: Any,
    *,
    mahalle_id: int | str,
    ada: str,
    parsel: str,
    mahalle_name: str | None = None,
) -> dict[str, Any]:
    """Normalize TKGM parcel JSON into AgriTwin shape."""
    if not isinstance(raw, dict):
        raise ValueError("Beklenmeyen parsel yanıtı")

    geometry = raw.get("geometry")
    props: dict[str, Any] = {}
    if isinstance(raw.get("properties"), dict):
        props = raw["properties"]
    elif raw.get("type") == "Feature" and isinstance(raw.get("properties"), dict):
        props = raw["properties"]

    # Some responses nest Feature under features[0]
    if geometry is None and isinstance(raw.get("features"), list) and raw["features"]:
        feat = raw["features"][0]
        if isinstance(feat, dict):
            geometry = feat.get("geometry")
            if isinstance(feat.get("properties"), dict):
                props = {**props, **feat["properties"]}

    if not isinstance(geometry, dict) or not geometry.get("coordinates"):
        raise ValueError("Parsel geometrisi yok")

    # Drop huge metadata; keep pure GeoJSON geometry
    clean_geometry = {
        "type": geometry.get("type") or "Polygon",
        "coordinates": geometry["coordinates"],
    }

    area_m2 = _parse_area_m2(props)
    area_da = round(area_m2 / 1000.0, 4) if area_m2 is not None and area_m2 > 0 else None

    mahalle = (
        mahalle_name
        or props.get("mahalleAd")
        or props.get("mahalle")
        or props.get("mahalleAd")
        or None
    )
    ada_out = str(props.get("adaNo") or props.get("ada") or ada)
    parsel_out = str(props.get("parselNo") or props.get("parsel") or parsel)

    centroid = geometry_centroid(clean_geometry)
    if not centroid:
        raise ValueError("Merkez hesaplanamadı")

    return {
        "mahalle": mahalle,
        "mahalle_id": int(mahalle_id) if str(mahalle_id).isdigit() else mahalle_id,
        "ada": ada_out,
        "parsel": parsel_out,
        "area_da": area_da,
        "centroid": centroid,
        "geometry": clean_geometry,
    }


def fetch_parcel(
    mahalle_id: int | str,
    ada: str,
    parsel: str,
    *,
    mahalle_name: str | None = None,
) -> dict[str, Any]:
    ada_s = str(ada).strip()
    parsel_s = str(parsel).strip()
    if not ada_s or not parsel_s:
        raise ValueError("Ada ve parsel gerekli")
    url = f"{CBS_BASE}/parsel/{mahalle_id}/{ada_s}/{parsel_s}"
    raw = _get_json(url)
    return normalize_parcel(
        raw,
        mahalle_id=mahalle_id,
        ada=ada_s,
        parsel=parsel_s,
        mahalle_name=mahalle_name,
    )


def http_error_from_tkgm(exc: Exception) -> HTTPException:
    if isinstance(exc, TkgmNotFound):
        return HTTPException(
            status_code=404,
            detail="Parsel bulunamadı. Ada / parsel numarasını kontrol edin.",
        )
    if isinstance(exc, TkgmUnavailable):
        return HTTPException(
            status_code=502,
            detail="TKGM servisine şu an ulaşılamıyor. Konumu manuel girin.",
        )
    if isinstance(exc, ValueError):
        return HTTPException(status_code=400, detail=str(exc))
    return HTTPException(
        status_code=502,
        detail="TKGM servisine şu an ulaşılamıyor. Konumu manuel girin.",
    )
