from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app.ai_engine import RuleInput, predict_irrigation


def test_drought_demo_recommends_irrigation():
    result = predict_irrigation(
        RuleInput(
            soil_moisture=28,
            air_temperature=33,
            rainfall_probability=5,
            last_irrigation_hours_ago=36,
            data_confidence=90,
        )
    )
    assert result.irrigation_needed is True
    assert result.risk_level in {"high", "critical"}
    assert result.confidence_score >= 60
    assert "Sulama" in result.explanation


def test_high_moisture_over_irrigation_risk():
    result = predict_irrigation(
        RuleInput(
            soil_moisture=78,
            air_temperature=24,
            rainfall_probability=40,
            last_irrigation_hours_ago=4,
        )
    )
    assert result.irrigation_needed is False
    assert result.risk_level == "high"
