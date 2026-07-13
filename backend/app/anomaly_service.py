"""Collect anomalies including IoT↔lab complementary conflicts."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy.orm import Session

from app.anomaly import (
    AnomalyFinding,
    ReadingSnapshot,
    detect_anomalies,
    detect_iot_lab_conflicts,
)
from app.models import LabReport, SensorReading


def _lab_param_value(report: LabReport, code: str) -> float | None:
    needle = code.lower().strip()
    for p in report.parameters:
        if p.parameter_code.lower().strip() == needle:
            return float(p.value)
    return None


def collect_farm_anomalies(db: Session, farm_id: int) -> list[AnomalyFinding]:
    rows = (
        db.query(SensorReading)
        .filter(SensorReading.farm_id == farm_id)
        .order_by(SensorReading.timestamp.desc())
        .limit(2)
        .all()
    )
    findings: list[AnomalyFinding] = []
    if rows:
        current = rows[0]
        previous = rows[1] if len(rows) > 1 else None
        findings.extend(
            detect_anomalies(
                ReadingSnapshot(
                    soil_moisture=current.soil_moisture,
                    timestamp=current.timestamp,
                    ph=current.ph,
                    last_irrigation_hours_ago=current.last_irrigation_hours_ago,
                    irrigation_duration=current.irrigation_duration,
                    source_type=current.source_type.value if current.source_type else None,
                ),
                (
                    ReadingSnapshot(
                        soil_moisture=previous.soil_moisture,
                        timestamp=previous.timestamp,
                        ph=previous.ph,
                        last_irrigation_hours_ago=previous.last_irrigation_hours_ago,
                        irrigation_duration=previous.irrigation_duration,
                    )
                    if previous
                    else None
                ),
                now=datetime.utcnow(),
            )
        )

        lab = (
            db.query(LabReport)
            .filter(
                LabReport.farm_id == farm_id,
                LabReport.user_confirmed.is_(True),
            )
            .order_by(LabReport.created_at.desc())
            .first()
        )
        if lab:
            findings.extend(
                detect_iot_lab_conflicts(
                    sensor_ec=current.ec,
                    sensor_ph=current.ph,
                    lab_ec=_lab_param_value(lab, "ec"),
                    lab_ph=_lab_param_value(lab, "ph"),
                    lab_confirmed=True,
                )
            )

    return findings
