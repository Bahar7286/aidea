from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.database import get_db
from app.deps import get_owned_farm
from app.models import Device, SensorReading, SourceType, User
from app.schemas import (
    DeviceCalibrateOut,
    DeviceCalibrateRequest,
    DeviceCreate,
    DeviceDetailOut,
    DeviceOut,
    DeviceSummaryOut,
    DeviceTestOut,
    DeviceTestRequest,
    DeviceUpdate,
    IoTIngestRequest,
    IoTSimulateRequest,
    SensorReadingOut,
)
from app.validation import compute_data_confidence

router = APIRouter(tags=["devices-iot"])

CALIBRATION_DUE_DAYS = 90


def _calibration_due(device: Device) -> bool:
    if device.last_calibration_at is None:
        return True
    return device.last_calibration_at < datetime.utcnow() - timedelta(days=CALIBRATION_DUE_DAYS)


def _last_moisture(db: Session, device_id: int) -> float | None:
    reading = (
        db.query(SensorReading)
        .filter(SensorReading.device_id == device_id)
        .order_by(SensorReading.timestamp.desc())
        .first()
    )
    return reading.soil_moisture if reading else None


def _device_out(db: Session, device: Device) -> DeviceOut:
    data = DeviceOut.model_validate(device)
    data.last_moisture = _last_moisture(db, device.id)
    data.calibration_due = _calibration_due(device)
    data.source_label = "simulation"
    return data


def _normalize_status(raw: str | None) -> str:
    if not raw:
        return "active"
    s = raw.lower().strip()
    if s in {"active", "online", "aktif", "normal"}:
        return "active"
    if s in {"warning", "uyari", "uyarı", "alert"}:
        return "warning"
    if s in {"offline", "cevrimdisi", "çevrimdışı", "inactive"}:
        return "offline"
    return s


