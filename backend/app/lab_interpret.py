"""Rule-based lab soil interpretation (not fertilizer prescriptions)."""

from __future__ import annotations

PARAM_LABELS = {
    "ph": "pH",
    "ec": "EC",
    "om": "Organik madde",
    "organic_matter": "Organik madde",
    "lime": "Kireç",
    "p": "Fosfor",
    "phosphorus": "Fosfor",
    "k": "Potasyum",
    "potassium": "Potasyum",
    "n": "Azot",
    "nitrogen": "Azot",
    "zn": "Çinko",
    "zinc": "Çinko",
    "fe": "Demir",
    "iron": "Demir",
    "b": "Bor",
    "boron": "Bor",
    "mg": "Magnezyum",
    "magnesium": "Magnezyum",
    "na": "Sodyum",
    "sodium": "Sodyum",
    "texture": "Bünye",
    "saturation": "Saturasyon",
}

DEFAULT_UNITS = {
    "ph": "pH",
    "ec": "dS/m",
    "om": "%",
    "organic_matter": "%",
    "lime": "%",
    "p": "ppm",
    "phosphorus": "ppm",
    "k": "ppm",
    "potassium": "ppm",
    "n": "ppm",
    "nitrogen": "ppm",
    "zn": "ppm",
    "zinc": "ppm",
    "fe": "ppm",
    "iron": "ppm",
    "b": "ppm",
    "boron": "ppm",
    "mg": "ppm",
    "magnesium": "ppm",
    "na": "ppm",
    "sodium": "ppm",
}


def normalize_code(code: str) -> str:
    c = code.lower().strip()
    aliases = {
        "organic_matter": "om",
        "phosphorus": "p",
        "potassium": "k",
        "nitrogen": "n",
        "zinc": "zn",
        "iron": "fe",
        "boron": "b",
        "magnesium": "mg",
        "sodium": "na",
        "caco3": "lime",
        "p2o5": "p",
        "k2o": "k",
    }
    return aliases.get(c, c)


def param_label(code: str) -> str:
    return PARAM_LABELS.get(normalize_code(code), code)


def classify_value(code: str, value: float) -> dict:
    """Return label, tone, and optional insight for a parameter."""
    c = normalize_code(code)
    if c == "ph":
        if value < 5.5:
            return {
                "label": "Asidik",
                "tone": "warn",
                "risk": "medium",
                "message": "Asidik pH besin alınabilirliğini düşürebilir.",
            }
        if value < 6.5:
            return {
                "label": "İdeal",
                "tone": "ok",
                "risk": "low",
                "message": "pH çoğu ürün için uygun aralıkta.",
            }
        if value <= 7.5:
            return {
                "label": "Nötr / hafif alkali",
                "tone": "ok",
                "risk": "low",
                "message": "pH kabul edilebilir; mikro besinleri izleyin.",
            }
        if value <= 8.2:
            return {
                "label": "Hafif alkali",
                "tone": "warn",
                "risk": "medium",
                "message": "Hafif alkali pH — demir/çinko alınabilirliği azalabilir.",
            }
        return {
            "label": "Alkali",
            "tone": "critical",
            "risk": "high",
            "message": "Yüksek pH — kritik bulgu; uzman görüşü önerilir.",
        }
    if c == "ec":
        if value < 0.8:
            return {"label": "Düşük", "tone": "ok", "risk": "low", "message": "EC düşük-orta; tuzluluk riski sınırlı."}
        if value <= 2.0:
            return {"label": "Orta", "tone": "ok", "risk": "low", "message": "EC orta seviyede."}
        if value <= 3.5:
            return {"label": "Yüksek", "tone": "warn", "risk": "medium", "message": "EC yüksek — sulama suyu ve drenajı kontrol edin."}
        return {"label": "Kritik", "tone": "critical", "risk": "high", "message": "Yüksek tuzluluk (EC) — kritik bulgu."}
    if c == "om":
        if value < 1.5:
            return {
                "label": "Düşük",
                "tone": "critical",
                "risk": "high",
                "message": "Organik madde düşük — toprak yapısı ve su tutumu zayıf olabilir.",
            }
        if value < 2.5:
            return {"label": "Orta-düşük", "tone": "warn", "risk": "medium", "message": "Organik madde sınırda; iyileştirme önerilir."}
        if value < 4.0:
            return {"label": "İyi", "tone": "ok", "risk": "low", "message": "Organik madde yeterli."}
        return {"label": "Yüksek", "tone": "ok", "risk": "low", "message": "Organik madde yüksek."}
    if c in {"p", "k", "n"}:
        low = 15 if c != "k" else 150
        high = 40 if c != "k" else 350
        if value < low:
            return {"label": "Düşük", "tone": "warn", "risk": "medium", "message": f"{param_label(c)} düşük görünüyor (bilgi amaçlı; reçete değil)."}
        if value > high:
            return {"label": "Yüksek", "tone": "warn", "risk": "low", "message": f"{param_label(c)} yüksek; gübreleme planında dikkate alın."}
        return {"label": "Yeterli", "tone": "ok", "risk": "low", "message": f"{param_label(c)} yeterli aralıkta."}
    if c == "lime":
        if value > 25:
            return {"label": "Yüksek", "tone": "warn", "risk": "medium", "message": "Kireç oranı yüksek."}
        return {"label": "Uygun", "tone": "ok", "risk": "low", "message": "Kireç oranı kabul edilebilir."}
    return {"label": "—", "tone": "neutral", "risk": "low", "message": f"{param_label(c)} kaydı mevcut."}


