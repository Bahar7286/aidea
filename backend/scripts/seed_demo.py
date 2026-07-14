"""Seed distinct demo personas + farms for jüri/demo.

Run from backend/:
  .venv\\Scripts\\python.exe -m scripts.seed_demo

Also used by app.demo_bootstrap (startup + POST /auth/demo-login).
"""

from __future__ import annotations

import sys
from datetime import datetime, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app.auth import hash_password
from app.database import Base, SessionLocal, engine
from app.agro_catalog import ensure_agro_catalog
from app.db_migrate import ensure_sqlite_columns
from app.materials_service import sync_farm_materials
from app.models import (
    AgroMaterial,
    Crop,
    CropHistory,
    CropSeasonStatus,
    Device,
    Farm,
    FarmMaterialUse,
    IrrigationEvent,
    IrrigationStatus,
    LabParameter,
    LabReport,
    LabSourceType,
    ManagementZone,
    Prediction,
    RiskLevel,
    SensorReading,
    SourceType,
    SupportTicket,
    User,
)

DEMO_PASSWORD = "Secret12"

# Keep this list the source of truth for demo personas.
DEMO_USERS = [
    {
        "email": "admin@agritwin.demo",
        "name": "Ayşe Demir",
        "role": "admin",
        "phone": "5551000001",
        "purpose": "Yönetim paneli (/admin) — kullanıcı, filo, destek, ayarlar",
        "seed_profile": "admin",
    },
    {
        "email": "ciftci@agritwin.demo",
        "name": "Mehmet Yılmaz",
        "role": "farmer",
        "phone": "5551000002",
        "purpose": "Ana demo: Domates Serası — kuruyan nem + sulama geçmişi",
        "seed_profile": "farmer",
    },
    {
        "email": "ziraat@agritwin.demo",
        "name": "Elif Kaya",
        "role": "agronomist",
        "phone": "5551000003",
        "purpose": "Konya buğday danışmanı — kumlu tarla, manuel + simülasyon",
        "seed_profile": "agronomist",
    },
    {
        "email": "kooperatif@agritwin.demo",
        "name": "Yeşilova Kooperatifi",
        "role": "cooperative",
        "phone": "5551000004",
        "purpose": "Çok bölgeli kooperatif — 2 arazi, farklı nem rejimleri",
        "seed_profile": "cooperative",
    },
]


def upsert_user(db, spec: dict) -> User:
    user = db.query(User).filter(User.email == spec["email"]).first()
    if user:
        user.name = spec["name"]
        user.role = spec["role"]
        user.phone = spec.get("phone")
        user.password_hash = hash_password(DEMO_PASSWORD)
        user.email_verified = True
        user.is_active = True
        return user
    user = User(
        name=spec["name"],
        email=spec["email"],
        phone=spec.get("phone"),
        password_hash=hash_password(DEMO_PASSWORD),
        role=spec["role"],
        email_verified=True,
        is_active=True,
        last_login_at=None,
    )
    db.add(user)
    db.flush()
    return user


def _get_or_create_farm(
    db,
    owner: User,
    *,
    name: str,
    location: str,
    latitude: float,
    longitude: float,
    area: float,
    soil_type: str,
    irrigation_type: str,
) -> Farm:
    farm = (
        db.query(Farm)
        .filter(Farm.user_id == owner.id, Farm.name == name)
        .first()
    )
    if not farm:
        farm = Farm(
            user_id=owner.id,
            name=name,
            location=location,
            latitude=latitude,
            longitude=longitude,
            area=area,
            soil_type=soil_type,
            irrigation_type=irrigation_type,
            is_active=True,
        )
        db.add(farm)
        db.flush()
    else:
        farm.location = location
        farm.latitude = latitude
        farm.longitude = longitude
        farm.area = area
        farm.soil_type = soil_type
        farm.irrigation_type = irrigation_type
        farm.is_active = True
    return farm


def _ensure_crop(
    db,
    farm: Farm,
    *,
    crop_type: str,
    growth_stage: str,
    planting_days_ago: int | None = None,
) -> None:
    crop = db.query(Crop).filter(Crop.farm_id == farm.id).first()
    if not crop:
        crop = Crop(farm_id=farm.id, crop_type=crop_type, growth_stage=growth_stage)
        db.add(crop)
    else:
        crop.crop_type = crop_type
        crop.growth_stage = growth_stage
    if planting_days_ago is not None:
        crop.planting_date = datetime.utcnow() - timedelta(days=planting_days_ago)
    db.flush()


