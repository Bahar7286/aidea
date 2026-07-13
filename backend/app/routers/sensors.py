import json
from datetime import datetime
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.ai_engine import RuleInput, predict_irrigation
from app.llm_explain import enrich_explanation
from app.auth import get_current_user
from app.database import get_db
from app.deps import get_owned_farm
from app.models import Prediction, RiskLevel, SensorReading, SourceType, User
from app.schemas import (
    DatasetInfoOut,
    DatasetLoadRequest,
    PredictionOut,
    SensorReadingCreate,
    SensorReadingOut,
)
from app.validation import compute_data_confidence

router = APIRouter(tags=["data"])

DATASETS_DIR = Path(__file__).resolve().parents[3] / "ai" / "datasets"


def _load_scenario_file(scenario: str) -> dict:
    path = DATASETS_DIR / f"{scenario}.json"
    if not path.exists():
        available = sorted(p.stem for p in DATASETS_DIR.glob("*.json"))
        raise HTTPException(
            status_code=400,
            detail=f"Senaryo bulunamadı: {scenario}. Mevcut: {', '.join(available)}",
        )
    with path.open(encoding="utf-8") as f:
        return json.load(f)


@router.get("/datasets", response_model=list[DatasetInfoOut])
def list_datasets(current_user: User = Depends(get_current_user)):
    """List fixed MVP test scenarios under ai/datasets/."""
    _ = current_user
    items: list[DatasetInfoOut] = []
    for path in sorted(DATASETS_DIR.glob("*.json")):
        try:
            with path.open(encoding="utf-8") as f:
                meta = json.load(f)
        except (OSError, json.JSONDecodeError):
            meta = {}
        items.append(
            DatasetInfoOut(
                id=path.stem,
                name=str(meta.get("name") or path.stem),
                description=meta.get("description"),
            )
        )
    return items


@router.post("/datasets/load", response_model=SensorReadingOut, status_code=201)
def load_dataset(
    payload: DatasetLoadRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Load a fixed test scenario as source_type=test_dataset (not simulation)."""
    farm = get_owned_farm(db, payload.farm_id, current_user, require_active=True)
    scenario = _load_scenario_file(payload.scenario)
    reading_data = scenario.get("reading") or {}
    if "soil_moisture" not in reading_data:
        raise HTTPException(status_code=400, detail="Senaryo okuma verisi eksik.")

    confidence, _ = compute_data_confidence(
        soil_moisture=float(reading_data["soil_moisture"]),
        air_temperature=reading_data.get("air_temperature"),
        rainfall_probability=reading_data.get("rainfall_probability"),
        last_irrigation_hours_ago=reading_data.get("last_irrigation_hours_ago"),
        timestamp=datetime.utcnow(),
    )
    reading = SensorReading(
        farm_id=farm.id,
        zone_id=payload.zone_id,
        source_type=SourceType.test_dataset,
        soil_moisture=float(reading_data["soil_moisture"]),
        soil_moisture_deep=reading_data.get("soil_moisture_deep"),
        soil_temperature=reading_data.get("soil_temperature"),
        air_temperature=reading_data.get("air_temperature"),
        air_humidity=reading_data.get("air_humidity"),
        rainfall_probability=reading_data.get("rainfall_probability"),
        ph=reading_data.get("ph"),
        ec=reading_data.get("ec"),
        salinity=reading_data.get("salinity"),
        last_irrigation_hours_ago=reading_data.get("last_irrigation_hours_ago"),
        irrigation_duration=reading_data.get("irrigation_duration"),
        water_amount=reading_data.get("water_amount"),
        data_confidence=confidence,
        is_validated=True,
    )
    db.add(reading)
    db.commit()
    db.refresh(reading)
    return SensorReadingOut.model_validate(reading)


@router.post("/sensor-readings/{farm_id}", response_model=SensorReadingOut, status_code=201)
def create_reading(
    farm_id: int,
    payload: SensorReadingCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    farm = get_owned_farm(db, farm_id, current_user, require_active=True)
    confidence, _ = compute_data_confidence(
        soil_moisture=payload.soil_moisture,
        air_temperature=payload.air_temperature,
        rainfall_probability=payload.rainfall_probability,
        last_irrigation_hours_ago=payload.last_irrigation_hours_ago,
        timestamp=datetime.utcnow(),
    )
    reading = SensorReading(
        farm_id=farm.id,
        zone_id=payload.zone_id,
        source_type=SourceType(payload.source_type),
        soil_moisture=payload.soil_moisture,
        soil_moisture_deep=payload.soil_moisture_deep,
        moisture_depth_cm=payload.moisture_depth_cm,
        moisture_deep_depth_cm=payload.moisture_deep_depth_cm,
        soil_temperature=payload.soil_temperature,
        air_temperature=payload.air_temperature,
        air_humidity=payload.air_humidity,
        rainfall_probability=payload.rainfall_probability,
        ph=payload.ph,
        ec=payload.ec,
        salinity=payload.salinity,
        last_irrigation_hours_ago=payload.last_irrigation_hours_ago,
        irrigation_duration=payload.irrigation_duration,
        water_amount=payload.water_amount,
        data_confidence=confidence,
        is_validated=True,
    )
    db.add(reading)
    db.commit()
    db.refresh(reading)
    return SensorReadingOut.model_validate(reading)


@router.get("/sensor-readings/{farm_id}", response_model=list[SensorReadingOut])
def list_readings(
    farm_id: int,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    get_owned_farm(db, farm_id, current_user)
    cap = max(1, min(limit, 200))
    rows = (
        db.query(SensorReading)
        .filter(SensorReading.farm_id == farm_id)
        .order_by(SensorReading.timestamp.desc())
        .limit(cap)
        .all()
    )
    return [SensorReadingOut.model_validate(r) for r in rows]


@router.post("/predict/irrigation", response_model=PredictionOut)
def predict(
    farm_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Query param: farm_id — runs rule-based irrigation prediction."""
    farm = get_owned_farm(db, farm_id, current_user, require_active=True)
    reading = (
        db.query(SensorReading)
        .filter(SensorReading.farm_id == farm_id)
        .order_by(SensorReading.timestamp.desc())
        .first()
    )
    if not reading:
        raise HTTPException(
            status_code=400,
            detail="Tahmin için önce sensör verisi girilmelidir.",
        )

    age_hours = (datetime.utcnow() - reading.timestamp).total_seconds() / 3600
    crop = farm.crops[0] if farm.crops else None
    rule_inp = RuleInput(
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
    result = enrich_explanation(rule_inp, predict_irrigation(rule_inp))
    prediction = Prediction(
        farm_id=farm.id,
        irrigation_needed=result.irrigation_needed,
        irrigation_duration=result.irrigation_duration,
        risk_level=RiskLevel(result.risk_level),
        confidence_score=result.confidence_score,
        explanation=result.explanation,
        moisture_24h=result.moisture_24h,
        moisture_48h=result.moisture_48h,
        moisture_72h=result.moisture_72h,
    )
    db.add(prediction)
    db.commit()
    db.refresh(prediction)
    return PredictionOut.model_validate(prediction)


@router.get("/predictions/{farm_id}", response_model=list[PredictionOut])
def list_predictions(
    farm_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    get_owned_farm(db, farm_id, current_user)
    rows = (
        db.query(Prediction)
        .filter(Prediction.farm_id == farm_id)
        .order_by(Prediction.created_at.desc())
        .limit(20)
        .all()
    )
    return [PredictionOut.model_validate(r) for r in rows]
