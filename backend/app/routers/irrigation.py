from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.ai_engine import RuleInput, predict_irrigation
from app.auth import get_current_user
from app.database import get_db
from app.deps import get_owned_farm
from app.models import (
    IrrigationEvent,
    IrrigationStatus,
    Prediction,
    RiskLevel,
    SensorReading,
    SourceType,
    User,
)
from app.schemas import (
    IrrigationEventOut,
    IrrigationStartOut,
    IrrigationStartRequest,
    IrrigationStopRequest,
    PredictionOut,
)
from app.validation import compute_data_confidence

router = APIRouter(prefix="/irrigation", tags=["irrigation"])

MIN_CONFIDENCE_FOR_AUTOMATION = 60.0


def _event_out(event: IrrigationEvent) -> IrrigationEventOut:
    valve = "açık" if event.status == IrrigationStatus.running else "kapalı"
    return IrrigationEventOut(
        id=event.id,
        farm_id=event.farm_id,
        start_time=event.start_time,
        end_time=event.end_time,
        duration=event.duration,
        water_amount=event.water_amount,
        status=event.status.value,
        valve_status=valve,
    )


def _latest_reading(db: Session, farm_id: int) -> SensorReading | None:
    return (
        db.query(SensorReading)
        .filter(SensorReading.farm_id == farm_id)
        .order_by(SensorReading.timestamp.desc())
        .first()
    )


def _run_prediction(db: Session, farm, reading: SensorReading) -> Prediction:
    age_hours = (datetime.utcnow() - reading.timestamp).total_seconds() / 3600
    crop = farm.crops[0] if farm.crops else None
    result = predict_irrigation(
        RuleInput(
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
    )
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
    db.flush()
    return prediction


@router.post("/start", response_model=IrrigationStartOut, status_code=status.HTTP_201_CREATED)
def start_irrigation(
    payload: IrrigationStartRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not payload.user_approved:
        raise HTTPException(
            status_code=400,
            detail="Sulama başlatmak için kullanıcı onayı (user_approved=true) zorunludur.",
        )

    farm = get_owned_farm(db, payload.farm_id, current_user, require_active=True)
    reading = _latest_reading(db, farm.id)
    if not reading:
        raise HTTPException(
            status_code=400,
            detail="Sulama için önce sensör verisi / AI analizi gerekir.",
        )

    # Use latest prediction confidence if available, else reading confidence
    latest_pred = (
        db.query(Prediction)
        .filter(Prediction.farm_id == farm.id)
        .order_by(Prediction.created_at.desc())
        .first()
    )
    confidence = (
        latest_pred.confidence_score
        if latest_pred
        else (reading.data_confidence or 0)
    )
    if confidence < MIN_CONFIDENCE_FOR_AUTOMATION:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Güven skoru %{confidence:.0f} — otomasyon için en az "
                f"%{MIN_CONFIDENCE_FOR_AUTOMATION:.0f} gerekir."
            ),
        )

    running = (
        db.query(IrrigationEvent)
        .filter(
            IrrigationEvent.farm_id == farm.id,
            IrrigationEvent.status == IrrigationStatus.running,
        )
        .first()
    )
    if running:
        raise HTTPException(
            status_code=400,
            detail="Bu arazi için zaten devam eden bir sulama var.",
        )

    duration = payload.duration_minutes
    if duration is None:
        duration = (
            latest_pred.irrigation_duration
            if latest_pred and latest_pred.irrigation_duration
            else 14.0
        )
    water = round(duration * 6.0, 1)

    if payload.virtual_session:
        event = IrrigationEvent(
            farm_id=farm.id,
            start_time=datetime.utcnow(),
            end_time=None,
            duration=duration,
            water_amount=water,
            status=IrrigationStatus.running,
        )
        db.add(event)
        if latest_pred:
            pred_out = PredictionOut.model_validate(latest_pred)
        else:
            prediction = _run_prediction(db, farm, reading)
            pred_out = PredictionOut.model_validate(prediction)
        db.commit()
        db.refresh(event)
        return IrrigationStartOut(
            event=_event_out(event),
            updated_moisture=reading.soil_moisture,
            prediction=pred_out,
            message=(
                f"Sanal sulama oturumu başladı (vana açık simülasyonu). "
                f"Süre {duration:.0f} dk. Durdurmak için stop kullanın."
            ),
        )

    new_moisture = min(100.0, reading.soil_moisture + duration * 1.2)

    event = IrrigationEvent(
        farm_id=farm.id,
        start_time=datetime.utcnow(),
        end_time=datetime.utcnow(),
        duration=duration,
        water_amount=water,
        status=IrrigationStatus.completed,
    )
    db.add(event)

    confidence_score, _ = compute_data_confidence(
        soil_moisture=new_moisture,
        air_temperature=reading.air_temperature,
        rainfall_probability=reading.rainfall_probability,
        last_irrigation_hours_ago=0,
        timestamp=datetime.utcnow(),
    )
    updated = SensorReading(
        farm_id=farm.id,
        source_type=SourceType.simulation,
        soil_moisture=round(new_moisture, 1),
        soil_temperature=reading.soil_temperature,
        air_temperature=reading.air_temperature,
        air_humidity=reading.air_humidity,
        rainfall_probability=reading.rainfall_probability,
        ph=reading.ph,
        ec=reading.ec,
        salinity=reading.salinity,
        last_irrigation_hours_ago=0,
        irrigation_duration=duration,
        water_amount=water,
        data_confidence=confidence_score,
    )
    db.add(updated)
    db.flush()

    prediction = _run_prediction(db, farm, updated)
    db.commit()
    db.refresh(event)
    db.refresh(prediction)

    return IrrigationStartOut(
        event=_event_out(event),
        updated_moisture=updated.soil_moisture,
        prediction=PredictionOut.model_validate(prediction),
        message=(
            f"Sanal sulama tamamlandı. Vana kapandı. "
            f"Nem %{reading.soil_moisture:.0f} → %{updated.soil_moisture:.0f}."
        ),
    )


