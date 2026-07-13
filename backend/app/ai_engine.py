"""Rule-based irrigation decision engine for AgriTwin MVP."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class RuleInput:
    soil_moisture: float
    air_temperature: float | None = None
    rainfall_probability: float | None = None
    last_irrigation_hours_ago: float | None = None
    soil_type: str | None = None
    crop_type: str | None = None
    growth_stage: str | None = None
    data_confidence: float | None = 100.0
    data_age_hours: float | None = 0.0
    materials_summary: str | None = None
    material_notes: list[str] | None = None
    ec: float | None = None


@dataclass
class RuleResult:
    irrigation_needed: bool
    irrigation_duration: float | None
    risk_level: str
    confidence_score: float
    explanation: str
    moisture_24h: float
    moisture_48h: float
    moisture_72h: float


def _daily_moisture_drop(inp: RuleInput) -> float:
    drop = 3.0
    if inp.air_temperature is not None:
        if inp.air_temperature >= 32:
            drop += 4.0
        elif inp.air_temperature >= 28:
            drop += 2.5
        elif inp.air_temperature >= 24:
            drop += 1.0
    if inp.rainfall_probability is not None and inp.rainfall_probability >= 50:
        drop -= 2.0
    if inp.soil_type and inp.soil_type.lower() in {"kumlu", "sandy"}:
        drop += 1.5
    return max(1.0, drop)


def predict_irrigation(inp: RuleInput) -> RuleResult:
    reasons: list[str] = []
    confidence = float(inp.data_confidence if inp.data_confidence is not None else 80.0)

    if inp.data_age_hours is not None and inp.data_age_hours > 24:
        confidence -= 30
        reasons.append("Veri 24 saatten eski olduğu için güven skoru düşürüldü")

    rain = inp.rainfall_probability if inp.rainfall_probability is not None else 0.0
    hours = inp.last_irrigation_hours_ago if inp.last_irrigation_hours_ago is not None else 48.0
    temp = inp.air_temperature if inp.air_temperature is not None else 25.0
    moisture = inp.soil_moisture

    irrigation_needed = False
    duration: float | None = None
    risk = "low"

    if moisture > 70:
        risk = "high"
        reasons.append(f"Toprak nemi %{moisture:.0f} — aşırı sulama riski")
        irrigation_needed = False
    elif moisture < 25:
        risk = "critical"
        irrigation_needed = True
        duration = 18.0
        reasons.append(f"Toprak nemi kritik seviyede (%{moisture:.0f})")
    elif moisture < 30 and rain < 20 and hours > 24:
        risk = "high"
        irrigation_needed = True
        duration = 14.0
        reasons.append(
            f"Nem %{moisture:.0f}, yağış ihtimali %{rain:.0f}, son sulama {hours:.0f} saat önce"
        )
        if temp >= 30:
            reasons.append(f"Hava sıcaklığı yüksek ({temp:.0f}°C)")
            duration = 16.0
    elif moisture < 35 and rain < 30:
        risk = "medium"
        irrigation_needed = True
        duration = 10.0
        reasons.append(f"Nem %{moisture:.0f} ve yağış düşük — sulama yaklaşıyor")
    elif moisture < 40:
        risk = "medium"
        irrigation_needed = False
        reasons.append(f"Nem %{moisture:.0f} — izleme yeterli, acil sulama gerekmiyor")
    else:
        risk = "low"
        irrigation_needed = False
        reasons.append(f"Toprak nemi yeterli (%{moisture:.0f})")

    if inp.air_temperature is None or inp.rainfall_probability is None:
        confidence -= 15
        reasons.append("Eksik veri nedeniyle analiz sınırlı")

    confidence = max(20.0, min(100.0, confidence))

    drop = _daily_moisture_drop(inp)
    m24 = max(0.0, moisture - drop)
    m48 = max(0.0, moisture - drop * 2)
    m72 = max(0.0, moisture - drop * 3)

    if not irrigation_needed and m48 < 28 and rain < 25:
        risk = "high" if risk in {"low", "medium"} else risk
        irrigation_needed = True
        duration = duration or 12.0
        reasons.append("48 saat içinde nem kritik eşiğe düşebilir")

    if inp.material_notes:
        reasons.extend(inp.material_notes[:2])
    explanation = ". ".join(reasons) + "."
    if irrigation_needed:
        explanation = f"Sulama öneriliyor. {explanation}"
    else:
        explanation = f"Şu an sulama gerekli değil. {explanation}"

    return RuleResult(
        irrigation_needed=irrigation_needed,
        irrigation_duration=duration,
        risk_level=risk,
        confidence_score=round(confidence, 1),
        explanation=explanation,
        moisture_24h=round(m24, 1),
        moisture_48h=round(m48, 1),
        moisture_72h=round(m72, 1),
    )
