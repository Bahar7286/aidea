from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.anomaly_service import collect_farm_anomalies
from app.auth import get_current_user
from app.database import get_db
from app.deps import get_owned_farm
from app.models import (
    Crop,
    Device,
    Farm,
    IrrigationEvent,
    IrrigationStatus,
    LabReport,
    ManagementZone,
    Prediction,
    SensorReading,
    SourceType,
    User,
)
from app.schemas import (
    DataSourceOut,
    FarmCreate,
    FarmOut,
    FarmOverviewOut,
    FarmUpdate,
    PredictionOut,
    SensorReadingOut,
    TwinViewOut,
    TwinZoneOut,
)
from app.water_report import compute_water_usage

router = APIRouter(prefix="/farms", tags=["farms"])


def _farm_out(db: Session, farm: Farm) -> FarmOut:
    return FarmOut.model_validate(farm).model_copy(
        update={
            "zone_count": db.query(ManagementZone)
            .filter(ManagementZone.farm_id == farm.id)
            .count(),
            "device_count": db.query(Device).filter(Device.farm_id == farm.id).count(),
        }
    )


@router.post("", response_model=FarmOut, status_code=status.HTTP_201_CREATED)
def create_farm(
    payload: FarmCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    farm = Farm(
        user_id=current_user.id,
        name=payload.name,
        location=payload.location,
        latitude=payload.latitude,
        longitude=payload.longitude,
        area=payload.area,
        soil_type=payload.soil_type,
        irrigation_type=payload.irrigation_type,
        is_active=True,
    )
    db.add(farm)
    db.flush()
    if payload.crop_type:
        db.add(
            Crop(
                farm_id=farm.id,
                crop_type=payload.crop_type,
                growth_stage=payload.growth_stage,
            )
        )
    db.commit()
    db.refresh(farm)
    return _farm_out(db, farm)


@router.get("", response_model=list[FarmOut])
def list_farms(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    include_inactive: bool = False,
):
    q = db.query(Farm).filter(Farm.user_id == current_user.id)
    if not include_inactive:
        q = q.filter(Farm.is_active.is_(True))
    farms = q.order_by(Farm.created_at.desc()).all()
    return [_farm_out(db, f) for f in farms]


@router.get("/{farm_id}", response_model=FarmOut)
def get_farm(
    farm_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return _farm_out(db, get_owned_farm(db, farm_id, current_user))


@router.get("/{farm_id}/overview", response_model=FarmOverviewOut)
def farm_overview(
    farm_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    farm = get_owned_farm(db, farm_id, current_user)
    reading = (
        db.query(SensorReading)
        .filter(SensorReading.farm_id == farm_id)
        .order_by(SensorReading.timestamp.desc())
        .first()
    )
    prediction = (
        db.query(Prediction)
        .filter(Prediction.farm_id == farm_id)
        .order_by(Prediction.created_at.desc())
        .first()
    )
    zones = db.query(ManagementZone).filter(ManagementZone.farm_id == farm_id).all()
    anomalies = collect_farm_anomalies(db, farm_id)
    open_irr = (
        db.query(IrrigationEvent)
        .filter(
            IrrigationEvent.farm_id == farm_id,
            IrrigationEvent.status == IrrigationStatus.running,
        )
        .first()
        is not None
    )
    finished = (
        db.query(IrrigationEvent)
        .filter(
            IrrigationEvent.farm_id == farm_id,
            IrrigationEvent.status.in_(
                [IrrigationStatus.completed, IrrigationStatus.stopped]
            ),
        )
        .all()
    )
    water = compute_water_usage([e.water_amount for e in finished])
    return FarmOverviewOut(
        farm=_farm_out(db, farm),
        latest_reading=SensorReadingOut.model_validate(reading) if reading else None,
        latest_prediction=PredictionOut.model_validate(prediction) if prediction else None,
        zone_names=[z.name for z in zones],
        anomaly_count=len(anomalies),
        open_irrigation=open_irr,
        water_used_liters=water.water_used_liters if water.session_count else None,
        water_savings_liters=water.savings_liters if water.session_count else None,
        water_savings_pct=water.savings_pct,
        water_usage_note=water.note if water.session_count else None,
    )


def _zone_moisture(base: float | None, index: int) -> float | None:
    if base is None:
        return None
    return round(max(5.0, min(60.0, base + (index - 1) * 2.5)), 1)


@router.get("/{farm_id}/twin", response_model=TwinViewOut)
def farm_twin(
    farm_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    farm = get_owned_farm(db, farm_id, current_user)
    reading = (
        db.query(SensorReading)
        .filter(SensorReading.farm_id == farm_id)
        .order_by(SensorReading.timestamp.desc())
        .first()
    )
    prediction = (
        db.query(Prediction)
        .filter(Prediction.farm_id == farm_id)
        .order_by(Prediction.created_at.desc())
        .first()
    )
    zones = db.query(ManagementZone).filter(ManagementZone.farm_id == farm_id).all()
    names = [z.name for z in zones] or ["Kuzey", "Orta", "Güney"]
    twin_zones: list[TwinZoneOut] = []
    base = reading.soil_moisture if reading else None
    for i, name in enumerate(names[:5]):
        m = _zone_moisture(base, i)
        risk = "unknown"
        if m is not None:
            if m < 22:
                risk = "high"
            elif m < 28:
                risk = "medium"
            else:
                risk = "low"
        twin_zones.append(
            TwinZoneOut(
                id=zones[i].id if i < len(zones) else None,
                name=name,
                soil_moisture=m,
                soil_temperature=reading.soil_temperature if reading else None,
                air_temperature=reading.air_temperature if reading else None,
                air_humidity=reading.air_humidity if reading else None,
                ec=reading.ec if reading else None,
                risk=risk,
            )
        )

    insight = None
    if prediction:
        insight = prediction.explanation
    elif reading:
        insight = (
            f"Son ölçüm nem %{reading.soil_moisture}. "
            "Sınırlı dijital ikiz — uydu katmanı yok; bölge nemleri son okumadan türetilir."
        )
    else:
        insight = "Veri yok. Manuel giriş veya IoT simülasyonu ile haritayı doldurun."

    source = reading.source_type.value if reading and reading.source_type else None
    return TwinViewOut(
        farm=_farm_out(db, farm),
        zones=twin_zones,
        latest_reading=SensorReadingOut.model_validate(reading) if reading else None,
        latest_prediction=PredictionOut.model_validate(prediction) if prediction else None,
        source_label=source,
        confidence=reading.data_confidence if reading else None,
        insight=insight,
    )


@router.get("/{farm_id}/data-sources", response_model=list[DataSourceOut])
def farm_data_sources(
    farm_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    get_owned_farm(db, farm_id, current_user)
    sources: list[DataSourceOut] = []

    for st, label in [
        (SourceType.manual, "Manuel Veri"),
        (SourceType.simulation, "IoT Simülasyonu"),
        (SourceType.test_dataset, "Test Veri Seti"),
        (SourceType.iot, "Saha IoT"),
    ]:
        rows = (
            db.query(SensorReading)
            .filter(SensorReading.farm_id == farm_id, SensorReading.source_type == st)
            .order_by(SensorReading.timestamp.desc())
            .all()
        )
        last = rows[0] if rows else None
        avg_conf = None
        if rows:
            confs = [r.data_confidence for r in rows if r.data_confidence is not None]
            avg_conf = round(sum(confs) / len(confs), 1) if confs else None
        sources.append(
            DataSourceOut(
                key=st.value,
                name=label,
                source_type=st.value,
                status="active" if rows else "pending",
                last_update=last.timestamp if last else None,
                record_count=len(rows),
                trust_score=avg_conf,
                detail="Simülasyon — gerçek sensör değil"
                if st == SourceType.simulation
                else None,
            )
        )

    labs = (
        db.query(LabReport)
        .filter(LabReport.farm_id == farm_id)
        .order_by(LabReport.created_at.desc())
        .all()
    )
    sources.append(
        DataSourceOut(
            key="lab",
            name="Laboratuvar Analizleri",
            source_type="lab_manual",
            status="active" if labs else "pending",
            last_update=labs[0].created_at if labs else None,
            record_count=len(labs),
            trust_score=90.0 if labs else None,
            detail="Statik toprak profili — IoT’nin yerini almaz",
        )
    )

    devices = db.query(Device).filter(Device.farm_id == farm_id).all()
    last_dev = max((d.last_data_time for d in devices if d.last_data_time), default=None)
    sources.append(
        DataSourceOut(
            key="devices",
            name="Kayıtlı Cihazlar",
            source_type="iot",
            status="active" if devices else "offline",
            last_update=last_dev,
            record_count=len(devices),
            trust_score=None,
            detail=f"{len(devices)} cihaz",
        )
    )
    return sources


@router.put("/{farm_id}", response_model=FarmOut)
def update_farm(
    farm_id: int,
    payload: FarmUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Allow update on inactive farms so users can restore is_active.
    farm = get_owned_farm(db, farm_id, current_user)
    data = payload.model_dump(exclude_unset=True)
    crop_type = data.pop("crop_type", None)
    growth_stage = data.pop("growth_stage", None)
    for key, value in data.items():
        setattr(farm, key, value)
    if crop_type is not None or growth_stage is not None:
        crop = farm.crops[0] if farm.crops else None
        # Empty crop_type clears the primary crop (nested crop delete).
        if crop_type is not None and not str(crop_type).strip():
            if crop:
                db.delete(crop)
        elif crop:
            if crop_type is not None:
                crop.crop_type = crop_type
            if growth_stage is not None:
                crop.growth_stage = growth_stage
        elif crop_type:
            db.add(
                Crop(
                    farm_id=farm.id,
                    crop_type=crop_type,
                    growth_stage=growth_stage,
                )
            )
    db.commit()
    db.refresh(farm)
    return _farm_out(db, farm)


@router.delete("/{farm_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_farm(
    farm_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Soft-delete: marks farm inactive. Data preserved for history/admin."""
    farm = get_owned_farm(db, farm_id, current_user)
    farm.is_active = False
    db.commit()
    return None