@router.post("/devices", response_model=DeviceOut, status_code=status.HTTP_201_CREATED)
def create_device(
    payload: DeviceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    get_owned_farm(db, payload.farm_id, current_user, require_active=True)
    existing = (
        db.query(Device)
        .filter(
            Device.farm_id == payload.farm_id,
            Device.device_name == payload.device_name,
        )
        .first()
    )
    if existing:
        raise HTTPException(
            status_code=400,
            detail="Bu arazi için aynı isimde cihaz zaten kayıtlı.",
        )
    now = datetime.utcnow()
    device = Device(
        farm_id=payload.farm_id,
        device_name=payload.device_name,
        device_type=payload.device_type,
        connection_status="active",
        serial_number=payload.serial_number,
        zone_id=payload.zone_id,
        region_name=payload.region_name,
        depth_cm=payload.depth_cm or 20,
        connection_type=(payload.connection_type or "wifi").lower(),
        battery_percent=100.0,
        signal_dbm=-70,
        firmware_version="1.0.0-sim",
        installed_at=now,
        calibration_offset=0.0,
        sampling_minutes=payload.sampling_minutes or 15,
        notes=payload.notes,
        last_data_time=None,
    )
    db.add(device)
    db.commit()
    db.refresh(device)
    return _device_out(db, device)


@router.get("/devices/detail/{device_id}", response_model=DeviceDetailOut)
def get_device_detail(
    device_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    device = db.query(Device).filter(Device.id == device_id).first()
    if not device:
        raise HTTPException(status_code=404, detail="Cihaz bulunamadı.")
    get_owned_farm(db, device.farm_id, current_user)
    readings = (
        db.query(SensorReading)
        .filter(SensorReading.device_id == device.id)
        .order_by(SensorReading.timestamp.desc())
        .limit(48)
        .all()
    )
    events: list[str] = []
    if device.last_data_time:
        events.append(f"Son veri: {device.last_data_time.isoformat()}Z")
    if device.last_calibration_at:
        events.append(f"Son kalibrasyon: {device.last_calibration_at.isoformat()}Z")
    elif device.installed_at:
        events.append("Kalibrasyon henüz yapılmadı")
    if _calibration_due(device):
        events.append("Kalibrasyon süresi yaklaşıyor / geçmiş")
    if _normalize_status(device.connection_status) == "warning":
        events.append("Uyarı: anormal sinyal veya pil")
    if not events:
        events.append("Henüz olay kaydı yok")
    return DeviceDetailOut(
        device=_device_out(db, device),
        recent_readings=[SensorReadingOut.model_validate(r) for r in readings],
        events=events,
    )


@router.put("/devices/detail/{device_id}", response_model=DeviceOut)
def update_device(
    device_id: int,
    payload: DeviceUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    device = db.query(Device).filter(Device.id == device_id).first()
    if not device:
        raise HTTPException(status_code=404, detail="Cihaz bulunamadı.")
    get_owned_farm(db, device.farm_id, current_user, require_active=True)
    data = payload.model_dump(exclude_unset=True)
    if "connection_status" in data and data["connection_status"]:
        data["connection_status"] = _normalize_status(data["connection_status"])
    if "connection_type" in data and data["connection_type"]:
        data["connection_type"] = data["connection_type"].lower()
    for key, value in data.items():
        setattr(device, key, value)
    db.commit()
    db.refresh(device)
    return _device_out(db, device)


@router.delete("/devices/detail/{device_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_device(
    device_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    device = db.query(Device).filter(Device.id == device_id).first()
    if not device:
        raise HTTPException(status_code=404, detail="Cihaz bulunamadı.")
    get_owned_farm(db, device.farm_id, current_user, require_active=True)
    # Keep sensor history; only detach device FK.
    db.query(SensorReading).filter(SensorReading.device_id == device.id).update(
        {"device_id": None}
    )
    db.delete(device)
    db.commit()
    return None


@router.post("/devices/detail/{device_id}/calibrate", response_model=DeviceCalibrateOut)
def calibrate_device(
    device_id: int,
    payload: DeviceCalibrateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    device = db.query(Device).filter(Device.id == device_id).first()
    if not device:
        raise HTTPException(status_code=404, detail="Cihaz bulunamadı.")
    get_owned_farm(db, device.farm_id, current_user, require_active=True)

    raw = payload.raw_value
    if raw is None:
        last = _last_moisture(db, device.id)
        if last is None:
            raise HTTPException(
                status_code=400,
                detail="Ham ölçüm yok. Önce simülasyon/ingest çalıştırın veya raw_value girin.",
            )
        raw = float(last)

    deviation = round(raw - payload.reference_value, 2)
    offset = round(payload.reference_value - raw, 3)
    abs_dev = abs(deviation)
    if abs_dev <= 0.5:
        cal_status = "good"
    elif abs_dev <= 2.0:
        cal_status = "ok"
    else:
        cal_status = "needs_attention"

    now = datetime.utcnow()
    device.calibration_offset = offset
    device.last_calibration_at = now
    db.commit()
    db.refresh(device)

    return DeviceCalibrateOut(
        device_id=device.id,
        raw_value=raw,
        reference_value=payload.reference_value,
        deviation=deviation,
        status=cal_status,
        calibration_offset=offset,
        last_calibration_at=now,
        message="Kalibrasyon kaydedildi (MVP yazılım ofseti; simülasyon cihazı).",
    )


@router.get("/devices/{farm_id}/summary", response_model=DeviceSummaryOut)
def device_summary(
    farm_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    get_owned_farm(db, farm_id, current_user)
    rows = db.query(Device).filter(Device.farm_id == farm_id).all()
    total = len(rows)
    online = sum(1 for d in rows if _normalize_status(d.connection_status) == "active")
    warning = sum(1 for d in rows if _normalize_status(d.connection_status) == "warning")
    offline = sum(1 for d in rows if _normalize_status(d.connection_status) == "offline")
    known = online + warning + offline
    if known < total:
        offline += total - known
    calibration_pending = sum(1 for d in rows if _calibration_due(d))
    pct = round((online / total) * 100, 1) if total else 0.0
    return DeviceSummaryOut(
        farm_id=farm_id,
        total=total,
        online=online,
        warning=warning,
        offline=offline,
        calibration_pending=calibration_pending,
        online_percent=pct,
    )


@router.get("/devices/{farm_id}", response_model=list[DeviceOut])
def list_devices(
    farm_id: int,
    status_filter: str | None = Query(default=None, alias="status"),
    device_type: str | None = None,
    q: str | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    get_owned_farm(db, farm_id, current_user)
    rows = db.query(Device).filter(Device.farm_id == farm_id).order_by(Device.id.asc()).all()
    out = [_device_out(db, d) for d in rows]
    if status_filter and status_filter.lower() not in {"all", "tumu", "tümü"}:
        wanted = _normalize_status(status_filter)
        out = [d for d in out if _normalize_status(d.connection_status) == wanted]
    if device_type:
        out = [d for d in out if d.device_type == device_type]
    if q:
        needle = q.lower().strip()
        out = [
            d
            for d in out
            if needle in d.device_name.lower()
            or (d.serial_number and needle in d.serial_number.lower())
            or (d.region_name and needle in d.region_name.lower())
        ]
    return out


@router.post("/devices/test-connection", response_model=DeviceTestOut)
def test_connection(
    payload: DeviceTestRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    device = db.query(Device).filter(Device.id == payload.device_id).first()
    if not device:
        raise HTTPException(status_code=404, detail="Cihaz bulunamadı.")
    get_owned_farm(db, device.farm_id, current_user, require_active=True)

    device.connection_status = "active"
    device.last_data_time = datetime.utcnow()
    device.signal_dbm = -62
    if device.battery_percent is None:
        device.battery_percent = 92.0
    db.commit()
    db.refresh(device)
    return DeviceTestOut(
        device_id=device.id,
        connection_status=device.connection_status,
        message="Bağlantı testi başarılı (IoT simülasyonu).",
        last_data_time=device.last_data_time,
        signal_dbm=device.signal_dbm,
        battery_percent=device.battery_percent,
    )


@router.post("/iot/simulate", response_model=SensorReadingOut, status_code=201)
def iot_simulate(
    payload: IoTSimulateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    farm = get_owned_farm(db, payload.farm_id, current_user, require_active=True)
    from app.datasets_path import list_scenario_metas, load_scenario

    try:
        scenario = load_scenario(payload.scenario)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    _ = list_scenario_metas  # kept for parity / debugging imports
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
        source_type=SourceType.simulation,
        soil_moisture=float(reading_data["soil_moisture"]),
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
    )
    db.add(reading)

    device = None
    if payload.device_id:
        device = (
            db.query(Device)
            .filter(Device.id == payload.device_id, Device.farm_id == farm.id)
            .first()
        )
        if not device:
            raise HTTPException(status_code=404, detail="Cihaz bulunamadı.")
    else:
        device = (
            db.query(Device)
            .filter(Device.farm_id == farm.id)
            .order_by(Device.id.asc())
            .first()
        )
        if not device:
            device = Device(
                farm_id=farm.id,
                device_name="Nem Sensörü 01",
                device_type="soil_moisture",
                connection_status="active",
                serial_number="SIM-AUTO-01",
                depth_cm=20,
                connection_type="wifi",
                battery_percent=88.0,
                signal_dbm=-68,
                firmware_version="1.0.0-sim",
                installed_at=datetime.utcnow(),
                calibration_offset=0.0,
                sampling_minutes=15,
            )
            db.add(device)
            db.flush()

    # Apply calibration offset for displayed moisture when set
    offset = device.calibration_offset or 0.0
    if offset:
        reading.soil_moisture = max(0.0, min(100.0, reading.soil_moisture + offset))

    device.connection_status = "active"
    device.last_data_time = datetime.utcnow()
    if device.battery_percent is not None and device.battery_percent > 1:
        device.battery_percent = max(1.0, device.battery_percent - 0.1)
    device.signal_dbm = device.signal_dbm or -65
    reading.device_id = device.id
    db.commit()
    db.refresh(reading)
    return SensorReadingOut.model_validate(reading)


def _meas(measurements: dict, *keys: str) -> float | None:
    for key in keys:
        item = measurements.get(key)
        if item is not None:
            return float(item.value)
    return None


@router.post("/iot/ingest", response_model=SensorReadingOut, status_code=201)
def iot_ingest(
    payload: IoTIngestRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Field Node Lite JSON ingest (Wi-Fi HTTPS). simulation=true → source_type simulation."""
    farm = get_owned_farm(db, payload.farm_id, current_user, require_active=True)
    m = payload.measurements
    moisture = _meas(m, "soil_moisture_20cm", "soil_moisture", "soil_moisture_shallow")
    if moisture is None:
        raise HTTPException(
            status_code=400,
            detail="measurements içinde soil_moisture_20cm (veya soil_moisture) zorunlu.",
        )
    moisture_deep = _meas(m, "soil_moisture_40cm", "soil_moisture_deep")
    soil_temp = _meas(m, "soil_temperature")
    air_temp = _meas(m, "air_temperature")
    air_hum = _meas(m, "air_humidity")
    ec = _meas(m, "ec", "soil_ec")

    source = SourceType.simulation if payload.simulation else SourceType.iot
    confidence, _ = compute_data_confidence(
        soil_moisture=moisture,
        air_temperature=air_temp,
        rainfall_probability=None,
        last_irrigation_hours_ago=None,
        timestamp=payload.timestamp or datetime.utcnow(),
    )
    # Basic physical-range gate → is_validated
    is_validated = 0 <= moisture <= 100
    if moisture_deep is not None and not (0 <= moisture_deep <= 100):
        is_validated = False
    if air_hum is not None and not (0 <= air_hum <= 100):
        is_validated = False

    device = (
        db.query(Device)
        .filter(
            Device.farm_id == farm.id,
            Device.device_name == payload.device_id,
        )
        .first()
    )
    if not device:
        device = Device(
            farm_id=farm.id,
            device_name=payload.device_id,
            device_type="field_node",
            connection_status="active",
            depth_cm=20,
            connection_type="wifi",
            battery_percent=95.0,
            signal_dbm=-67,
            firmware_version="1.0.0-sim",
            installed_at=datetime.utcnow(),
            calibration_offset=0.0,
            sampling_minutes=15,
        )
        db.add(device)
        db.flush()

    offset = device.calibration_offset or 0.0
    if offset:
        moisture = max(0.0, min(100.0, moisture + offset))

    reading = SensorReading(
        farm_id=farm.id,
        zone_id=payload.zone_id,
        source_type=source,
        timestamp=payload.timestamp or datetime.utcnow(),
        soil_moisture=moisture,
        soil_moisture_deep=moisture_deep,
        moisture_depth_cm=20.0,
        moisture_deep_depth_cm=40.0 if moisture_deep is not None else None,
        soil_temperature=soil_temp,
        air_temperature=air_temp,
        air_humidity=air_hum,
        ec=ec,
        data_confidence=confidence,
        is_validated=is_validated,
        device_id=device.id,
    )
    db.add(reading)
    device.connection_status = (
        "active" if payload.status == "normal" else _normalize_status(payload.status)
    )
    device.last_data_time = reading.timestamp
    db.commit()
    db.refresh(reading)
    return SensorReadingOut.model_validate(reading)
