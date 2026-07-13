from datetime import datetime, timedelta
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app.anomaly import ReadingSnapshot, detect_anomalies, detect_iot_lab_conflicts
from app.water_report import compute_water_usage


def test_sudden_moisture_jump():
    now = datetime.utcnow()
    findings = detect_anomalies(
        ReadingSnapshot(soil_moisture=92, timestamp=now),
        ReadingSnapshot(soil_moisture=38, timestamp=now - timedelta(hours=1)),
    )
    codes = {f.code for f in findings}
    assert "sudden_moisture_jump" in codes


def test_post_irrigation_no_rise():
    now = datetime.utcnow()
    findings = detect_anomalies(
        ReadingSnapshot(
            soil_moisture=29,
            timestamp=now,
            last_irrigation_hours_ago=2,
            irrigation_duration=15,
        ),
        ReadingSnapshot(soil_moisture=28, timestamp=now - timedelta(hours=2)),
    )
    codes = {f.code for f in findings}
    assert "post_irrigation_no_rise" in codes


def test_iot_lab_ec_conflict():
    findings = detect_iot_lab_conflicts(
        sensor_ec=3.5,
        lab_ec=1.2,
        lab_confirmed=True,
    )
    codes = {f.code for f in findings}
    assert "iot_lab_ec_conflict" in codes
    assert "laboratuvar kimyasını değiştirmez" in findings[0].message


def test_iot_lab_no_conflict_unconfirmed():
    findings = detect_iot_lab_conflicts(
        sensor_ec=3.5,
        lab_ec=1.2,
        lab_confirmed=False,
    )
    assert findings == []


def test_water_usage_savings():
    report = compute_water_usage([180.0, 120.0])  # vs 45 min × 6 L/min baseline
    assert report.session_count == 2
    assert report.water_used_liters == 300.0
    assert report.baseline_liters == 540.0
    assert report.savings_liters == 240.0
    assert report.savings_pct == 44.4