def _ensure_crop_season(
    db,
    farm: Farm,
    *,
    crop_type: str,
    planting_days_ago: int,
    harvest_days_ago: int | None = None,
    status: CropSeasonStatus = CropSeasonStatus.harvested,
    yield_amount: float | None = None,
    yield_unit: str | None = "kg/da",
    notes: str | None = None,
) -> CropHistory:
    """Idempotent crop season by farm + crop_type + approximate planting window."""
    plant_at = datetime.utcnow() - timedelta(days=planting_days_ago)
    window_start = plant_at - timedelta(days=14)
    window_end = plant_at + timedelta(days=14)
    row = (
        db.query(CropHistory)
        .filter(
            CropHistory.farm_id == farm.id,
            CropHistory.crop_type == crop_type,
            CropHistory.planting_date >= window_start,
            CropHistory.planting_date <= window_end,
        )
        .first()
    )
    harvest_at = (
        datetime.utcnow() - timedelta(days=harvest_days_ago)
        if harvest_days_ago is not None
        else None
    )
    if not row:
        row = CropHistory(
            farm_id=farm.id,
            crop_type=crop_type,
            planting_date=plant_at,
            harvest_date=harvest_at if status == CropSeasonStatus.harvested else harvest_at,
            status=status,
            yield_amount=yield_amount,
            yield_unit=yield_unit,
            notes=notes,
            source_type="manual",
        )
        db.add(row)
    else:
        row.status = status
        row.planting_date = plant_at
        row.harvest_date = harvest_at if status == CropSeasonStatus.harvested else None
        if yield_amount is not None:
            row.yield_amount = yield_amount
        if yield_unit:
            row.yield_unit = yield_unit
        if notes:
            row.notes = notes
        row.source_type = "manual"
    db.flush()
    return row


def _ensure_zone(db, farm: Farm, name: str, notes: str | None = None) -> ManagementZone:
    zone = (
        db.query(ManagementZone)
        .filter(ManagementZone.farm_id == farm.id, ManagementZone.name == name)
        .first()
    )
    if not zone:
        zone = ManagementZone(farm_id=farm.id, name=name, notes=notes)
        db.add(zone)
        db.flush()
    elif notes and not zone.notes:
        zone.notes = notes
    return zone


def _ensure_device(
    db,
    farm: Farm,
    *,
    device_name: str,
    serial_number: str,
    region_name: str,
    zone: ManagementZone | None = None,
    device_type: str = "soil_moisture",
    battery: float = 85.0,
    signal_dbm: int = -65,
    connection_type: str = "wifi",
    depth_cm: int = 20,
) -> Device:
    device = (
        db.query(Device)
        .filter(Device.farm_id == farm.id, Device.device_name == device_name)
        .first()
    )
    if not device:
        device = Device(
            farm_id=farm.id,
            device_name=device_name,
            device_type=device_type,
            connection_status="active",
            serial_number=serial_number,
            region_name=region_name,
            zone_id=zone.id if zone else None,
            depth_cm=depth_cm,
            connection_type=connection_type,
            battery_percent=battery,
            signal_dbm=signal_dbm,
            firmware_version="1.0.0-sim",
            installed_at=datetime.utcnow() - timedelta(days=21),
            calibration_offset=0.0,
            sampling_minutes=15,
            last_data_time=datetime.utcnow(),
        )
        db.add(device)
        db.flush()
    else:
        device.connection_status = "active"
        device.region_name = region_name
        device.zone_id = zone.id if zone else device.zone_id
        device.battery_percent = battery
        device.signal_dbm = signal_dbm
        device.serial_number = serial_number
    return device


def _seed_readings_if_empty(
    db,
    farm: Farm,
    rows: list[dict],
    *,
    device: Device | None = None,
    min_count: int = 3,
) -> None:
    count = db.query(SensorReading).filter(SensorReading.farm_id == farm.id).count()
    if count >= min_count:
        latest = (
            db.query(SensorReading)
            .filter(SensorReading.farm_id == farm.id)
            .order_by(SensorReading.timestamp.desc())
            .first()
        )
        if latest and device:
            device.last_data_time = latest.timestamp
        return

    # Replace thin single-reading seeds so personas stay distinct.
    if count > 0 and count < min_count:
        db.query(SensorReading).filter(SensorReading.farm_id == farm.id).delete()
        db.flush()

    last_ts = None
    for row in rows:
        ts = row.get("timestamp") or datetime.utcnow()
        last_ts = ts
        db.add(
            SensorReading(
                farm_id=farm.id,
                device_id=row.get("device_id") or (device.id if device else None),
                zone_id=row.get("zone_id"),
                source_type=row["source_type"],
                timestamp=ts,
                soil_moisture=row["soil_moisture"],
                soil_temperature=row.get("soil_temperature"),
                air_temperature=row.get("air_temperature"),
                air_humidity=row.get("air_humidity"),
                rainfall_probability=row.get("rainfall_probability"),
                ph=row.get("ph"),
                ec=row.get("ec"),
                last_irrigation_hours_ago=row.get("last_irrigation_hours_ago"),
                data_confidence=row.get("data_confidence", 80.0),
                is_validated=True,
            )
        )
    db.flush()
    if device and last_ts:
        device.last_data_time = last_ts


def _ensure_prediction(db, farm: Farm, **kwargs) -> None:
    if db.query(Prediction).filter(Prediction.farm_id == farm.id).count() > 0:
        pred = (
            db.query(Prediction)
            .filter(Prediction.farm_id == farm.id)
            .order_by(Prediction.created_at.desc())
            .first()
        )
        for k, v in kwargs.items():
            setattr(pred, k, v)
        return
    db.add(Prediction(farm_id=farm.id, **kwargs))
    db.flush()


def _ensure_irrigation_history(db, farm: Farm, events: list[dict]) -> None:
    if db.query(IrrigationEvent).filter(IrrigationEvent.farm_id == farm.id).count() > 0:
        return
    for ev in events:
        db.add(
            IrrigationEvent(
                farm_id=farm.id,
                start_time=ev["start_time"],
                end_time=ev.get("end_time"),
                duration=ev.get("duration"),
                water_amount=ev.get("water_amount"),
                status=ev.get("status", IrrigationStatus.completed),
            )
        )
    db.flush()


