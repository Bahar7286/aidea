"""OpenRouter helpers for soil lab report parse + narrative (no fertilizer Rx)."""

from __future__ import annotations

import json
import logging
import re
from typing import Any

import httpx

from app.config import settings
from app.lab_interpret import DEFAULT_UNITS, normalize_code

logger = logging.getLogger(__name__)

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
DEFAULT_MODEL = "openai/gpt-4o-mini"
MAX_TEXT_CHARS = 8000

ALLOWED_PARSE_CODES = {
    "ph",
    "ec",
    "om",
    "lime",
    "p",
    "k",
    "n",
    "ca",
    "mg",
    "zn",
    "fe",
    "b",
    "na",
    "texture",
    "saturation",
}

_BANNED_RX = (
    "gübre reçete",
    "gubre reçete",
    "npk uygula",
    "azot doz",
    "kg/da uygula",
    "fertilizer prescription",
)


def _headers(api_key: str) -> dict[str, str]:
    return {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://aidea-three.vercel.app",
        "X-Title": "AgriTwin AI",
    }


def _model() -> str:
    return settings.openrouter_model or DEFAULT_MODEL


def parse_soil_report_with_ai(text: str) -> tuple[list[dict], float, str] | None:
    """Ask OpenRouter for structured soil parameters. Returns None if unavailable/failed."""
    key = (settings.openrouter_api_key or "").strip()
    if not key:
        return None
    clipped = (text or "").strip()[:MAX_TEXT_CHARS]
    if len(clipped) < 40:
        return None

    payload: dict[str, Any] = {
        "model": _model(),
        "temperature": 0.1,
        "max_tokens": 900,
        "response_format": {"type": "json_object"},
        "messages": [
            {
                "role": "system",
                "content": (
                    "Sen tarımsal toprak laboratuvar raporu ayrıştırıcısısın. "
                    "Yalnızca JSON döndür. Şema: "
                    '{"is_soil_report": bool, "confidence": 0-100, '
                    '"rejection_reason_tr": string|null, '
                    '"parameters": [{"parameter_code": str, "value": number, '
                    '"unit": str, "confidence_pct": 0-100}]}. '
                    "parameter_code yalnızca: ph, ec, om, lime, p, k, n, ca, mg, zn, fe, b, na, "
                    "texture, saturation. "
                    "texture için value 0 kullan ve birime bünye adını yaz (örn. tınlı). "
                    "Fatura, hava, fatura PDF, doktor raporu vb. ise is_soil_report=false "
                    "ve parameters=[]. Gübre reçetesi üretme; yalnızca rapordaki değerleri çıkar."
                ),
            },
            {
                "role": "user",
                "content": clipped,
            },
        ],
    }
    try:
        with httpx.Client(timeout=28.0) as client:
            resp = client.post(OPENROUTER_URL, headers=_headers(key), json=payload)
            resp.raise_for_status()
            data = resp.json()
        choices = data.get("choices") or []
        if not choices:
            return None
        content = (choices[0].get("message") or {}).get("content")
        if not isinstance(content, str) or not content.strip():
            return None
        parsed = _extract_json_object(content)
        if not parsed:
            return None
        if parsed.get("is_soil_report") is False:
            reason = (
                str(parsed.get("rejection_reason_tr") or "").strip()
                or "AI bu belgenin tarımsal toprak analiz raporu olmadığını belirtti."
            )
            return [], 0.0, reason
        rows = _validate_ai_parameters(parsed.get("parameters") or [])
        conf = parsed.get("confidence")
        try:
            avg = float(conf) if conf is not None else (
                sum(r["confidence_pct"] for r in rows) / len(rows) if rows else 0.0
            )
        except (TypeError, ValueError):
            avg = sum(r["confidence_pct"] for r in rows) / len(rows) if rows else 0.0
        msg = "OpenRouter ile yapılandırılmış çıkarım. Değerleri doğrulayın; otomatik kayıt yok."
        return rows, round(avg, 1), msg
    except Exception as exc:  # noqa: BLE001
        logger.warning("OpenRouter lab parse failed: %s", exc)
        return None


