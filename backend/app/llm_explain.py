"""Optional OpenRouter LLM explanations for irrigation (Turkish).

Rules remain the safety floor: numbers/risk/confidence come from ai_engine.
When OPENROUTER_API_KEY is set, LLM rewrites the explanation only.
Fertilizer prescriptions are never requested or returned.
"""

from __future__ import annotations

import json
import logging
from typing import Any

import httpx

from app.ai_engine import RuleInput, RuleResult
from app.config import settings

logger = logging.getLogger(__name__)

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
DEFAULT_MODEL = "openai/gpt-4o-mini"


def enrich_explanation(inp: RuleInput, result: RuleResult) -> RuleResult:
    """Return result with LLM explanation when API key present; else unchanged.

    Materials context may already be folded into rule explanation via material_notes.
    When LLM is available, materials_summary is passed for irrigation/EC commentary only.
    """
    key = (settings.openrouter_api_key or "").strip()
    if not key:
        return result

    try:
        text = _call_openrouter(key, inp, result)
        if text:
            return RuleResult(
                irrigation_needed=result.irrigation_needed,
                irrigation_duration=result.irrigation_duration,
                risk_level=result.risk_level,
                confidence_score=result.confidence_score,
                explanation=text,
                moisture_24h=result.moisture_24h,
                moisture_48h=result.moisture_48h,
                moisture_72h=result.moisture_72h,
            )
    except Exception as exc:  # noqa: BLE001 — graceful fallback
        logger.warning("OpenRouter explanation failed: %s", exc)
    return result


def _call_openrouter(api_key: str, inp: RuleInput, result: RuleResult) -> str | None:
    decision = "sulama öneriliyor" if result.irrigation_needed else "sulama gerekli değil"
    payload: dict[str, Any] = {
        "model": settings.openrouter_model or DEFAULT_MODEL,
        "temperature": 0.3,
        "max_tokens": 320,
        "messages": [
            {
                "role": "system",
                "content": (
                    "Sen AgriTwin AI sulama danışmanısın. Sadece Türkçe yaz. "
                    "Kural motoru kararını ve sayısal değerleri değiştirme; yalnızca neden "
                    "açıkla. Gübre/ilaç reçetesi, doz (kg/da, NPK uygulaması), hastalık teşhisi "
                    "veya uydu iddiası yazma. Kullanıcının kayıtlı gübre/ilaç sınıflarını yalnızca "
                    "nem, sulama, EC/tuzluluk ve veri kalitesi bağlamında yorumla "
                    "(örn. yüksek K fertigasyon → EC izle; yaprak uygulaması ≠ toprak nemi). "
                    "Sanal sulama için kullanıcı onayı gerektiğini belirt. "
                    "Simüle IoT verisi gerçek saha sensörü değildir; abartma. "
                    "2-4 kısa cümle; sade ve çiftçi dostu."
                ),
            },
            {
                "role": "user",
                "content": json.dumps(
                    {
                        "karar": decision,
                        "sure_dk": result.irrigation_duration,
                        "risk": result.risk_level,
                        "guven": result.confidence_score,
                        "kural_aciklama": result.explanation,
                        "olcum": {
                            "toprak_nemi": inp.soil_moisture,
                            "hava_sicakligi": inp.air_temperature,
                            "yagis_olasiligi": inp.rainfall_probability,
                            "son_sulama_saat": inp.last_irrigation_hours_ago,
                            "toprak_tipi": inp.soil_type,
                            "urun": inp.crop_type,
                            "gelisim": inp.growth_stage,
                            "ec": inp.ec,
                        },
                        "arazi_malzemeleri": inp.materials_summary,
                        "malzeme_notlari": inp.material_notes or [],
                        "tahmini_nem": {
                            "24s": result.moisture_24h,
                            "48s": result.moisture_48h,
                            "72s": result.moisture_72h,
                        },
                    },
                    ensure_ascii=False,
                ),
            },
        ],
    }
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://aidea-three.vercel.app",
        "X-Title": "AgriTwin AI",
    }
    with httpx.Client(timeout=18.0) as client:
        resp = client.post(OPENROUTER_URL, headers=headers, json=payload)
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
    # Soft guard: never let LLM flip into fertilizer land in display
    lower = text.lower()
    for banned in ("gübre reçete", "gubre reçete", "npk uygula", "azot doz"):
        if banned in lower:
            return None
    return text[:900]


def enrich_crop_suggestion_explanation(
    *,
    explanation: str,
    context: dict[str, Any],
) -> str | None:
    """Rewrite next-crop explanation in Turkish when OpenRouter key is set.

    Does not change suggestion list, scores, or suitability flags.
    """
    key = (settings.openrouter_api_key or "").strip()
    if not key:
        return None

    try:
        payload: dict[str, Any] = {
            "model": settings.openrouter_model or DEFAULT_MODEL,
            "temperature": 0.3,
            "max_tokens": 280,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "Sen AgriTwin AI ürün rotasyonu danışmanısın. Sadece Türkçe yaz. "
                        "Kural motorunun önerdiği ürün listesini ve skorları değiştirme; "
                        "yalnızca açıklama metnini sadeleştir. Gübre/ilaç reçetesi, doz, "
                        "hastalık teşhisi veya verim garantisi yazma. 2-4 kısa cümle."
                    ),
                },
                {
                    "role": "user",
                    "content": json.dumps(
                        {
                            "kural_aciklama": explanation,
                            "baglam": context,
                        },
                        ensure_ascii=False,
                    ),
                },
            ],
        }
        headers = {
                        "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://aidea-three.vercel.app",
            "X-Title": "AgriTwin AI",
        }
        with httpx.Client(timeout=18.0) as client:
            resp = client.post(OPENROUTER_URL, headers=headers, json=payload)
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
        for banned in ("gübre reçete", "gubre reçete", "npk uygula", "azot doz"):
            if banned in lower:
                return None
        return text[:900]
    except Exception as exc:  # noqa: BLE001
        logger.warning("OpenRouter crop explanation failed: %s", exc)
        return None