def _ensure_lab_report(
    db,
    farm: Farm,
    *,
    lab_name: str,
    report_number: str,
    zone: ManagementZone | None,
    parameters: list[tuple[str, float, str]],
    notes: str,
) -> None:
    exists = (
        db.query(LabReport)
        .filter(LabReport.farm_id == farm.id, LabReport.report_number == report_number)
        .first()
    )
    if exists:
        return
    report = LabReport(
        farm_id=farm.id,
        zone_id=zone.id if zone else None,
        lab_name=lab_name,
        report_number=report_number,
        analysis_date=datetime.utcnow() - timedelta(days=12),
        sample_date=datetime.utcnow() - timedelta(days=14),
        sample_depth_cm="0-30",
        sample_region=zone.name if zone else None,
        source_type=LabSourceType.lab_manual,
        user_confirmed=True,
        status="confirmed",
        notes=notes,
        extraction_confidence=92.0,
    )
    db.add(report)
    db.flush()
    for code, value, unit in parameters:
        db.add(
            LabParameter(
                report_id=report.id,
                parameter_code=code,
                value=value,
                unit=unit,
                method="demo-manual",
                extracted_auto=False,
                confidence_pct=95.0,
            )
        )
    db.flush()


def _ensure_materials(
    db,
    farm: Farm,
    codes: list[str],
    *,
    last_fertilizer_code: str | None = None,
    last_pesticide_code: str | None = None,
) -> None:
    ensure_agro_catalog(db)
    if db.query(FarmMaterialUse).filter(FarmMaterialUse.farm_id == farm.id).count() > 0:
        return
    by_code = {
        m.code: m
        for m in db.query(AgroMaterial).filter(AgroMaterial.code.in_(codes)).all()
    }
    items = []
    for code in codes:
        m = by_code.get(code)
        if not m:
            continue
        items.append(
            {
                "material_id": m.id,
                "notes": None,
                "frequency": None,
                "last_applied_at": None,
                "is_last_fertilizer": code == last_fertilizer_code,
                "is_last_pesticide": code == last_pesticide_code,
            }
        )
    if items:
        sync_farm_materials(db, farm.id, items=items)


def seed_ticket(
    db,
    user: User,
    farm: Farm | None,
    *,
    subject: str,
    description: str,
    priority: str = "medium",
    status: str = "open",
) -> None:
    exists = (
        db.query(SupportTicket)
        .filter(SupportTicket.user_id == user.id, SupportTicket.subject == subject)
        .first()
    )
    if exists:
        return
    n = db.query(SupportTicket).count() + 1
    db.add(
        SupportTicket(
            ticket_no=f"TK-DEMO-{n:04d}",
            user_id=user.id,
            subject=subject,
            description=description,
            priority=priority,
            status=status,
            farm_id=farm.id if farm else None,
        )
    )


# ---------------------------------------------------------------------------
# Persona farms
# ---------------------------------------------------------------------------