def interpret_report(parameters: list[dict]) -> list[dict]:
    insights: list[dict] = []
    for p in parameters:
        code = p.get("parameter_code") or p.get("code")
        value = p.get("value")
        if code is None or value is None:
            continue
        info = classify_value(str(code), float(value))
        insights.append(
            {
                "parameter_code": normalize_code(str(code)),
                "label": param_label(str(code)),
                "value": float(value),
                "unit": p.get("unit") or DEFAULT_UNITS.get(normalize_code(str(code)), ""),
                "status_label": info["label"],
                "tone": info["tone"],
                "risk": info["risk"],
                "message": info["message"],
            }
        )
    # sort critical first
    order = {"high": 0, "medium": 1, "low": 2}
    insights.sort(key=lambda x: order.get(x["risk"], 9))
    return insights


def count_critical(insights: list[dict]) -> int:
    return sum(1 for i in insights if i.get("risk") == "high")


def demo_extraction() -> tuple[list[dict], float]:
    """Simulated OCR-like values — not real document OCR."""
    rows = [
        {"parameter_code": "ph", "value": 7.8, "unit": "pH", "confidence_pct": 96, "extracted_auto": True},
        {"parameter_code": "ec", "value": 1.42, "unit": "dS/m", "confidence_pct": 91, "extracted_auto": True},
        {"parameter_code": "om", "value": 1.65, "unit": "%", "confidence_pct": 88, "extracted_auto": True},
        {"parameter_code": "lime", "value": 21.3, "unit": "%", "confidence_pct": 84, "extracted_auto": True},
        {"parameter_code": "p", "value": 18.5, "unit": "ppm", "confidence_pct": 79, "extracted_auto": True},
        {"parameter_code": "k", "value": 280, "unit": "ppm", "confidence_pct": 93, "extracted_auto": True},
        {"parameter_code": "n", "value": 42, "unit": "ppm", "confidence_pct": 72, "extracted_auto": True},
        {"parameter_code": "zn", "value": 1.1, "unit": "ppm", "confidence_pct": 65, "extracted_auto": True},
        {"parameter_code": "fe", "value": 8.4, "unit": "ppm", "confidence_pct": 58, "extracted_auto": True},
    ]
    avg = sum(r["confidence_pct"] for r in rows) / len(rows)
    return rows, round(avg, 1)


def compute_status(user_confirmed: bool, parameters: list) -> str:
    codes = {normalize_code(getattr(p, "parameter_code", None) or p.get("parameter_code", "")) for p in parameters}
    if "ph" not in codes or len(codes) < 2:
        return "missing"
    if not user_confirmed:
        return "pending"
    return "verified"
