import enum
from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class SourceType(str, enum.Enum):
    manual = "manual"
    simulation = "simulation"
    test_dataset = "test_dataset"
    lab_report = "lab_report"
    lab_manual = "lab_manual"
    iot = "iot"


class LabSourceType(str, enum.Enum):
    lab_report = "lab_report"
    lab_manual = "lab_manual"


class RiskLevel(str, enum.Enum):
    low = "low"
    medium = "medium"
    high = "high"
    critical = "critical"


class IrrigationStatus(str, enum.Enum):
    pending = "pending"
    running = "running"
    completed = "completed"
    stopped = "stopped"


class CropSeasonStatus(str, enum.Enum):
    growing = "growing"
    harvested = "harvested"


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    phone: Mapped[str | None] = mapped_column(String(32), nullable=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(50), default="farmer")
    email_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    # Soft paywall tier: free | pro (demo billing, no payment gateway)
    subscription_plan: Mapped[str] = mapped_column(String(40), default="free")
    last_login_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    farms = relationship("Farm", back_populates="owner", cascade="all, delete-orphan")


class VerificationCode(Base):
    __tablename__ = "verification_codes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    code: Mapped[str] = mapped_column(String(12), nullable=False)
    purpose: Mapped[str] = mapped_column(String(40), nullable=False)  # register | reset
    expires_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    used: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class Farm(Base):
    __tablename__ = "farms"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    location: Mapped[str | None] = mapped_column(String(255), nullable=True)
    latitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    longitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    area: Mapped[float | None] = mapped_column(Float, nullable=True)
    soil_type: Mapped[str | None] = mapped_column(String(80), nullable=True)
    irrigation_type: Mapped[str | None] = mapped_column(String(80), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    owner = relationship("User", back_populates="farms")
    crops = relationship("Crop", back_populates="farm", cascade="all, delete-orphan")
    readings = relationship("SensorReading", back_populates="farm", cascade="all, delete-orphan")
    predictions = relationship("Prediction", back_populates="farm", cascade="all, delete-orphan")
    irrigation_events = relationship(
        "IrrigationEvent", back_populates="farm", cascade="all, delete-orphan"
    )
    devices = relationship("Device", back_populates="farm", cascade="all, delete-orphan")
    zones = relationship("ManagementZone", back_populates="farm", cascade="all, delete-orphan")
    lab_reports = relationship("LabReport", back_populates="farm", cascade="all, delete-orphan")
    material_uses = relationship(
        "FarmMaterialUse", back_populates="farm", cascade="all, delete-orphan"
    )
    crop_histories = relationship(
        "CropHistory", back_populates="farm", cascade="all, delete-orphan"
    )


class AgroMaterial(Base):
    """Reference catalog of fertilizer / plant-protection *classes* (not brand Rx)."""

    __tablename__ = "agro_materials"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    code: Mapped[str] = mapped_column(String(40), unique=True, nullable=False, index=True)
    kind: Mapped[str] = mapped_column(String(40), nullable=False, index=True)
    name_tr: Mapped[str] = mapped_column(String(160), nullable=False)
    name_en: Mapped[str | None] = mapped_column(String(160), nullable=True)
    category: Mapped[str] = mapped_column(String(80), nullable=False)
    nutrient_focus: Mapped[str | None] = mapped_column(String(80), nullable=True)
    purpose: Mapped[str] = mapped_column(Text, nullable=False)
    ec_salinity_note: Mapped[str | None] = mapped_column(Text, nullable=True)
    phi_class_note: Mapped[str | None] = mapped_column(Text, nullable=True)
    irrigation_context: Mapped[str | None] = mapped_column(Text, nullable=True)
    sort_order: Mapped[int] = mapped_column(Integer, default=100)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    farm_uses = relationship("FarmMaterialUse", back_populates="material")


class FarmMaterialUse(Base):
    """User association: materials used on this farm (profile, not prescription)."""

    __tablename__ = "farm_material_uses"
    __table_args__ = (
        UniqueConstraint("farm_id", "material_id", name="uq_farm_material"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    farm_id: Mapped[int] = mapped_column(ForeignKey("farms.id"), nullable=False, index=True)
    material_id: Mapped[int] = mapped_column(
        ForeignKey("agro_materials.id"), nullable=False, index=True
    )
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    frequency: Mapped[str | None] = mapped_column(String(40), nullable=True)
    last_applied_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    # At most one last fertilizer and one last pesticide per farm (enforced in service).
    is_last_fertilizer: Mapped[bool] = mapped_column(Boolean, default=False)
    is_last_pesticide: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    farm = relationship("Farm", back_populates="material_uses")
    material = relationship("AgroMaterial", back_populates="farm_uses")


class ManagementZone(Base):
    __tablename__ = "management_zones"
    __table_args__ = (UniqueConstraint("farm_id", "name", name="uq_farm_zone"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    farm_id: Mapped[int] = mapped_column(ForeignKey("farms.id"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    farm = relationship("Farm", back_populates="zones")
    lab_reports = relationship("LabReport", back_populates="zone")


class Crop(Base):
    __tablename__ = "crops"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    farm_id: Mapped[int] = mapped_column(ForeignKey("farms.id"), nullable=False, index=True)
    crop_type: Mapped[str] = mapped_column(String(80), nullable=False)
    planting_date: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    growth_stage: Mapped[str | None] = mapped_column(String(80), nullable=True)

    farm = relationship("Farm", back_populates="crops")


class CropHistory(Base):
    """Past / current planting seasons for a farm (manual farm record)."""

    __tablename__ = "crop_histories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    farm_id: Mapped[int] = mapped_column(ForeignKey("farms.id"), nullable=False, index=True)
    crop_type: Mapped[str] = mapped_column(String(80), nullable=False)
    planting_date: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    harvest_date: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    status: Mapped[CropSeasonStatus] = mapped_column(
        Enum(CropSeasonStatus), nullable=False, default=CropSeasonStatus.growing
    )
    yield_amount: Mapped[float | None] = mapped_column(Float, nullable=True)
    yield_unit: Mapped[str | None] = mapped_column(String(40), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    # Farm record entered by user — not IoT/simulated sensor data
    source_type: Mapped[str] = mapped_column(String(40), nullable=False, default="manual")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    farm = relationship("Farm", back_populates="crop_histories")


class SensorReading(Base):
    __tablename__ = "sensor_readings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    farm_id: Mapped[int] = mapped_column(ForeignKey("farms.id"), nullable=False, index=True)
    zone_id: Mapped[int | None] = mapped_column(ForeignKey("management_zones.id"), nullable=True)
    source_type: Mapped[SourceType] = mapped_column(Enum(SourceType), nullable=False)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
    soil_moisture: Mapped[float] = mapped_column(Float, nullable=False)
    soil_moisture_deep: Mapped[float | None] = mapped_column(Float, nullable=True)
    moisture_depth_cm: Mapped[float | None] = mapped_column(Float, nullable=True)
    moisture_deep_depth_cm: Mapped[float | None] = mapped_column(Float, nullable=True)
    soil_temperature: Mapped[float | None] = mapped_column(Float, nullable=True)
    air_temperature: Mapped[float | None] = mapped_column(Float, nullable=True)
    air_humidity: Mapped[float | None] = mapped_column(Float, nullable=True)
    rainfall_probability: Mapped[float | None] = mapped_column(Float, nullable=True)
    ph: Mapped[float | None] = mapped_column(Float, nullable=True)
    ec: Mapped[float | None] = mapped_column(Float, nullable=True)
    salinity: Mapped[float | None] = mapped_column(Float, nullable=True)
    last_irrigation_hours_ago: Mapped[float | None] = mapped_column(Float, nullable=True)
    irrigation_duration: Mapped[float | None] = mapped_column(Float, nullable=True)
    water_amount: Mapped[float | None] = mapped_column(Float, nullable=True)
    data_confidence: Mapped[float | None] = mapped_column(Float, nullable=True)
    is_validated: Mapped[bool] = mapped_column(Boolean, default=True)
    device_id: Mapped[int | None] = mapped_column(ForeignKey("devices.id"), nullable=True)

    farm = relationship("Farm", back_populates="readings")


class Prediction(Base):
    __tablename__ = "predictions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    farm_id: Mapped[int] = mapped_column(ForeignKey("farms.id"), nullable=False, index=True)
    irrigation_needed: Mapped[bool] = mapped_column(Boolean, nullable=False)
    irrigation_duration: Mapped[float | None] = mapped_column(Float, nullable=True)
    risk_level: Mapped[RiskLevel] = mapped_column(Enum(RiskLevel), nullable=False)
    confidence_score: Mapped[float] = mapped_column(Float, nullable=False)
    explanation: Mapped[str] = mapped_column(Text, nullable=False)
    moisture_24h: Mapped[float | None] = mapped_column(Float, nullable=True)
    moisture_48h: Mapped[float | None] = mapped_column(Float, nullable=True)
    moisture_72h: Mapped[float | None] = mapped_column(Float, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    farm = relationship("Farm", back_populates="predictions")


class IrrigationEvent(Base):
    __tablename__ = "irrigation_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    farm_id: Mapped[int] = mapped_column(ForeignKey("farms.id"), nullable=False, index=True)
    start_time: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    end_time: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    duration: Mapped[float | None] = mapped_column(Float, nullable=True)
    water_amount: Mapped[float | None] = mapped_column(Float, nullable=True)
    status: Mapped[IrrigationStatus] = mapped_column(
        Enum(IrrigationStatus), default=IrrigationStatus.pending
    )

    farm = relationship("Farm", back_populates="irrigation_events")


class Device(Base):
    __tablename__ = "devices"
    __table_args__ = (UniqueConstraint("farm_id", "device_name", name="uq_farm_device"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    farm_id: Mapped[int] = mapped_column(ForeignKey("farms.id"), nullable=False, index=True)
    device_name: Mapped[str] = mapped_column(String(120), nullable=False)
    device_type: Mapped[str] = mapped_column(String(80), nullable=False)
    connection_status: Mapped[str] = mapped_column(String(40), default="active")
    last_data_time: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    serial_number: Mapped[str | None] = mapped_column(String(80), nullable=True)
    zone_id: Mapped[int | None] = mapped_column(ForeignKey("management_zones.id"), nullable=True)
    region_name: Mapped[str | None] = mapped_column(String(120), nullable=True)
    depth_cm: Mapped[int | None] = mapped_column(Integer, nullable=True, default=20)
    connection_type: Mapped[str | None] = mapped_column(String(40), nullable=True, default="wifi")
    battery_percent: Mapped[float | None] = mapped_column(Float, nullable=True)
    signal_dbm: Mapped[int | None] = mapped_column(Integer, nullable=True)
    firmware_version: Mapped[str | None] = mapped_column(String(40), nullable=True)
    installed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    last_calibration_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    calibration_offset: Mapped[float | None] = mapped_column(Float, nullable=True, default=0.0)
    sampling_minutes: Mapped[int | None] = mapped_column(Integer, nullable=True, default=15)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    # JSON list of capability codes, e.g. ["soil_moisture","ec","air_humidity"]
    capabilities: Mapped[str | None] = mapped_column(Text, nullable=True)

    farm = relationship("Farm", back_populates="devices")


class LabReport(Base):
    __tablename__ = "lab_reports"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    farm_id: Mapped[int] = mapped_column(ForeignKey("farms.id"), nullable=False, index=True)
    zone_id: Mapped[int | None] = mapped_column(ForeignKey("management_zones.id"), nullable=True)
    lab_name: Mapped[str] = mapped_column(String(160), nullable=False)
    report_number: Mapped[str | None] = mapped_column(String(80), nullable=True)
    analysis_date: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    sample_date: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    sample_depth_cm: Mapped[str | None] = mapped_column(String(40), nullable=True)
    sample_region: Mapped[str | None] = mapped_column(String(120), nullable=True)
    file_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    source_type: Mapped[LabSourceType] = mapped_column(Enum(LabSourceType), nullable=False)
    user_confirmed: Mapped[bool] = mapped_column(Boolean, default=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    status: Mapped[str | None] = mapped_column(String(40), nullable=True, default="pending")
    extraction_confidence: Mapped[float | None] = mapped_column(Float, nullable=True)

    farm = relationship("Farm", back_populates="lab_reports")
    zone = relationship("ManagementZone", back_populates="lab_reports")
    parameters = relationship(
        "LabParameter", back_populates="report", cascade="all, delete-orphan"
    )


class LabParameter(Base):
    __tablename__ = "lab_parameters"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    report_id: Mapped[int] = mapped_column(ForeignKey("lab_reports.id"), nullable=False, index=True)
    parameter_code: Mapped[str] = mapped_column(String(40), nullable=False)
    value: Mapped[float] = mapped_column(Float, nullable=False)
    unit: Mapped[str] = mapped_column(String(40), nullable=False)
    method: Mapped[str | None] = mapped_column(String(80), nullable=True)
    extracted_auto: Mapped[bool] = mapped_column(Boolean, default=False)
    confidence_pct: Mapped[float | None] = mapped_column(Float, nullable=True)

    report = relationship("LabReport", back_populates="parameters")


class SupportTicket(Base):
    __tablename__ = "support_tickets"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    ticket_no: Mapped[str] = mapped_column(String(40), unique=True, nullable=False, index=True)
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    subject: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    priority: Mapped[str] = mapped_column(String(20), default="medium")  # low/medium/high
    status: Mapped[str] = mapped_column(String(20), default="open")  # open/pending/resolved/closed
    farm_id: Mapped[int | None] = mapped_column(ForeignKey("farms.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class SystemSetting(Base):
    __tablename__ = "system_settings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    key: Mapped[str] = mapped_column(String(80), unique=True, nullable=False, index=True)
    value: Mapped[str] = mapped_column(Text, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