def seed_farmer_farm(db, owner: User) -> Farm:
    """Çiftçi — Antalya sera: dry-down then irrigate."""
    farm = _get_or_create_farm(
        db,
        owner,
        name="Domates Serası",
        location="Antalya / Serik",
        latitude=36.9167,
        longitude=31.1000,
        area=2.5,
        soil_type="tinli",
        irrigation_type="damla",
    )
    _ensure_crop(
        db,
        farm,
        crop_type="domates",
        growth_stage="ciceklenme",
        planting_days_ago=45,
    )
    z1 = _ensure_zone(db, farm, "Kuzey", "Kuzey sera hücreleri")
    z2 = _ensure_zone(db, farm, "Orta", "Orta sera hücreleri")
    z3 = _ensure_zone(db, farm, "Güney", "Güney sera hücreleri")
    d1 = _ensure_device(
        db,
        farm,
        device_name="Toprak Nemi Sensörü 01",
        serial_number="SN-DEMO-CFT-001",
        region_name="Kuzey",
        zone=z1,
        battery=88.0,
        signal_dbm=-64,
    )
    d2 = _ensure_device(
        db,
        farm,
        device_name="Toprak Nemi Sensörü 02",
        serial_number="SN-DEMO-CFT-002",
        region_name="Güney",
        zone=z3,
        battery=76.0,
        signal_dbm=-71,
        connection_type="lora",
    )

    now = datetime.utcnow()
    # Dry-down curve → then after irrigation bump (history)
    _seed_readings_if_empty(
        db,
        farm,
        [
            {
                "timestamp": now - timedelta(hours=48),
                "source_type": SourceType.simulation,
                "soil_moisture": 34.0,
                "soil_temperature": 23.5,
                "air_temperature": 29.0,
                "air_humidity": 48.0,
                "rainfall_probability": 5.0,
                "last_irrigation_hours_ago": 8.0,
                "data_confidence": 86.0,
                "zone_id": z1.id,
                "device_id": d1.id,
            },
            {
                "timestamp": now - timedelta(hours=36),
                "source_type": SourceType.simulation,
                "soil_moisture": 29.5,
                "soil_temperature": 24.0,
                "air_temperature": 30.0,
                "air_humidity": 46.0,
                "rainfall_probability": 8.0,
                "last_irrigation_hours_ago": 20.0,
                "data_confidence": 84.0,
                "zone_id": z1.id,
                "device_id": d1.id,
            },
            {
                "timestamp": now - timedelta(hours=24),
                "source_type": SourceType.simulation,
                "soil_moisture": 24.0,
                "soil_temperature": 24.8,
                "air_temperature": 31.0,
                "air_humidity": 44.0,
                "rainfall_probability": 10.0,
                "last_irrigation_hours_ago": 32.0,
                "data_confidence": 83.0,
                "zone_id": z1.id,
                "device_id": d1.id,
            },
            {
                "timestamp": now - timedelta(hours=12),
                "source_type": SourceType.simulation,
                "soil_moisture": 21.5,
                "soil_temperature": 25.2,
                "air_temperature": 32.0,
                "air_humidity": 42.0,
                "rainfall_probability": 12.0,
                "ph": 6.4,
                "ec": 1.8,
                "last_irrigation_hours_ago": 44.0,
                "data_confidence": 82.0,
                "zone_id": z3.id,
                "device_id": d2.id,
            },
            {
                "timestamp": now - timedelta(hours=2),
                "source_type": SourceType.simulation,
                "soil_moisture": 22.0,
                "soil_temperature": 25.5,
                "air_temperature": 31.5,
                "air_humidity": 45.0,
                "rainfall_probability": 10.0,
                "ph": 6.5,
                "ec": 1.9,
                "last_irrigation_hours_ago": 54.0,
                "data_confidence": 82.0,
                "zone_id": z1.id,
                "device_id": d1.id,
            },
        ],
        device=d1,
        min_count=5,
    )

    _ensure_prediction(
        db,
        farm,
        irrigation_needed=True,
        irrigation_duration=25.0,
        risk_level=RiskLevel.high,
        confidence_score=78.0,
        explanation=(
            "Sera domates: toprak nemi kuruma eğiliminde (≈%22) ve son sulama "
            "üzerinden ~2 gün geçmiş. Önerilen süre ~25 dk (simülasyon demo)."
        ),
        moisture_24h=21.0,
        moisture_48h=18.0,
        moisture_72h=15.0,
    )
    _ensure_irrigation_history(
        db,
        farm,
        [
            {
                "start_time": now - timedelta(days=5),
                "end_time": now - timedelta(days=5) + timedelta(minutes=22),
                "duration": 22.0,
                "water_amount": 130.0,
                "status": IrrigationStatus.completed,
            },
            {
                "start_time": now - timedelta(days=3),
                "end_time": now - timedelta(days=3) + timedelta(minutes=20),
                "duration": 20.0,
                "water_amount": 120.0,
                "status": IrrigationStatus.completed,
            },
        ],
    )
    _ensure_lab_report(
        db,
        farm,
        lab_name="Antalya Toprak Lab",
        report_number="LAB-CFT-2026-014",
        zone=z1,
        parameters=[
            ("ph", 6.5, "pH"),
            ("ec", 1.85, "dS/m"),
            ("organic_matter", 2.8, "%"),
            ("n", 42.0, "ppm"),
            ("p", 18.0, "ppm"),
            ("k", 210.0, "ppm"),
        ],
        notes="Kullanıcı onaylı demo lab (sera tinli toprak).",
    )
    _ensure_materials(
        db,
        farm,
        ["fert_map", "fert_kno3", "fert_can", "pp_fungicide", "pp_insecticide", "pp_acaricide"],
        last_fertilizer_code="fert_kno3",
        last_pesticide_code="pp_fungicide",
    )
    # Product seasons: past leafy + pepper, current tomato (solanaceae → suggest cereal/legume after harvest)
    _ensure_crop_season(
        db,
        farm,
        crop_type="marul",
        planting_days_ago=200,
        harvest_days_ago=150,
        status=CropSeasonStatus.harvested,
        yield_amount=2800.0,
        notes="Demo: önceki yapraklı sebze sezonu (manuel kayıt).",
    )
    _ensure_crop_season(
        db,
        farm,
        crop_type="biber",
        planting_days_ago=130,
        harvest_days_ago=55,
        status=CropSeasonStatus.harvested,
        yield_amount=4200.0,
        notes="Demo: hasat edilmiş biber; aynı aile rotasyonu notu için.",
    )
    _ensure_crop_season(
        db,
        farm,
        crop_type="domates",
        planting_days_ago=45,
        harvest_days_ago=None,
        status=CropSeasonStatus.growing,
        yield_amount=None,
        yield_unit=None,
        notes="Demo: mevcut sera sezonu (manuel çiftlik kaydı).",
    )
    return farm


def seed_light_farm(db, owner: User) -> Farm:
    """Backward-compatible alias → agronomist Konya field."""
    return seed_agronomist_farm(db, owner)