@router.post("/stop", response_model=IrrigationEventOut)
def stop_irrigation(
    payload: IrrigationStopRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    farm = get_owned_farm(db, payload.farm_id, current_user, require_active=True)
    query = db.query(IrrigationEvent).filter(IrrigationEvent.farm_id == farm.id)
    if payload.event_id:
        event = query.filter(IrrigationEvent.id == payload.event_id).first()
    else:
        event = (
            query.filter(IrrigationEvent.status == IrrigationStatus.running)
            .order_by(IrrigationEvent.start_time.desc())
            .first()
        )
    if not event:
        raise HTTPException(status_code=404, detail="Durdurulacak sulama olayı bulunamadı.")

    if event.status == IrrigationStatus.stopped:
        return _event_out(event)

    was_running = event.status == IrrigationStatus.running
    event.status = IrrigationStatus.stopped
    event.end_time = datetime.utcnow()
    if event.start_time and event.end_time:
        elapsed = round(
            (event.end_time - event.start_time).total_seconds() / 60.0, 1
        )
        # Prefer planned duration for virtual sessions if stop is quick
        if event.duration and event.duration > elapsed:
            event.duration = event.duration
        else:
            event.duration = max(elapsed, 1.0)
    if was_running:
        reading = _latest_reading(db, farm.id)
        if reading and event.duration:
            new_moisture = min(100.0, reading.soil_moisture + event.duration * 1.2)
            water = event.water_amount or round(event.duration * 6.0, 1)
            confidence_score, _ = compute_data_confidence(
                soil_moisture=new_moisture,
                air_temperature=reading.air_temperature,
                rainfall_probability=reading.rainfall_probability,
                last_irrigation_hours_ago=0,
                timestamp=datetime.utcnow(),
            )
            db.add(
                SensorReading(
                    farm_id=farm.id,
                    source_type=SourceType.simulation,
                    soil_moisture=round(new_moisture, 1),
                    soil_temperature=reading.soil_temperature,
                    air_temperature=reading.air_temperature,
                    air_humidity=reading.air_humidity,
                    rainfall_probability=reading.rainfall_probability,
                    ph=reading.ph,
                    ec=reading.ec,
                    salinity=reading.salinity,
                    last_irrigation_hours_ago=0,
                    irrigation_duration=event.duration,
                    water_amount=water,
                    data_confidence=confidence_score,
                )
            )
            event.status = IrrigationStatus.completed
    db.commit()
    db.refresh(event)
    return _event_out(event)


@router.get("/status/{farm_id}")
def irrigation_status(
    farm_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    get_owned_farm(db, farm_id, current_user)
    running = (
        db.query(IrrigationEvent)
        .filter(
            IrrigationEvent.farm_id == farm_id,
            IrrigationEvent.status == IrrigationStatus.running,
        )
        .order_by(IrrigationEvent.start_time.desc())
        .first()
    )
    reading = _latest_reading(db, farm_id)
    latest_pred = (
        db.query(Prediction)
        .filter(Prediction.farm_id == farm_id)
        .order_by(Prediction.created_at.desc())
        .first()
    )
    confidence = (
        latest_pred.confidence_score
        if latest_pred
        else (reading.data_confidence if reading else 0) or 0
    )
    remaining_seconds: float | None = None
    planned_end: datetime | None = None
    if running and running.duration and running.start_time:
        from datetime import timedelta

        planned_end = running.start_time + timedelta(minutes=float(running.duration))
        remaining_seconds = max(
            0.0, (planned_end - datetime.utcnow()).total_seconds()
        )

    valve_open = bool(running)
    return {
        "farm_id": farm_id,
        "valve_status": "açık" if valve_open else "kapalı",
        "pump_status": "açık" if valve_open else "kapalı",
        "running": _event_out(running) if running else None,
        "remaining_seconds": remaining_seconds,
        "planned_end": planned_end.isoformat() + "Z" if planned_end else None,
        "current_moisture": reading.soil_moisture if reading else None,
        "confidence_score": confidence,
        "automation_allowed": bool(
            latest_pred
            and latest_pred.irrigation_needed
            and confidence >= MIN_CONFIDENCE_FOR_AUTOMATION
        ),
        "message": (
            "Sanal pompa/vana açık — oturum çalışıyor."
            if running
            else "Sulama sistemi beklemede (simülasyon)."
        ),
    }


@router.get("/history/{farm_id}", response_model=list[IrrigationEventOut])
def irrigation_history(
    farm_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    get_owned_farm(db, farm_id, current_user)
    rows = (
        db.query(IrrigationEvent)
        .filter(IrrigationEvent.farm_id == farm_id)
        .order_by(IrrigationEvent.start_time.desc())
        .limit(50)
        .all()
    )
    return [_event_out(r) for r in rows]
