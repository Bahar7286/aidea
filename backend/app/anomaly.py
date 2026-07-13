"""Rule-based anomaly detection for AgriTwin MVP."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass
class ReadingSnapshot:
    soil_moisture: float
    timestamp: datetime
    ph: float | None = None
    last_irrigation_hours_ago: float | None = None
    irrigation_duration: float | None = None
    source_type: str | None = None


@dataclass
class AnomalyFinding:
    code: str
    severity: str  # low | medium | high | critical
    title: str
    message: str


def detect_anomalies(
    current: ReadingSnapshot,
    previous: ReadingSnapshot | None = None,
    *,
    now: datetime | None = None,
) -> list[AnomalyFinding]:
    findings: list[AnomalyFinding] = []
    now = now or datetime.utcnow()

    age_hours = (now - current.timestamp).total_seconds() / 3600
    if age_hours > 24:
        findings.append(
            AnomalyFinding(
                code="stale_data",
                severity="medium",
                title="Eski veri",
                message=f"Son veri {age_hours:.0f} saat önce — güncel değil.",
            )
        )

    if current.ph is not None and (current.ph < 0 or current.ph > 14):
        findings.append(
            AnomalyFinding(
                code="invalid_ph",
                severity="high",
                title="Gerçekçi olmayan pH",
                message=f"pH değeri {current.ph} geçerli aralıkta değil (0–14).",
            )
        )
    elif current.ph is not None and (current.ph < 4.0 or current.ph > 9.5):
        findings.append(
            AnomalyFinding(
                code="extreme_ph",
                severity="medium",
                title="Aşırı pH",
                message=f"pH {current.ph} tarımsal aralık dışında olabilir.",
            )
        )

    if previous is not None:
        hours_between = max(
            (current.timestamp - previous.timestamp).total_seconds() / 3600,
            0.01,
        )
        delta = abs(current.soil_moisture - previous.soil_moisture)
        # Sudden jump: >15% within ~1 hour (scaled)
        if hours_between <= 2 and delta >= 15:
            findings.append(
                AnomalyFinding(
                    code="sudden_moisture_jump",
                    severity="high",
                    title="Ani nem değişimi",
                    message=(
                        f"Nem %{previous.soil_moisture:.0f} → %{current.soil_moisture:.0f} "
                        f"({hours_between:.1f} saatte %{delta:.0f} fark)."
                    ),
                )
            )

        # Post-irrigation: recent irrigation but moisture did not rise
        irrigated_recently = (
            current.last_irrigation_hours_ago is not None
            and current.last_irrigation_hours_ago <= 3
            and (current.irrigation_duration or 0) > 0
        )
        if irrigated_recently and current.soil_moisture <= previous.soil_moisture + 2:
            findings.append(
                AnomalyFinding(
                    code="post_irrigation_no_rise",
                    severity="high",
                    title="Sulama sonrası beklenmeyen sonuç",
                    message=(
                        "Yakın zamanda sulama kaydı var ancak nem artışı gözlenmedi. "
                        "Vana veya sensör kontrol edilmeli."
                    ),
                )
            )

    if previous is None and age_hours > 48:
        findings.append(
            AnomalyFinding(
                code="data_gap",
                severity="medium",
                title="Veri kesintisi şüphesi",
                message="Karşılaştırılacak önceki okuma yok ve son veri çok eski.",
            )
        )

    return findings


def detect_iot_lab_conflicts(
    *,
    sensor_ec: float | None = None,
    sensor_ph: float | None = None,
    lab_ec: float | None = None,
    lab_ph: float | None = None,
    lab_confirmed: bool = False,
) -> list[AnomalyFinding]:
    """Flag complementary IoT vs lab chemistry conflicts (P1).

    Never implies continuous IoT replaces laboratory analysis.
    """
    if not lab_confirmed:
        return []

    findings: list[AnomalyFinding] = []
    disclaimer = (
        " IoT sürekliliği laboratuvar kimyasını değiştirmez; sonuçlar tamamlayıcıdır."
    )

    if sensor_ec is not None and lab_ec is not None and lab_ec > 0:
        rel = abs(sensor_ec - lab_ec) / lab_ec
        abs_delta = abs(sensor_ec - lab_ec)
        if rel >= 0.4 or abs_delta >= 1.0:
            findings.append(
                AnomalyFinding(
                    code="iot_lab_ec_conflict",
                    severity="medium",
                    title="IoT–lab EC çelişkisi",
                    message=(
                        f"Sensör EC {sensor_ec:.2f} ile onaylı lab EC {lab_ec:.2f} "
                        f"anlamlı fark gösteriyor.{disclaimer}"
                    ),
                )
            )

    if sensor_ph is not None and lab_ph is not None:
        if abs(sensor_ph - lab_ph) >= 1.0:
            findings.append(
                AnomalyFinding(
                    code="iot_lab_ph_conflict",
                    severity="medium",
                    title="IoT–lab pH çelişkisi",
                    message=(
                        f"Sensör pH {sensor_ph:.1f} ile onaylı lab pH {lab_ph:.1f} "
                        f"farklı.{disclaimer}"
                    ),
                )
            )

    return findings