def seed_agronomist_farm(db, owner: User) -> Farm:
    """Ziraat — Konya buğday, kumlu, orta nem, manuel + simülasyon karışımı."""
    farm = (
        db.query(Farm)
        .filter(
            Farm.user_id == owner.id,
            Farm.name.in_(["Karapınar Buğday Tarlası", "Danışman Demo Tarlası"]),
        )
        .first()
    )
    if farm:
        farm.name = "Karapınar Buğday Tarlası"
        farm.location = "Konya / Karapınar"
        farm.latitude = 37.7147
        farm.longitude = 33.5506
        farm.area = 18.5
        farm.soil_type = "kumlu"
        farm.irrigation_type = "yagmurlama"
        farm.is_active = True
    else:
        farm = _get_or_create_farm(
            db,
            owner,
            name="Karapınar Buğday Tarlası",
            location="Konya / Karapınar",
            latitude=37.7147,
            longitude=33.5506,
            area=18.5,
            soil_type="kumlu",
            irrigation_type="yagmurlama",
        )

    _ensure_crop(
        db,
        farm,
        crop_type="bugday",
        growth_stage="vegetatif",
        planting_days_ago=70,
    )
    z_a = _ensure_zone(db, farm, "A Parseli", "Kumlu üst yamaç")
    z_b = _ensure_zone(db, farm, "B Parseli", "Orta vadi")
    d_sim = _ensure_device(
        db,
        farm,
        device_name="Alan Nem Prob A",
        serial_number="SN-DEMO-ZRT-A01",
        region_name="A Parseli",
        zone=z_a,
        battery=91.0,
        signal_dbm=-58,
        depth_cm=30,
    )
    d_man = _ensure_device(
        db,
        farm,
        device_name="El Ölçümü İstasyonu",
        serial_number="SN-DEMO-ZRT-M01",
        region_name="B Parseli",
        zone=z_b,
        device_type="handheld_probe",
        battery=100.0,
        signal_dbm=-50,
        connection_type="manual",
        depth_cm=20,
    )

    now = datetime.utcnow()
    _seed_readings_if_empty(
        db,
        farm,
        [
            {
                "timestamp": now - timedelta(hours=40),
                "source_type": SourceType.manual,
                "soil_moisture": 36.0,
                "soil_temperature": 18.0,
                "air_temperature": 24.0,
                "air_humidity": 38.0,
                "rainfall_probability": 15.0,
                "last_irrigation_hours_ago": 18.0,
                "data_confidence": 74.0,
                "zone_id": z_b.id,
                "device_id": d_man.id,
            },
            {
                "timestamp": now - timedelta(hours=28),
                "source_type": SourceType.simulation,
                "soil_moisture": 34.5,
                "soil_temperature": 18.5,
                "air_temperature": 25.0,
                "air_humidity": 36.0,
                "rainfall_probability": 18.0,
                "last_irrigation_hours_ago": 30.0,
                "data_confidence": 80.0,
                "zone_id": z_a.id,
                "device_id": d_sim.id,
            },
            {
                "timestamp": now - timedelta(hours=14),
                "source_type": SourceType.manual,
                "soil_moisture": 33.0,
                "soil_temperature": 19.0,
                "air_temperature": 26.0,
                "air_humidity": 35.0,
                "rainfall_probability": 20.0,
                "ph": 7.6,
                "ec": 0.9,
                "last_irrigation_hours_ago": 42.0,
                "data_confidence": 76.0,
                "zone_id": z_b.id,
                "device_id": d_man.id,
            },
            {
                "timestamp": now - timedelta(hours=3),
                "source_type": SourceType.simulation,
                "soil_moisture": 32.5,
                "soil_temperature": 19.5,
                "air_temperature": 27.0,
                "air_humidity": 34.0,
                "rainfall_probability": 22.0,
                "ph": 7.5,
                "ec": 0.95,
                "last_irrigation_hours_ago": 12.0,
                "data_confidence": 81.0,
                "zone_id": z_a.id,
                "device_id": d_sim.id,
            },
        ],
        device=d_sim,
        min_count=4,
    )

    _ensure_prediction(
        db,
        farm,
        irrigation_needed=False,
        irrigation_duration=None,
        risk_level=RiskLevel.medium,
        confidence_score=72.0,
        explanation=(
            "Kumlu Konya tarlası: nem orta (%32–36). Yağmurlama sonrası izleme "
            "yeterli; acil sulama yok (simülasyon + manuel karışım)."
        ),
        moisture_24h=31.0,
        moisture_48h=29.5,
        moisture_72h=28.0,
    )
    _ensure_irrigation_history(
        db,
        farm,
        [
            {
                "start_time": now - timedelta(days=7),
                "end_time": now - timedelta(days=7) + timedelta(minutes=45),
                "duration": 45.0,
                "water_amount": 420.0,
                "status": IrrigationStatus.completed,
            },
            {
                "start_time": now - timedelta(days=2),
                "end_time": now - timedelta(days=2) + timedelta(minutes=35),
                "duration": 35.0,
                "water_amount": 310.0,
                "status": IrrigationStatus.completed,
            },
        ],
    )
    _ensure_lab_report(
        db,
        farm,
        lab_name="Konya İl Toprak Analiz",
        report_number="LAB-ZRT-2026-008",
        zone=z_a,
        parameters=[
            ("ph", 7.6, "pH"),
            ("ec", 0.92, "dS/m"),
            ("organic_matter", 1.1, "%"),
            ("n", 28.0, "ppm"),
            ("p", 12.0, "ppm"),
            ("k", 145.0, "ppm"),
            ("lime", 8.5, "%"),
        ],
        notes="Danışman onaylı açık alan buğday profili (kumlu).",
    )
    _ensure_materials(
        db,
        farm,
        ["fert_urea", "fert_dap", "fert_as", "fert_compost", "pp_fungicide"],
    )
    # Open field: harvested maize + earlier legume — no growing history row so suggestions show
    _ensure_crop_season(
        db,
        farm,
        crop_type="fasulye",
        planting_days_ago=280,
        harvest_days_ago=210,
        status=CropSeasonStatus.harvested,
        yield_amount=220.0,
        notes="Demo: eski baklagil sezonu.",
    )
    _ensure_crop_season(
        db,
        farm,
        crop_type="misir",
        planting_days_ago=180,
        harvest_days_ago=45,
        status=CropSeasonStatus.harvested,
        yield_amount=850.0,
        notes="Demo: son hasat mısır — rotasyon önerileri için (manuel kayıt).",
    )
    return farm


