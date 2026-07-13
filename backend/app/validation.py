from datetime import datetime


def compute_data_confidence(
    *,
    soil_moisture: float,
    air_temperature: float | None,
    rainfall_probability: float | None,
    last_irrigation_hours_ago: float | None,
    timestamp: datetime | None = None,
) -> tuple[float, list[str]]:
    """Return confidence 0-100 and warning messages."""
    score = 100.0
    warnings: list[str] = []

    if not 0 <= soil_moisture <= 100:
        score -= 40
        warnings.append("Toprak nemi geçerli aralıkta değil (0–100)")

    if air_temperature is None:
        score -= 10
        warnings.append("Hava sıcaklığı eksik")
    if rainfall_probability is None:
        score -= 10
        warnings.append("Yağış ihtimali eksik")
    if last_irrigation_hours_ago is None:
        score -= 10
        warnings.append("Son sulama zamanı eksik")

    if timestamp is not None:
        age_hours = (datetime.utcnow() - timestamp).total_seconds() / 3600
        if age_hours > 24:
            score -= 30
            warnings.append("Veri güncel değil (24 saatten eski)")

    return max(0.0, min(100.0, score)), warnings