def enrich_lab_narrative(
    *,
    parameters: list[dict],
    rule_summary: str,
    insights: list[dict],
) -> str | None:
    """Rewrite lab insight summary in Turkish when OpenRouter key is set."""
    key = (settings.openrouter_api_key or "").strip()
    if not key:
        return None
    try:
        payload: dict[str, Any] = {
            "model": _model(),
            "temperature": 0.3,
            "max_tokens": 320,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "Sen AgriTwin AI toprak laboratuvar yorumcususun. Sadece Türkçe yaz. "
                        "Kullanıcı onaylı lab değerlerini ve kural özetini bozma. "
                        "Gübre/ilaç reçetesi, doz (kg/da, NPK), hastalık teşhisi yazma. "
                        "Labın IoT nem sensörünün yerine geçmediğini belirt. "
                        "2-4 kısa cümle; sulama/nem bağlamına katkı olarak yorumla."
                    ),
                },
                {
                    "role": "user",
                    "content": json.dumps(
                        {
                            "kural_ozet": rule_summary,
                            "parametreler": parameters,
                            "bulgular": [
                                {
                                    "kod": i.get("parameter_code"),
                                    "risk": i.get("risk"),
                                    "mesaj": i.get("message"),
                                }
                                for i in insights[:8]
                            ],
                        },
                        ensure_ascii=False,
                    ),
                },
            ],
        }
        with httpx.Client(timeout=18.0) as client:
            resp = client.post(OPENROUTER_URL, headers=_headers(key), json=payload)
            resp.raise_for_status()
            data = resp.json()
        choices = data.get("choices") or []
        if not choices:
            return None
        content = (choices[0].get("message") or {}).get("content")
        if not isinstance(content, str):
            return None
        text = content.strip()
        if len(text) < 20:
            return None
        lower = text.lower()
        for banned in _BANNED_RX:
            if banned in lower:
                return None
        return text[:900]
    except Exception as exc:  # noqa: BLE001
        logger.warning("OpenRouter lab narrative failed: %s", exc)
        return None


def _extract_json_object(content: str) -> dict[str, Any] | None:
    raw = content.strip()
    if raw.startswith("```"):
        raw = re.sub(r"^```(?:json)?\s*", "", raw)
        raw = re.sub(r"\s*```$", "", raw)
    try:
        obj = json.loads(raw)
        return obj if isinstance(obj, dict) else None
    except json.JSONDecodeError:
        match = re.search(r"\{[\s\S]*\}", raw)
        if not match:
            return None
        try:
            obj = json.loads(match.group(0))
            return obj if isinstance(obj, dict) else None
        except json.JSONDecodeError:
            return None


def _validate_ai_parameters(raw: list[Any]) -> list[dict]:
    out: dict[str, dict] = {}
    for item in raw:
        if not isinstance(item, dict):
            continue
        code = normalize_code(str(item.get("parameter_code") or ""))
        if code not in ALLOWED_PARSE_CODES:
            continue
        try:
            value = float(item.get("value"))
        except (TypeError, ValueError):
            continue
        unit = str(item.get("unit") or "").strip() or DEFAULT_UNITS.get(code, "")
        if code == "texture" and not unit:
            unit = "bünye"
        if not unit:
            continue
        try:
            conf = float(item.get("confidence_pct") if item.get("confidence_pct") is not None else 75)
        except (TypeError, ValueError):
            conf = 75.0
        conf = max(0.0, min(100.0, conf))
        out[code] = {
            "parameter_code": code,
            "value": value,
            "unit": unit[:40],
            "confidence_pct": round(conf, 1),
            "extracted_auto": True,
        }
    return list(out.values())