def seed_cooperative_farms(db, owner: User) -> list[Farm]:
    """Kooperatif — iki arazi, farklı nem / ürün."""
    now = datetime.utcnow()
    farms: list[Farm] = []

    # Farm 1 — multi-zone mixed veggies, dryer north
    f1 = _get_or_create_farm(
        db,
        owner,
        name="Yeşilova Merkez Parsel",
        location="Isparta / Yalvaç",
        latitude=38.2956,
        longitude=31.1778,
        area=12.0,
        soil_type="killi-tinli",
        irrigation_type="damla",
    )
    _ensure_crop(
        db,
        f1,
        crop_type="biber",
        growth_stage="meyve",
        planting_days_ago=55,
    )
    zn = _ensure_zone(db, f1, "Kuzey Zonu", "Rüzgâra açık, daha kuru")
    zo = _ensure_zone(db, f1, "Orta Zonu", "Ana damla hattı")
    zg = _ensure_zone(db, f1, "Güney Zonu", "Gölgeli / daha nemli")
    d_n = _ensure_device(
        db,
        f1,
        device_name="Koop Nodal N",
        serial_number="SN-DEMO-KOP-N1",
        region_name="Kuzey",
        zone=zn,
        battery=82.0,
        signal_dbm=-68,
        connection_type="lora",
    )
    d_o = _ensure_device(
        db,
        f1,
        device_name="Koop Nodal O",
        serial_number="SN-DEMO-KOP-O1",
        region_name="Orta",
        zone=zo,
        battery=79.0,
        signal_dbm=-66,
    )
    d_g = _ensure_device(
        db,
        f1,
        device_name="Koop Nodal G",
        serial_number="SN-DEMO-KOP-G1",
        region_name="Güney",
        zone=zg,
        battery=85.0,
        signal_dbm=-62,
    )
    _seed_readings_if_empty(
        db,
        f1,
        [
            {
                "timestamp": now - timedelta(hours=30),
                "source_type": SourceType.simulation,
                "soil_moisture": 19.0,
                "soil_temperature": 22.0,
                "air_temperature": 28.0,
                "air_humidity": 40.0,
                "rainfall_probability": 5.0,
                "last_irrigation_hours_ago": 40.0,
                "data_confidence": 79.0,
                "zone_id": zn.id,
                "device_id": d_n.id,
            },
            {
                "timestamp": now - timedelta(hours=18),
                "source_type": SourceType.simulation,
                "soil_moisture": 27.0,
                "soil_temperature": 21.5,
                "air_temperature": 27.0,
                "air_humidity": 42.0,
                "rainfall_probability": 8.0,
                "last_irrigation_hours_ago": 16.0,
                "data_confidence": 81.0,
                "zone_id": zo.id,
                "device_id": d_o.id,
            },
            {
                "timestamp": now - timedelta(hours=6),
                "source_type": SourceType.simulation,
                "soil_moisture": 33.0,
                "soil_temperature": 21.0,
                "air_temperature": 26.0,
                "air_humidity": 48.0,
                "rainfall_probability": 10.0,
                "last_irrigation_hours_ago": 10.0,
                "data_confidence": 83.0,
                "zone_id": zg.id,
                "device_id": d_g.id,
            },
            {
                "timestamp": now - timedelta(hours=1),
                "source_type": SourceType.simulation,
                "soil_moisture": 20.5,
                "soil_temperature": 22.5,
                "air_temperature": 29.0,
                "air_humidity": 39.0,
                "rainfall_probability": 6.0,
                "ph": 6.9,
                "ec": 1.4,
                "last_irrigation_hours_ago": 48.0,
                "data_confidence": 80.0,
                "zone_id": zn.id,
                "device_id": d_n.id,
            },
        ],
        device=d_n,
        min_count=4,
    )
    _ensure_prediction(
        db,
        f1,
        irrigation_needed=True,
        irrigation_duration=30.0,
        risk_level=RiskLevel.high,
        confidence_score=74.0,
        explanation=(
            "Kooperatif merkez: Kuzey zonu kuruyor (%20), Güney nemli. "
            "Bölgesel sulama önerilir — önce kuzey hattı (~30 dk, simülasyon)."
        ),
        moisture_24h=19.0,
        moisture_48h=17.0,
        moisture_72h=15.5,
    )
    _ensure_irrigation_history(
        db,
        f1,
        [
            {
                "start_time": now - timedelta(days=4),
                "end_time": now - timedelta(days=4) + timedelta(minutes=40),
                "duration": 40.0,
                "water_amount": 280.0,
                "status": IrrigationStatus.completed,
            }
        ],
    )
    _ensure_lab_report(
        db,
        f1,
        lab_name="Isparta Koop Laboratuvarı",
        report_number="LAB-KOP-M-031",
        zone=zo,
        parameters=[
            ("ph", 6.9, "pH"),
            ("ec", 1.35, "dS/m"),
            ("organic_matter", 2.2, "%"),
            ("n", 35.0, "ppm"),
            ("p", 15.0, "ppm"),
            ("k", 180.0, "ppm"),
        ],
        notes="Merkez parsel — onaylı.",
    )
    _ensure_materials(
        db,
        f1,
        ["fert_mkp", "fert_kno3", "fert_mgso4", "pp_insecticide", "pp_biological"],
    )
    _ensure_crop_season(
        db,
        f1,
        crop_type="domates",
        planting_days_ago=210,
        harvest_days_ago=100,
        status=CropSeasonStatus.harvested,
        yield_amount=5100.0,
        notes="Koop demo: önceki domates sezonu (solanaceae).",
    )
    _ensure_crop_season(
        db,
        f1,
        crop_type="biber",
        planting_days_ago=55,
        harvest_days_ago=None,
        status=CropSeasonStatus.growing,
        yield_amount=None,
        yield_unit=None,
        notes="Koop demo: mevcut biber (aynı aile — hasat sonrası rotasyon).",
    )
    farms.append(f1)

    # Farm 2 — cooler orchard, moderate-high moisture
    f2 = _get_or_create_farm(
        db,
        owner,
        name="Yeşilova Kuzey Bahçe",
        location="Isparta / Gelendost",
        latitude=38.1210,
        longitude=31.0150,
        area=6.5,
        soil_type="tinli",
        irrigation_type="damla",
    )
    _ensure_crop(
        db,
        f2,
        crop_type="elma",
        growth_stage="meyve_gelisim",
        planting_days_ago=900,
    )
    zb = _ensure_zone(db, f2, "Bahçe İç", "Olgun ağaç sırası")
    d_b = _ensure_device(
        db,
        f2,
        device_name="Bahçe Nem",
        serial_number="SN-DEMO-KOP-B1",
        region_name="Bahçe",
        zone=zb,
        battery=94.0,
        signal_dbm=-55,
    )
    _seed_readings_if_empty(
        db,
        f2,
        [
            {
                "timestamp": now - timedelta(hours=36),
                "source_type": SourceType.simulation,
                "soil_moisture": 38.0,
                "soil_temperature": 17.0,
                "air_temperature": 22.0,
                "air_humidity": 55.0,
                "rainfall_probability": 25.0,
                "last_irrigation_hours_ago": 6.0,
                "data_confidence": 85.0,
                "zone_id": zb.id,
                "device_id": d_b.id,
            },
            {
                "timestamp": now - timedelta(hours=18),
                "source_type": SourceType.simulation,
                "soil_moisture": 36.5,
                "soil_temperature": 17.5,
                "air_temperature": 23.0,
                "air_humidity": 52.0,
                "rainfall_probability": 30.0,
                "last_irrigation_hours_ago": 24.0,
                "data_confidence": 84.0,
                "zone_id": zb.id,
                "device_id": d_b.id,
            },
            {
                "timestamp": now - timedelta(hours=4),
                "source_type": SourceType.manual,
                "soil_moisture": 35.0,
                "soil_temperature": 18.0,
                "air_temperature": 24.0,
                "air_humidity": 50.0,
                "rainfall_probability": 28.0,
                "ph": 6.8,
                "ec": 0.8,
                "last_irrigation_hours_ago": 36.0,
                "data_confidence": 77.0,
                "zone_id": zb.id,
                "device_id": d_b.id,
            },
        ],
        device=d_b,
        min_count=3,
    )
    _ensure_prediction(
        db,
        f2,
        irrigation_needed=False,
        irrigation_duration=None,
        risk_level=RiskLevel.low,
        confidence_score=80.0,
        explanation=(
            "Kuzey bahçe nemi yeterli (%35+). Yağış ihtimali var; sulama ertelemesi "
            "uygun (simülasyon demo)."
        ),
        moisture_24h=34.0,
        moisture_48h=33.0,
        moisture_72h=32.0,
    )
    _ensure_irrigation_history(
        db,
        f2,
        [
            {
                "start_time": now - timedelta(days=6),
                "end_time": now - timedelta(days=6) + timedelta(minutes=50),
                "duration": 50.0,
                "water_amount": 360.0,
                "status": IrrigationStatus.completed,
            }
        ],
    )
    _ensure_materials(db, f2, ["fert_k2so4", "fert_can", "pp_fungicide", "pp_acaricide"])
    farms.append(f2)
    return farms


