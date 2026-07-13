"""Seed demo users + Domates Serası sample data for jüri/demo.

Run from backend/:
  .venv\\Scripts\\python.exe -m scripts.seed_demo
"""

from __future__ import annotations

import sys
from datetime import datetime, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app.auth import hash_password
from app.database import Base, SessionLocal, engine
from app.db_migrate import ensure_sqlite_columns
from app.models import (
    Crop,
    Device,
    Farm,
    IrrigationEvent,
    IrrigationStatus,
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
    },
    {
        "email": "ciftci@agritwin.demo",
        "name": "Mehmet Yılmaz",
        "role": "farmer",
        "phone": "5551000002",
        "purpose": "Ana demo: Domates Serası — nem, AI, senaryo, sanal sulama",
        "seed_farm": True,
    },
    {
        "email": "ziraat@agritwin.demo",
        "name": "Elif Kaya",
        "role": "agronomist",
        "phone": "5551000003",
        "purpose": "Danışmanlık rolü; ikinci arazi ile çok kullanıcılı admin listesi",
        "seed_farm_light": True,
    },
    {
        "email": "kooperatif@agritwin.demo",
        "name": "Yeşilova Kooperatifi",
        "role": "cooperative",
        "phone": "5551000004",
        "purpose": "Kooperatif hesabı; üretici paneli + destek talebi açabilir",
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


def seed_farmer_farm(db, owner: User) -> Farm:
    farm = (
        db.query(Farm)
        .filter(Farm.user_id == owner.id, Farm.name == "Domates Serası")
        .first()
    )
    if not farm:
        farm = Farm(
            user_id=owner.id,
            name="Domates Serası",
            location="Antalya / Serik",
            latitude=36.9167,
            longitude=31.1000,
            area=2.5,
            soil_type="tinli",
            irrigation_type="damla",
            is_active=True,
        )
        db.add(farm)
        db.flush()
        db.add(
            Crop(
                farm_id=farm.id,
                crop_type="domates",
                growth_stage="ciceklenme",
                planting_date=datetime.utcnow() - timedelta(days=45),
            )
        )
        db.add(
            ManagementZone(
                farm_id=farm.id,
                name="Bölge 1",
                notes="Kuzey sera hücreleri",
            )
        )
    else:
        if farm.latitude is None or farm.longitude is None:
            farm.latitude = 36.9167
            farm.longitude = 31.1000

    device = (
        db.query(Device)
        .filter(Device.farm_id == farm.id, Device.device_name == "Toprak Nemi Sensörü 01")
        .first()
    )
    if not device:
        device = Device(
            farm_id=farm.id,
            device_name="Toprak Nemi Sensörü 01",
            device_type="soil_moisture",
            connection_status="active",
            serial_number="SN-DEMO-001",
            region_name="Kuzey",
            depth_cm=20,
            connection_type="wifi",
            battery_percent=88.0,
            signal_dbm=-64,
            firmware_version="1.0.0-sim",
            installed_at=datetime.utcnow() - timedelta(days=14),
            calibration_offset=0.0,
            sampling_minutes=15,
            last_data_time=datetime.utcnow(),
        )
        db.add(device)
        db.flush()

    reading_count = (
        db.query(SensorReading).filter(SensorReading.farm_id == farm.id).count()
    )
    if reading_count == 0:
        for i, moisture in enumerate([34.0, 29.5, 24.0]):
            ts = datetime.utcnow() - timedelta(hours=36 - i * 12)
            reading = SensorReading(
                farm_id=farm.id,
                device_id=device.id,
                source_type=SourceType.simulation,
                timestamp=ts,
                soil_moisture=moisture,
                soil_temperature=24.0 + i,
                air_temperature=30.0 + i,
                air_humidity=45.0,
                rainfall_probability=10.0,
                last_irrigation_hours_ago=24.0 + i * 6,
                data_confidence=82.0,
                is_validated=True,
            )
            db.add(reading)
        db.flush()
        latest = (
            db.query(SensorReading)
            .filter(SensorReading.farm_id == farm.id)
            .order_by(SensorReading.timestamp.desc())
            .first()
        )
        if latest:
            device.last_data_time = latest.timestamp

    if (
        db.query(Prediction).filter(Prediction.farm_id == farm.id).count()
        == 0
    ):
        db.add(
            Prediction(
                farm_id=farm.id,
                irrigation_needed=True,
                irrigation_duration=25.0,
                risk_level=RiskLevel.high,
                confidence_score=78.0,
                explanation=(
                    "Toprak nemi düşük ve son sulama üzerinden uzun süre geçmiş. "
                    "Önerilen süre ~25 dk (simülasyon demo)."
                ),
                moisture_24h=21.0,
                moisture_48h=18.0,
                moisture_72h=15.0,
            )
        )

    if (
        db.query(IrrigationEvent).filter(IrrigationEvent.farm_id == farm.id).count()
        == 0
    ):
        db.add(
            IrrigationEvent(
                farm_id=farm.id,
                start_time=datetime.utcnow() - timedelta(days=3),
                end_time=datetime.utcnow() - timedelta(days=3, minutes=-20),
                duration=20.0,
                water_amount=120.0,
                status=IrrigationStatus.completed,
            )
        )

    return farm


def seed_light_farm(db, owner: User) -> Farm:
    farm = (
        db.query(Farm)
        .filter(Farm.user_id == owner.id, Farm.name == "Danışman Demo Tarlası")
        .first()
    )
    if farm:
        return farm
    farm = Farm(
        user_id=owner.id,
        name="Danışman Demo Tarlası",
        location="Konya / Karapınar",
        latitude=37.7147,
        longitude=33.5506,
        area=8.0,
        soil_type="kumlu",
        irrigation_type="yagmurlama",
        is_active=True,
    )
    db.add(farm)
    db.flush()
    db.add(
        Crop(
            farm_id=farm.id,
            crop_type="bugday",
            growth_stage="vegetatif",
        )
    )
    db.add(
        SensorReading(
            farm_id=farm.id,
            source_type=SourceType.manual,
            soil_moisture=38.0,
            air_temperature=26.0,
            rainfall_probability=20.0,
            last_irrigation_hours_ago=12.0,
            data_confidence=75.0,
            is_validated=True,
        )
    )
    return farm


def seed_ticket(db, user: User, farm: Farm | None) -> None:
    exists = (
        db.query(SupportTicket)
        .filter(SupportTicket.user_id == user.id)
        .first()
    )
    if exists:
        return
    n = db.query(SupportTicket).count() + 1
    db.add(
        SupportTicket(
            ticket_no=f"TK-DEMO-{n:04d}",
            user_id=user.id,
            subject="IoT simülasyon veri gecikmesi",
            description="Demo: nem okuması gecikti, kontrol edilir.",
            priority="medium",
            status="open",
            farm_id=farm.id if farm else None,
        )
    )


def main() -> None:
    Base.metadata.create_all(bind=engine)
    ensure_sqlite_columns()
    db = SessionLocal()
    try:
        print("=== AgriTwin demo kullanicilari ===")
        print(f"Ortak sifre: {DEMO_PASSWORD}")
        print("Dogrulama: e-posta onceden dogrulanmis (kod gerekmez)\n")

        farmer_farm = None
        for spec in DEMO_USERS:
            user = upsert_user(db, spec)
            farm = None
            if spec.get("seed_farm"):
                farm = seed_farmer_farm(db, user)
                farmer_farm = farm
                seed_ticket(db, user, farm)
            if spec.get("seed_farm_light"):
                farm = seed_light_farm(db, user)
            db.commit()
            print(
                f"- {spec['role']:12}  {spec['email']:28}  {spec['name']}"
            )
            print(f"  - {spec['purpose']}")
            if farm:
                print(f"  - Arazi: {farm.name} (id={farm.id})")

        print("\nDemo akis onerisi:")
        print("1) admin@agritwin.demo -> /admin")
        print("2) ciftci@agritwin.demo -> /dashboard -> Domates Serasi (AI / sulama)")
        if farmer_farm:
            print(f"   Ciftci arazi id: {farmer_farm.id}")
        print("3) ziraat / kooperatif -> rol farki + admin kullanici listesi")
    finally:
        db.close()


if __name__ == "__main__":
    main()
