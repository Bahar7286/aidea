from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.ai_engine import RuleInput, predict_irrigation
from app.auth import get_current_user
from app.database import get_db
from app.deps import get_owned_farm
from app.models import SensorReading, User
from app.scenario_engine import (
    _daily_moisture_drop,
    _stress_from_risk,
    _water_liters,
    simulate_scenarios,
)
from app.schemas import (
    CustomSimulateOut,
    CustomSimulateRequest,
    ForecastPointOut,
    ScenarioCompareOut,
    ScenarioResultOut,
    ScenarioSimulateRequest,
)

router = APIRouter(tags=["scenarios"])


def _base_input(farm, reading: SensorReading) -> RuleInput:
    age_hours = (datetime.utcnow() - reading.timestamp).total_seconds() / 3600
    crop = farm.crops[0] if farm.crops else None
    return RuleInput(
        soil_moisture=reading.soil_moisture,
        air_temperature=reading.air_temperature,
        rainfall_probability=reading.rainfall_probability,
        last_irrigation_hours_ago=reading.last_irrigation_hours_ago,
        soil_type=farm.soil_type,
        crop_type=crop.crop_type if crop else None,
        growth_stage=crop.growth_stage if crop else None,
        data_confidence=reading.data_confidence,
        data_age_hours=age_hours,
    )


@router.post("/simulate/scenario", response_model=ScenarioCompareOut)
def compare_scenarios(
    payload: ScenarioSimulateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if len(payload.scenarios) < 2:
        raise HTTPException(
            status_code=400,
            detail="En az iki senaryo karşılaştırılmalıdır.",
        )

    farm = get_owned_farm(db, payload.farm_id, current_user, require_active=True)
    reading = (
        db.query(SensorReading)
        .filter(SensorReading.farm_id == farm.id)
        .order_by(SensorReading.timestamp.desc())
        .first()
    )
    if not reading:
        raise HTTPException(
            status_code=400,
            detail="Senaryo için önce sensör verisi girilmelidir.",
        )

    base = _base_input(farm, reading)
    recommended, outcomes = simulate_scenarios(
        base,
        list(payload.scenarios),
        duration_minutes=payload.duration_minutes,
        area=farm.area,
    )
    return ScenarioCompareOut(
        farm_id=farm.id,
        current_moisture=reading.soil_moisture,
        recommended_scenario=recommended,  # type: ignore[arg-type]
        results=[
            ScenarioResultOut(
                scenario=o.scenario,  # type: ignore[arg-type]
                label=o.label,
                estimated_moisture=o.estimated_moisture,
                estimated_water_liters=o.estimated_water_liters,
                risk_level=o.risk_level,  # type: ignore[arg-type]
                plant_stress=o.plant_stress,
                recommended=o.recommended,
                explanation=o.explanation,
            )
            for o in outcomes
        ],
    )


@router.post("/simulate/custom", response_model=CustomSimulateOut)
def custom_simulate(
    payload: CustomSimulateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Slider-based custom irrigation scenario for F28 simulator UI."""
    farm = get_owned_farm(db, payload.farm_id, current_user, require_active=True)
    reading = (
        db.query(SensorReading)
        .filter(SensorReading.farm_id == farm.id)
        .order_by(SensorReading.timestamp.desc())
        .first()
    )
    if not reading:
        raise HTTPException(
            status_code=400,
            detail="Senaryo için önce sensör verisi girilmelidir.",
        )

    base = _base_input(farm, reading)
    duration = payload.duration_minutes
    water = payload.water_amount_liters
    if water is None:
        water = _water_liters(duration, farm.area)

    moisture = min(100.0, reading.soil_moisture + duration * 1.2)
    if payload.target_moisture is not None:
        # Blend toward target for UI feel, still physics-bounded
        moisture = min(100.0, max(moisture, (moisture + payload.target_moisture) / 2))

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
    drop = _daily_moisture_drop(base)
    forecast: list[ForecastPointOut] = []
    for day in range(0, 6):
        current_path = max(0.0, reading.soil_moisture - drop * day)
        if day == 0:
            scenario_path = reading.soil_moisture
        else:
            scenario_path = max(0.0, moisture - drop * (day - 1) * 0.85)
        forecast.append(
            ForecastPointOut(
                day=day,
                current_path=round(current_path, 1),
                scenario_path=round(scenario_path, 1),
                critical_level=20.0,
            )
        )

    mm = round(water / max(farm.area or 1.0, 0.5) * 0.1, 1)
    cost = round(water * 0.045, 1)
    return CustomSimulateOut(
        farm_id=farm.id,
        name=payload.name,
        current_moisture=reading.soil_moisture,
        estimated_moisture=round(moisture, 1),
        estimated_water_liters=water,
        estimated_water_mm=mm,
        estimated_cost_try=cost,
        duration_minutes=duration,
        risk_level=projected.risk_level,  # type: ignore[arg-type]
        plant_stress=_stress_from_risk(projected.risk_level),
        forecast=forecast,
        explanation=(
            f"{duration:.0f} dk sulama → tahmini nem %{moisture:.0f}, "
            f"~{water:.0f} L. Simülasyon; gerçek vana değildir."
        ),
    )