def seed_admin_demo(db, owner: User) -> Farm | None:
    """Admin — küçük demo arazi + panel için yeterli filo/ticket bağlamı."""
    farm = _get_or_create_farm(
        db,
        owner,
        name="Yönetim Demo Arazisi",
        location="Ankara / Gölbaşı",
        latitude=39.7900,
        longitude=32.8050,
        area=0.8,
        soil_type="tinli",
        irrigation_type="damla",
    )
    _ensure_crop(db, farm, crop_type="marul", growth_stage="vegetatif", planting_days_ago=20)
    z = _ensure_zone(db, farm, "Test Hücresi", "Admin smoke / cihaz filosu")
    d = _ensure_device(
        db,
        farm,
        device_name="Admin Filo Sensörü",
        serial_number="SN-DEMO-ADM-01",
        region_name="Test",
        zone=z,
        battery=97.0,
        signal_dbm=-52,
    )
    now = datetime.utcnow()
    _seed_readings_if_empty(
        db,
        farm,
        [
            {
                "timestamp": now - timedelta(hours=8),
                "source_type": SourceType.simulation,
                "soil_moisture": 30.0,
                "soil_temperature": 20.0,
                "air_temperature": 25.0,
                "air_humidity": 45.0,
                "rainfall_probability": 10.0,
                "last_irrigation_hours_ago": 20.0,
                "data_confidence": 88.0,
                "zone_id": z.id,
                "device_id": d.id,
            },
            {
                "timestamp": now - timedelta(hours=1),
                "source_type": SourceType.simulation,
                "soil_moisture": 29.0,
                "soil_temperature": 20.5,
                "air_temperature": 26.0,
                "air_humidity": 44.0,
                "rainfall_probability": 12.0,
                "last_irrigation_hours_ago": 27.0,
                "data_confidence": 87.0,
                "zone_id": z.id,
                "device_id": d.id,
            },
        ],
        device=d,
        min_count=2,
    )
    _ensure_prediction(
        db,
        farm,
        irrigation_needed=False,
        irrigation_duration=None,
        risk_level=RiskLevel.low,
        confidence_score=85.0,
        explanation="Admin test arazisi stabil; panel KPI için örnek nem.",
        moisture_24h=28.0,
        moisture_48h=27.0,
        moisture_72h=26.0,
    )
    _ensure_materials(db, farm, ["fert_compost", "pp_biological"])
    return farm


