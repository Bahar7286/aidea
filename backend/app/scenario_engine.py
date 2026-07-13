"""Scenario comparison helpers built on the rule engine."""

from __future__ import annotations

from dataclasses import dataclass

from app.ai_engine import RuleInput, _daily_moisture_drop, predict_irrigation


SCENARIO_LABELS = {
    "irrigate_now": "Şimdi sulama",
    "wait_12h": "12 saat sonra sulama",
    "wait_24h": "24 saat sonra sulama",
    "skip": "Sulama yapmama",
    "reduce_duration": "Sulama süresini azaltma",
    "increase_duration": "Sulama süresini artırma",
}


@dataclass
class ScenarioOutcome:
    scenario: str
    label: str
    estimated_moisture: float
    estimated_water_liters: float | None
    risk_level: str
    plant_stress: str
    recommended: bool
    explanation: str


def _stress_from_risk(risk: str) -> str:
    return {
        "low": "düşük",
        "medium": "orta",
        "high": "yüksek",
        "critical": "kritik",
    }.get(risk, "orta")


def _water_liters(duration_min: float, area_da: float | None = None) -> float:
    # Simple MVP estimate: ~6 L/min baseline, scale lightly by area
    factor = 1.0 + max(0.0, (area_da or 1.0) - 1.0) * 0.15
    return round(duration_min * 6.0 * factor, 1)


def simulate_scenarios(
    base: RuleInput,
    scenarios: list[str],
    *,
    duration_minutes: float | None = None,
    area: float | None = None,
) -> tuple[str, list[ScenarioOutcome]]:
    drop = _daily_moisture_drop(base)
    base_result = predict_irrigation(base)
    default_duration = duration_minutes or base_result.irrigation_duration or 14.0

    outcomes: list[ScenarioOutcome] = []

    for name in scenarios:
        if name == "irrigate_now":
            duration = default_duration
            moisture = min(100.0, base.soil_moisture + duration * 1.2)
            water = _water_liters(duration, area)
            projected = predict_irrigation(
                RuleInput(
                    soil_moisture=moisture,
                    air_temperature=base.air_temperature,
                    rainfall_probability=base.rainfall_probability,
                    last_irrigation_hours_ago=0,
                    soil_type=base.soil_type,
                    crop_type=base.crop_type,
                    growth_stage=base.growth_stage,
                    data_confidence=base.data_confidence,
                )
            )
            explanation = (
                f"Şimdi {duration:.0f} dk sulama sonrası tahmini nem %{moisture:.0f}."
            )
        elif name == "wait_12h":
            moisture = max(0.0, base.soil_moisture - drop * 0.5)
            water = None
            projected = predict_irrigation(
                RuleInput(
                    soil_moisture=moisture,
                    air_temperature=base.air_temperature,
                    rainfall_probability=base.rainfall_probability,
                    last_irrigation_hours_ago=(base.last_irrigation_hours_ago or 24) + 12,
                    soil_type=base.soil_type,
                    crop_type=base.crop_type,
                    growth_stage=base.growth_stage,
                    data_confidence=base.data_confidence,
                )
            )
            explanation = f"12 saat beklenirse tahmini nem %{moisture:.0f}."
        elif name == "wait_24h":
            moisture = max(0.0, base.soil_moisture - drop)
            water = None
            projected = predict_irrigation(
                RuleInput(
                    soil_moisture=moisture,
                    air_temperature=base.air_temperature,
                    rainfall_probability=base.rainfall_probability,
                    last_irrigation_hours_ago=(base.last_irrigation_hours_ago or 24) + 24,
                    soil_type=base.soil_type,
                    crop_type=base.crop_type,
                    growth_stage=base.growth_stage,
                    data_confidence=base.data_confidence,
                )
            )
            explanation = f"24 saat beklenirse tahmini nem %{moisture:.0f}."
        elif name == "skip":
            moisture = max(0.0, base.soil_moisture - drop * 3)
            water = 0.0
            projected = predict_irrigation(
                RuleInput(
                    soil_moisture=moisture,
                    air_temperature=base.air_temperature,
                    rainfall_probability=base.rainfall_probability,
                    last_irrigation_hours_ago=(base.last_irrigation_hours_ago or 24) + 72,
                    soil_type=base.soil_type,
                    crop_type=base.crop_type,
                    growth_stage=base.growth_stage,
                    data_confidence=base.data_confidence,
                )
            )
            explanation = f"Sulama yapılmazsa 72 saatte tahmini nem %{moisture:.0f}."
        elif name == "reduce_duration":
            duration = max(5.0, default_duration * 0.7)
            moisture = min(100.0, base.soil_moisture + duration * 1.2)
            water = _water_liters(duration, area)
            projected = predict_irrigation(
                RuleInput(
                    soil_moisture=moisture,
                    air_temperature=base.air_temperature,
                    rainfall_probability=base.rainfall_probability,
                    last_irrigation_hours_ago=0,
                    soil_type=base.soil_type,
                    crop_type=base.crop_type,
                    growth_stage=base.growth_stage,
                    data_confidence=base.data_confidence,
                )
            )
            explanation = (
                f"Süre {duration:.0f} dk'ya indirilirse tahmini nem %{moisture:.0f}."
            )
        elif name == "increase_duration":
            duration = min(60.0, default_duration * 1.3)
            moisture = min(100.0, base.soil_moisture + duration * 1.2)
            water = _water_liters(duration, area)
            projected = predict_irrigation(
                RuleInput(
                    soil_moisture=moisture,
                    air_temperature=base.air_temperature,
                    rainfall_probability=base.rainfall_probability,
                    last_irrigation_hours_ago=0,
                    soil_type=base.soil_type,
                    crop_type=base.crop_type,
                    growth_stage=base.growth_stage,
                    data_confidence=base.data_confidence,
                )
            )
            explanation = (
                f"Süre {duration:.0f} dk'ya çıkarılırsa tahmini nem %{moisture:.0f}."
            )
        else:
            continue

        outcomes.append(
            ScenarioOutcome(
                scenario=name,
                label=SCENARIO_LABELS.get(name, name),
                estimated_moisture=round(moisture, 1),
                estimated_water_liters=water,
                risk_level=projected.risk_level,
                plant_stress=_stress_from_risk(projected.risk_level),
                recommended=False,
                explanation=explanation,
            )
        )

    # Recommend lowest risk among irrigate options; prefer irrigate_now if tied and needed
    risk_rank = {"low": 0, "medium": 1, "high": 2, "critical": 3}
    if outcomes:
        best = min(
            outcomes,
            key=lambda o: (
                risk_rank.get(o.risk_level, 9),
                0 if o.scenario == "irrigate_now" and base_result.irrigation_needed else 1,
                o.estimated_water_liters if o.estimated_water_liters is not None else 9999,
            ),
        )
        for o in outcomes:
            o.recommended = o.scenario == best.scenario
        recommended = best.scenario
    else:
        recommended = "irrigate_now"

    return recommended, outcomes
