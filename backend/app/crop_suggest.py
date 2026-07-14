"""Rule-based next-crop suggestions from farm season history + soil context.

Not ML. No fertilizer / disease prescriptions — rotation + moisture/lab hints only.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any

# Crop family map (Turkish MVP codes + common aliases)
CROP_FAMILY: dict[str, str] = {
    "domates": "solanaceae",
    "biber": "solanaceae",
    "patlican": "solanaceae",
    "patates": "solanaceae",
    "salatalik": "cucurbit",
    "kavun": "cucurbit",
    "karpuz": "cucurbit",
    "kabak": "cucurbit",
    "marul": "leafy",
    "ispanak": "leafy",
    "roka": "leafy",
    "fasulye": "legume",
    "bezelye": "legume",
    "nohut": "legume",
    "misir": "cereal",
    "bugday": "cereal",
    "arpa": "cereal",
    "yulaf": "cereal",
    "aycicegi": "oilseed",
    "pamuk": "fiber",
    "sogan": "allium",
    "sarimsak": "allium",
    "cilek": "berry",
    "uzum": "perennial",
    "zeytin": "perennial",
    "elma": "perennial",
}

FAMILY_LABEL_TR: dict[str, str] = {
    "solanaceae": "patlıcangiller",
    "cucurbit": "kabakgiller",
    "leafy": "yapraklı sebze",
    "legume": "baklagil",
    "cereal": "tahıl",
    "oilseed": "yağ bitkisi",
    "fiber": "lif bitkisi",
    "allium": "soğangiller",
    "berry": "yumuşak meyve",
    "perennial": "çok yıllık",
    "other": "diğer",
}

# Preferred follow-on families after a previous family (simple rotation)
ROTATION_NEXT: dict[str, list[str]] = {
    "solanaceae": ["cereal", "legume", "leafy", "allium", "oilseed"],
    "cucurbit": ["cereal", "legume", "leafy", "solanaceae"],
    "leafy": ["solanaceae", "legume", "cereal", "allium"],
    "legume": ["cereal", "solanaceae", "leafy", "cucurbit"],
    "cereal": ["legume", "oilseed", "solanaceae", "leafy"],
    "oilseed": ["cereal", "legume", "leafy"],
    "fiber": ["cereal", "legume"],
    "allium": ["leafy", "legume", "cereal", "solanaceae"],
    "berry": ["leafy", "legume"],
    "perennial": ["leafy", "legume"],  # inter-row / cover only — not replace orchard
    "other": ["cereal", "legume", "leafy"],
}

# Minimum fallow days before repeating same family (row crops)
SAME_FAMILY_FALLOW_DAYS: dict[str, int] = {
    "solanaceae": 90,
    "cucurbit": 60,
    "leafy": 21,
    "legume": 45,
    "cereal": 30,
    "oilseed": 45,
    "fiber": 60,
    "allium": 45,
    "berry": 30,
    "perennial": 3650,  # do not suggest replacing perennial
    "other": 30,
}

# Candidates offered in MVP (code → label)
CANDIDATE_CROPS: list[tuple[str, str, str]] = [
    ("bugday", "Buğday", "cereal"),
    ("arpa", "Arpa", "cereal"),
    ("misir", "Mısır", "cereal"),
    ("fasulye", "Fasulye", "legume"),
    ("marul", "Marul", "leafy"),
    ("sogan", "Soğan", "allium"),
    ("aycicegi", "Ayçiçeği", "oilseed"),
    ("domates", "Domates", "solanaceae"),
    ("biber", "Biber", "solanaceae"),
    ("salatalik", "Salatalık", "cucurbit"),
    ("patates", "Patates", "solanaceae"),
    ("cilek", "Çilek", "berry"),
]

WATER_DEMAND: dict[str, str] = {
    "domates": "high",
    "biber": "high",
    "salatalik": "high",
    "patates": "medium",
    "marul": "medium",
    "fasulye": "medium",
    "misir": "medium",
    "bugday": "low",
    "arpa": "low",
    "aycicegi": "low",
    "sogan": "medium",
    "cilek": "medium",
    "pamuk": "medium",
}


@dataclass
class SuggestionItem:
    crop_type: str
    label_tr: str
    family: str
    score: float
    reasons: list[str]
    suitable_now: bool


@dataclass
class SuggestionResult:
    suggestions: list[SuggestionItem]
    soil_condition: dict[str, Any]
    days_since_harvest: int | None
    previous_crop: str | None
    previous_family: str | None
    current_crop: str | None
    fallow_ok: bool
    explanation: str
    engine: str = "rule"


def crop_family(crop_type: str | None) -> str:
    if not crop_type:
        return "other"
    key = crop_type.lower().strip()
    return CROP_FAMILY.get(key, "other")


def suggest_next_crops(
    *,
    previous_crop: str | None,
    days_since_harvest: int | None,
    current_growing: str | None,
    soil_moisture: float | None,
    risk_level: str | None,
    lab_ph: float | None,
    lab_om: float | None,
    now: datetime | None = None,
) -> SuggestionResult:
    _ = now  # reserved for seasonal hooks
    prev_family = crop_family(previous_crop)
    preferred = ROTATION_NEXT.get(prev_family, ROTATION_NEXT["other"])
    same_fallow = SAME_FAMILY_FALLOW_DAYS.get(prev_family, 30)

    fallow_ok = True
    if current_growing:
        fallow_ok = False
    elif days_since_harvest is not None and days_since_harvest < 14:
        fallow_ok = False

    moisture = soil_moisture
    risk = (risk_level or "medium").lower()

    soil_condition = {
        "soil_moisture": moisture,
        "risk_level": risk if risk_level else None,
        "lab_ph": lab_ph,
        "lab_om": lab_om,
        "summary_tr": _soil_summary_tr(moisture, risk, lab_ph, lab_om),
    }

    items: list[SuggestionItem] = []
    for code, label, family in CANDIDATE_CROPS:
        if current_growing and code == current_growing.lower().strip():
            continue  # already growing
        reasons: list[str] = []
        score = 50.0
        suitable = True

        # Growing: only light cover / do not push new plantings
        if current_growing:
            suitable = False
            reasons.append("Sahada hâlâ yetişen ürün var; yeni ekim önerilmez.")
            score -= 40

        # Fallow after harvest
        if days_since_harvest is not None:
            if days_since_harvest < 14 and not current_growing:
                suitable = False
                reasons.append(
                    f"Hasattan sonra yalnızca {days_since_harvest} gün geçti; "
                    "kısa dinlenme önerilir (≥14 gün)."
                )
                score -= 25
            elif days_since_harvest >= 14:
                reasons.append(f"Hasattan bu yana {days_since_harvest} gün geçti.")
                score += min(15.0, days_since_harvest / 10.0)

        # Same family rotation lock
        if previous_crop and family == prev_family and prev_family != "other":
            needed = same_fallow
            if days_since_harvest is None or days_since_harvest < needed:
                suitable = False
                wait = needed - (days_since_harvest or 0)
                reasons.append(
                    f"Önceki ürün {FAMILY_LABEL_TR.get(prev_family, prev_family)} ailesinden; "
                    f"aynı aile için ~{needed} gün bekleyin"
                    + (f" (kalan ~{wait} gün)." if days_since_harvest is not None else ".")
                )
                score -= 35
            else:
                reasons.append(
                    f"Aynı aile ({FAMILY_LABEL_TR.get(family)}) için dinlenme süresi dolmuş."
                )
                score += 5
        elif previous_crop and family in preferred:
            rank = preferred.index(family)
            bonus = 25 - rank * 4
            score += bonus
            reasons.append(
                f"Rotasyon: {FAMILY_LABEL_TR.get(prev_family, prev_family)} sonrası "
                f"{FAMILY_LABEL_TR.get(family, family)} uygun."
            )

        # Moisture / risk
        demand = WATER_DEMAND.get(code, "medium")
        if moisture is not None:
            if moisture < 25 and demand == "high":
                suitable = False if moisture < 18 else suitable
                reasons.append(
                    f"Toprak nemi düşük (%{moisture:.0f}); su isteği yüksek ürün riskli."
                )
                score -= 20
            elif moisture < 30 and demand == "low":
                reasons.append("Düşük/orta nemde tahıl veya düşük su isteği tercih edilebilir.")
                score += 12
            elif moisture >= 35 and demand == "high":
                reasons.append("Nem seviyesi sebze ekimi için destekleyici.")
                score += 8
            elif moisture > 55 and demand == "low":
                reasons.append("Nem yüksek; tahıl için fazla ıslak olabilir — izleyin.")
                score -= 8

        if risk in ("high", "critical") and demand == "high":
            reasons.append(f"Sulama riski {risk}; yüksek su isteği olan ürün ertelenebilir.")
            score -= 15
            if risk == "critical":
                suitable = False

        # Lab pH / OM (confirmed values passed by caller)
        if lab_ph is not None:
            if lab_ph < 5.5 and family in ("legume", "cereal"):
                reasons.append(f"Lab pH düşük ({lab_ph:.1f}); baklagil/tahıl daha toleranslı olabilir.")
                score += 6
            elif lab_ph < 5.5 and family == "solanaceae":
                reasons.append(f"Lab pH düşük ({lab_ph:.1f}); patlıcangiller için sınırlayıcı olabilir.")
                score -= 10
            elif 6.0 <= lab_ph <= 7.5:
                reasons.append(f"Lab pH uygun aralıkta ({lab_ph:.1f}).")
                score += 5
            elif lab_ph > 8.0 and family == "leafy":
                reasons.append(f"Lab pH yüksek ({lab_ph:.1f}); yapraklı sebzede dikkat.")
                score -= 8

        if lab_om is not None:
            if lab_om >= 2.5 and family in ("leafy", "solanaceae", "cucurbit"):
                reasons.append(f"Organik madde yeterli (%{lab_om:.1f}); sebze için destekleyici.")
                score += 6
            elif lab_om < 1.5 and demand == "high":
                reasons.append(f"OM düşük (%{lab_om:.1f}); yoğun sebze yerine baklagil/tahıl düşünülebilir.")
                score -= 8
                if family in ("legume", "cereal"):
                    score += 10
                    reasons.append("Düşük OM’de baklagil/tahıl rotasyonu tercih edilir.")

        # Perennials: never suggest replacing active orchard via this engine
        if family == "perennial":
            continue

        score = max(0.0, min(100.0, score))
        if not reasons:
            reasons.append("Genel rotasyon adayı.")

        items.append(
            SuggestionItem(
                crop_type=code,
                label_tr=label,
                family=family,
                score=round(score, 1),
                reasons=reasons[:4],
                suitable_now=suitable and score >= 40,
            )
        )

    items.sort(key=lambda x: (x.suitable_now, x.score), reverse=True)
    top = items[:6]

    explanation = _build_explanation(
        previous_crop=previous_crop,
        prev_family=prev_family,
        days_since_harvest=days_since_harvest,
        current_growing=current_growing,
        soil_condition=soil_condition,
        top=top,
    )

    return SuggestionResult(
        suggestions=top,
        soil_condition=soil_condition,
        days_since_harvest=days_since_harvest,
        previous_crop=previous_crop,
        previous_family=prev_family if previous_crop else None,
        current_crop=current_growing,
        fallow_ok=fallow_ok,
        explanation=explanation,
    )


def _soil_summary_tr(
    moisture: float | None,
    risk: str,
    lab_ph: float | None,
    lab_om: float | None,
) -> str:
    parts: list[str] = []
    if moisture is not None:
        if moisture < 25:
            parts.append(f"nem düşük (%{moisture:.0f})")
        elif moisture < 40:
            parts.append(f"nem orta (%{moisture:.0f})")
        else:
            parts.append(f"nem yeterli/yüksek (%{moisture:.0f})")
    else:
        parts.append("nem ölçümü yok")
    if risk and risk != "medium":
        parts.append(f"sulama riski: {risk}")
    if lab_ph is not None:
        parts.append(f"lab pH {lab_ph:.1f}")
    if lab_om is not None:
        parts.append(f"OM %{lab_om:.1f}")
    return "; ".join(parts)


def _build_explanation(
    *,
    previous_crop: str | None,
    prev_family: str,
    days_since_harvest: int | None,
    current_growing: str | None,
    soil_condition: dict[str, Any],
    top: list[SuggestionItem],
) -> str:
    bits: list[str] = []
    if current_growing:
        bits.append(
            f"Şu an sahada {current_growing} yetişiyor; hasat tamamlanana kadar yeni ekim önerilmez."
        )
    elif previous_crop:
        fam = FAMILY_LABEL_TR.get(prev_family, prev_family)
        days = (
            f" Hasattan {days_since_harvest} gün geçti."
            if days_since_harvest is not None
            else ""
        )
        bits.append(f"Önceki ürün: {previous_crop} ({fam}).{days}")
    else:
        bits.append("Henüz kayıtlı hasat yok; öneriler genel rotasyon ve toprak durumuna göre.")

    bits.append(f"Toprak durumu: {soil_condition.get('summary_tr')}.")

    good = [s for s in top if s.suitable_now]
    if good:
        names = ", ".join(s.label_tr for s in good[:3])
        bits.append(f"Kural motoru öncelikli adaylar: {names}.")
    else:
        bits.append("Şu an uygun ekim adayı sınırlı; dinlenme veya nem iyileştirmesi bekleyin.")

    bits.append(
        "Bu öneriler basit ürün rotasyonu kurallarıdır; gübre/ilaç reçetesi veya hastalık teşhisi değildir."
    )
    return " ".join(bits)