def seed_persona(db, spec: dict, user: User) -> list[Farm]:
    profile = spec.get("seed_profile") or ("farmer" if spec.get("seed_farm") else None)
    farms: list[Farm] = []

    if profile == "farmer" or spec.get("seed_farm"):
        farm = seed_farmer_farm(db, user)
        farms.append(farm)
        seed_ticket(
            db,
            user,
            farm,
            subject="IoT simülasyon veri gecikmesi",
            description="Demo: sera nem okuması gecikti, kontrol edilir.",
            priority="medium",
        )
    elif profile == "agronomist" or spec.get("seed_farm_light"):
        farm = seed_agronomist_farm(db, user)
        farms.append(farm)
        seed_ticket(
            db,
            user,
            farm,
            subject="Danışman — kumlu tarla kalibrasyon",
            description="Buğday tarlası el ölçümü ile simülasyon farkı incelenmeli.",
            priority="low",
            status="pending",
        )
    elif profile == "cooperative":
        farms = seed_cooperative_farms(db, user)
        seed_ticket(
            db,
            user,
            farms[0] if farms else None,
            subject="Kooperatif — kuzey zon kuraklık",
            description="Merkez parsel kuzey zonu diğerlerine göre düşük nem.",
            priority="high",
        )
    elif profile == "admin":
        farm = seed_admin_demo(db, user)
        if farm:
            farms.append(farm)
        seed_ticket(
            db,
            user,
            farms[0] if farms else None,
            subject="Sistem sağlık kontrolü",
            description="Admin demo: genel platform sağlık ve filo taraması.",
            priority="low",
            status="resolved",
        )

    return farms


def run_seed(db) -> dict[str, list[Farm]]:
    """Idempotent upsert used by CLI and demo_bootstrap."""
    ensure_agro_catalog(db)
    result: dict[str, list[Farm]] = {}
    for spec in DEMO_USERS:
        user = upsert_user(db, spec)
        farms = seed_persona(db, spec, user)
        result[spec["email"]] = farms
    return result


def main() -> None:
    Base.metadata.create_all(bind=engine)
    ensure_sqlite_columns()
    db = SessionLocal()
    try:
        print("=== AgriTwin demo kullanicilari (ayrik persona verisi) ===")
        print(f"Ortak sifre: {DEMO_PASSWORD}")
        print("Dogrulama: e-posta onceden dogrulanmis (kod gerekmez)\n")

        result = run_seed(db)
        db.commit()

        for spec in DEMO_USERS:
            farms = result.get(spec["email"], [])
            print(f"- {spec['role']:12}  {spec['email']:28}  {spec['name']}")
            print(f"  - {spec['purpose']}")
            for farm in farms:
                print(f"  - Arazi: {farm.name} (id={farm.id}, {farm.location})")

        print("\nDemo akis onerisi:")
        print("1) admin@agritwin.demo -> /admin (KPI, kullanicilar, destek)")
        print("2) ciftci@agritwin.demo -> Domates Serasi (kuruma + sulama onayi)")
        print("3) ziraat@agritwin.demo -> Karapinar Bugday (orta nem, manuel+sim)")
        print("4) kooperatif@agritwin.demo -> 2 arazi / degisen zon nemi")
    finally:
        db.close()


if __name__ == "__main__":
    main()
