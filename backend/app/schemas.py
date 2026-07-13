from datetime import datetime
from typing import Literal

from pydantic import BaseModel, EmailStr, Field


SourceTypeLiteral = Literal[
    "manual",
    "simulation",
    "test_dataset",
    "lab_report",
    "lab_manual",
    "iot",
]
RiskLevelLiteral = Literal["low", "medium", "high", "critical"]


class UserCreate(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    email: EmailStr
    phone: str | None = Field(default=None, max_length=32)
    password: str = Field(min_length=8, max_length=128)
    role: str = "farmer"


class UserLogin(BaseModel):
    email: str = Field(min_length=3, max_length=255)  # email or phone
    password: str


class UserOut(BaseModel):
    id: int
    name: str
    email: EmailStr
    phone: str | None = None
    role: str
    email_verified: bool = False
    is_active: bool = True
    last_login_at: datetime | None = None
    created_at: datetime | None = None

    class Config:
        from_attributes = True


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut


class RegisterPendingOut(BaseModel):
    email: EmailStr
    message: str
    demo_code: str | None = None
    expires_in_seconds: int = 600


class VerifyRequest(BaseModel):
    email: EmailStr
    code: str = Field(min_length=4, max_length=12)


class RoleUpdateRequest(BaseModel):
    role: Literal["farmer", "agronomist", "cooperative", "consultant"]


class UserUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=120)
    phone: str | None = Field(default=None, max_length=32)
    current_password: str | None = None
    new_password: str | None = Field(default=None, min_length=8, max_length=128)


class ForgotPasswordRequest(BaseModel):
    email: str = Field(min_length=3, max_length=255)


class ResetPasswordRequest(BaseModel):
    email: EmailStr
    code: str = Field(min_length=4, max_length=12)
    new_password: str = Field(min_length=8, max_length=128)


class MessageOut(BaseModel):
    message: str
    demo_code: str | None = None
    email: EmailStr | None = None


class FarmCreate(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    location: str | None = None
    latitude: float | None = Field(default=None, ge=-90, le=90)
    longitude: float | None = Field(default=None, ge=-180, le=180)
    area: float | None = None
    soil_type: str | None = None
    irrigation_type: str | None = None
    crop_type: str | None = Field(default=None, max_length=80)
    growth_stage: str | None = None


class FarmUpdate(BaseModel):
    name: str | None = None
    location: str | None = None
    latitude: float | None = Field(default=None, ge=-90, le=90)
    longitude: float | None = Field(default=None, ge=-180, le=180)
    area: float | None = None
    soil_type: str | None = None
    irrigation_type: str | None = None
    is_active: bool | None = None
    crop_type: str | None = Field(default=None, max_length=80)
    growth_stage: str | None = None


class CropOut(BaseModel):
    id: int
    crop_type: str
    growth_stage: str | None
    planting_date: datetime | None

    class Config:
        from_attributes = True


class FarmOut(BaseModel):
    id: int
    name: str
    location: str | None
    latitude: float | None = None
    longitude: float | None = None
    area: float | None
    soil_type: str | None
    irrigation_type: str | None
    is_active: bool = True
    created_at: datetime
    crops: list[CropOut] = []
    zone_count: int = 0
    device_count: int = 0

    class Config:
        from_attributes = True


class SensorReadingCreate(BaseModel):
    soil_moisture: float = Field(ge=0, le=100)
    soil_moisture_deep: float | None = Field(default=None, ge=0, le=100)
    moisture_depth_cm: float | None = None
    moisture_deep_depth_cm: float | None = None
    soil_temperature: float | None = None
    air_temperature: float | None = None
    air_humidity: float | None = Field(default=None, ge=0, le=100)
    rainfall_probability: float | None = Field(default=None, ge=0, le=100)
    ph: float | None = Field(default=None, ge=0, le=14)
    ec: float | None = None
    salinity: float | None = None
    last_irrigation_hours_ago: float | None = Field(default=None, ge=0)
    irrigation_duration: float | None = None
    water_amount: float | None = None
    zone_id: int | None = None
    source_type: SourceTypeLiteral = "manual"


class SensorReadingOut(BaseModel):
    id: int
    farm_id: int
    zone_id: int | None = None
    source_type: str
    timestamp: datetime
    soil_moisture: float
    soil_moisture_deep: float | None = None
    moisture_depth_cm: float | None = None
    moisture_deep_depth_cm: float | None = None
    soil_temperature: float | None
    air_temperature: float | None
    air_humidity: float | None
    rainfall_probability: float | None
    ph: float | None
    ec: float | None
    salinity: float | None
    last_irrigation_hours_ago: float | None
    data_confidence: float | None
    is_validated: bool = True

    class Config:
        from_attributes = True


class PredictionOut(BaseModel):
    id: int
    farm_id: int
    irrigation_needed: bool
    irrigation_duration: float | None
    risk_level: RiskLevelLiteral
    confidence_score: float
    explanation: str
    moisture_24h: float | None
    moisture_48h: float | None
    moisture_72h: float | None
    created_at: datetime

    class Config:
        from_attributes = True


RecommendationCategory = Literal[
    "irrigation",
    "moisture_forecast",
    "data_quality",
    "lab_iot_compare",
    "weather_context",
    "climate",
    "other",
]


class RecommendationItemOut(BaseModel):
    id: str
    prediction_id: int | None = None
    category: RecommendationCategory = "irrigation"
    title: str
    summary: str
    priority: Literal["high", "medium", "low"]
    risk_level: RiskLevelLiteral | None = None
    confidence_score: float | None = None
    irrigation_needed: bool | None = None
    created_at: datetime | None = None
    automation_allowed: bool = False


class WeatherOut(BaseModel):
    provider: str = "open-meteo"
    latitude: float
    longitude: float
    coord_source: str | None = None
    location: str | None = None
    temperature_c: float | None = None
    humidity_pct: float | None = None
    precipitation_mm: float | None = None
    precip_probability_pct: float | None = None
    fetched_at: str | None = None
    error: str | None = None
    raw_time: str | None = None


class RecommendationSummaryOut(BaseModel):
    farm_id: int
    total: int
    high: int
    medium: int
    low: int
    items: list[RecommendationItemOut]


class RecommendationDetailOut(BaseModel):
    prediction: PredictionOut
    title: str
    priority: Literal["high", "medium", "low"]
    automation_allowed: bool
    factors: list[str]
    data_sources: list[str]
    current_moisture: float | None = None
    estimated_water_mm: float | None = None
    can_apply: bool
    apply_block_reason: str | None = None


class CustomSimulateRequest(BaseModel):
    farm_id: int
    duration_minutes: float = Field(default=60, ge=1, le=180)
    water_amount_liters: float | None = Field(default=None, ge=0)
    target_moisture: float | None = Field(default=None, ge=0, le=100)
    name: str | None = Field(default=None, max_length=120)


class ForecastPointOut(BaseModel):
    day: int
    current_path: float
    scenario_path: float
    critical_level: float = 20.0


class CustomSimulateOut(BaseModel):
    farm_id: int
    name: str | None
    current_moisture: float
    estimated_moisture: float
    estimated_water_liters: float
    estimated_water_mm: float
    estimated_cost_try: float
    duration_minutes: float
    risk_level: RiskLevelLiteral
    plant_stress: str
    forecast: list[ForecastPointOut]
    explanation: str


class HubAlertOut(BaseModel):
    code: str
    severity: str
    title: str
    message: str


class HubReportOut(BaseModel):
    key: str
    title: str
    description: str
    available: bool
    record_count: int = 0
    metric_label: str | None = None
    metric_value: str | None = None


class HubOut(BaseModel):
    farm_id: int
    farm_name: str
    alerts: list[HubAlertOut]
    alert_counts: dict[str, int]
    reports: list[HubReportOut]
    settings: dict[str, str | int | float | bool | None]
    note: str
    water_used_liters: float | None = None
    water_savings_liters: float | None = None
    water_savings_pct: float | None = None
    water_usage_note: str | None = None


class PredictRequest(BaseModel):
    farm_id: int


class DeviceCreate(BaseModel):
    farm_id: int
    device_name: str = Field(min_length=1, max_length=120)
    device_type: str = Field(min_length=1, max_length=80)
    serial_number: str | None = Field(default=None, max_length=80)
    zone_id: int | None = None
    region_name: str | None = Field(default=None, max_length=120)
    depth_cm: int | None = Field(default=20, ge=5, le=120)
    connection_type: str | None = Field(default="wifi", max_length=40)
    sampling_minutes: int | None = Field(default=15, ge=1, le=1440)
    notes: str | None = None
    api_key: str | None = None


class DeviceUpdate(BaseModel):
    device_name: str | None = Field(default=None, min_length=1, max_length=120)
    device_type: str | None = Field(default=None, min_length=1, max_length=80)
    serial_number: str | None = Field(default=None, max_length=80)
    zone_id: int | None = None
    region_name: str | None = Field(default=None, max_length=120)
    depth_cm: int | None = Field(default=None, ge=5, le=120)
    connection_type: str | None = Field(default=None, max_length=40)
    connection_status: str | None = Field(default=None, max_length=40)
    sampling_minutes: int | None = Field(default=None, ge=1, le=1440)
    notes: str | None = None


class DeviceOut(BaseModel):
    id: int
    farm_id: int
    device_name: str
    device_type: str
    connection_status: str
    last_data_time: datetime | None
    serial_number: str | None = None
    zone_id: int | None = None
    region_name: str | None = None
    depth_cm: int | None = None
    connection_type: str | None = None
    battery_percent: float | None = None
    signal_dbm: int | None = None
    firmware_version: str | None = None
    installed_at: datetime | None = None
    last_calibration_at: datetime | None = None
    calibration_offset: float | None = None
    sampling_minutes: int | None = None
    notes: str | None = None
    last_moisture: float | None = None
    calibration_due: bool = False
    source_label: str = "simulation"

    class Config:
        from_attributes = True


class DeviceSummaryOut(BaseModel):
    farm_id: int
    total: int
    online: int
    warning: int
    offline: int
    calibration_pending: int
    online_percent: float


class DeviceDetailOut(BaseModel):
    device: DeviceOut
    recent_readings: list[SensorReadingOut]
    events: list[str]


class DeviceCalibrateRequest(BaseModel):
    reference_value: float = Field(ge=0, le=100)
    raw_value: float | None = Field(default=None, ge=0, le=100)


class DeviceCalibrateOut(BaseModel):
    device_id: int
    raw_value: float
    reference_value: float
    deviation: float
    status: str
    calibration_offset: float
    last_calibration_at: datetime
    message: str


class DeviceTestRequest(BaseModel):
    device_id: int


class DeviceTestOut(BaseModel):
    device_id: int
    connection_status: str
    message: str
    last_data_time: datetime | None
    signal_dbm: int | None = None
    battery_percent: float | None = None


class IoTSimulateRequest(BaseModel):
    farm_id: int
    scenario: str = "drought_risk"
    device_id: int | None = None


class DatasetInfoOut(BaseModel):
    id: str
    name: str
    description: str | None = None


class DatasetLoadRequest(BaseModel):
    farm_id: int
    scenario: str = "drought_risk"
    zone_id: int | None = None


ScenarioType = Literal[
    "irrigate_now",
    "wait_12h",
    "wait_24h",
    "skip",
    "reduce_duration",
    "increase_duration",
]


class ScenarioSimulateRequest(BaseModel):
    farm_id: int
    scenarios: list[ScenarioType] = Field(
        default_factory=lambda: ["irrigate_now", "wait_24h"]
    )
    duration_minutes: float | None = Field(default=None, ge=1, le=120)


class ScenarioResultOut(BaseModel):
    scenario: ScenarioType
    label: str
    estimated_moisture: float
    estimated_water_liters: float | None
    risk_level: RiskLevelLiteral
    plant_stress: str
    recommended: bool
    explanation: str


class ScenarioCompareOut(BaseModel):
    farm_id: int
    current_moisture: float
    recommended_scenario: ScenarioType
    results: list[ScenarioResultOut]


IrrigationStatusLiteral = Literal["pending", "running", "completed", "stopped"]


class IrrigationStartRequest(BaseModel):
    farm_id: int
    user_approved: bool = False
    duration_minutes: float | None = Field(default=None, ge=1, le=120)
    virtual_session: bool = False


class IrrigationStopRequest(BaseModel):
    farm_id: int
    event_id: int | None = None


class IrrigationEventOut(BaseModel):
    id: int
    farm_id: int
    start_time: datetime
    end_time: datetime | None
    duration: float | None
    water_amount: float | None
    status: IrrigationStatusLiteral
    valve_status: str

    class Config:
        from_attributes = True


class IrrigationStartOut(BaseModel):
    event: IrrigationEventOut
    updated_moisture: float
    prediction: PredictionOut
    message: str


class ZoneCreate(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    farm_id: int
    notes: str | None = None


class ZoneUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=120)
    notes: str | None = None


class ZoneOut(BaseModel):
    id: int
    farm_id: int
    name: str
    notes: str | None
    created_at: datetime

    class Config:
        from_attributes = True


class LabParameterIn(BaseModel):
    parameter_code: str = Field(min_length=1, max_length=40)
    value: float
    unit: str = Field(min_length=1, max_length=40)
    method: str | None = None
    extracted_auto: bool = False
    confidence_pct: float | None = Field(default=None, ge=0, le=100)


class LabReportCreate(BaseModel):
    farm_id: int
    zone_id: int | None = None
    lab_name: str = Field(min_length=1, max_length=160)
    report_number: str | None = None
    analysis_date: datetime | None = None
    sample_date: datetime | None = None
    sample_depth_cm: str | None = None
    sample_region: str | None = None
    file_name: str | None = None
    source_type: Literal["lab_report", "lab_manual"] = "lab_manual"
    user_confirmed: bool = False
    notes: str | None = None
    parameters: list[LabParameterIn] = Field(min_length=1)
    extraction_confidence: float | None = Field(default=None, ge=0, le=100)


class LabParameterOut(BaseModel):
    id: int
    parameter_code: str
    value: float
    unit: str
    method: str | None
    extracted_auto: bool
    confidence_pct: float | None = None

    class Config:
        from_attributes = True


class LabReportOut(BaseModel):
    id: int
    farm_id: int
    zone_id: int | None
    lab_name: str
    report_number: str | None
    analysis_date: datetime | None
    sample_date: datetime | None
    sample_depth_cm: str | None
    sample_region: str | None
    file_name: str | None
    source_type: Literal["lab_report", "lab_manual"]
    user_confirmed: bool
    notes: str | None
    created_at: datetime
    status: str | None = None
    extraction_confidence: float | None = None
    parameters: list[LabParameterOut] = []
    critical_count: int = 0
    ph: float | None = None
    ec: float | None = None
    om: float | None = None

    class Config:
        from_attributes = True


class LabConfirmRequest(BaseModel):
    confirmed: bool = True
    parameters: list[LabParameterIn] | None = None


class LabReportUpdate(BaseModel):
    lab_name: str | None = Field(default=None, min_length=1, max_length=160)
    report_number: str | None = None
    analysis_date: datetime | None = None
    sample_date: datetime | None = None
    sample_depth_cm: str | None = None
    sample_region: str | None = None
    zone_id: int | None = None
    file_name: str | None = None
    notes: str | None = None
    parameters: list[LabParameterIn] | None = None


class LabSummaryOut(BaseModel):
    farm_id: int
    total: int
    pending: int
    verified: int
    missing: int
    last_30_days: int
    critical_findings: int


class LabInsightOut(BaseModel):
    parameter_code: str
    label: str
    value: float
    unit: str
    status_label: str
    tone: str
    risk: str
    message: str


class LabDetailOut(BaseModel):
    report: LabReportOut
    insights: list[LabInsightOut]
    ai_summary: str
    source_note: str


class LabExtractDemoOut(BaseModel):
    parameters: list[LabParameterIn]
    extraction_confidence: float
    message: str


class IoTIngestMeasurement(BaseModel):
    value: float
    unit: str


class IoTIngestRequest(BaseModel):
    device_id: str
    farm_id: int
    zone_id: int | None = None
    timestamp: datetime | None = None
    simulation: bool = False
    measurements: dict[str, IoTIngestMeasurement]
    battery: float | None = None
    signal_quality: float | None = None
    status: str = "normal"


class FarmOverviewOut(BaseModel):
    farm: FarmOut
    latest_reading: SensorReadingOut | None = None
    latest_prediction: PredictionOut | None = None
    zone_names: list[str] = []
    anomaly_count: int = 0
    open_irrigation: bool = False
    water_used_liters: float | None = None
    water_savings_liters: float | None = None
    water_savings_pct: float | None = None
    water_usage_note: str | None = None


class DataSourceOut(BaseModel):
    key: str
    name: str
    source_type: str
    status: Literal["active", "pending", "offline"]
    last_update: datetime | None = None
    record_count: int = 0
    trust_score: float | None = None
    detail: str | None = None


class TwinZoneOut(BaseModel):
    id: int | None = None
    name: str
    soil_moisture: float | None = None
    soil_temperature: float | None = None
    air_temperature: float | None = None
    air_humidity: float | None = None
    ec: float | None = None
    risk: str = "unknown"


class TwinViewOut(BaseModel):
    farm: FarmOut
    zones: list[TwinZoneOut]
    latest_reading: SensorReadingOut | None = None
    latest_prediction: PredictionOut | None = None
    source_label: str | None = None
    confidence: float | None = None
    insight: str | None = None


class ReadingSeriesStats(BaseModel):
    metric: str
    count: int
    avg: float | None = None
    min: float | None = None
    max: float | None = None
    points: list[SensorReadingOut] = []


class AdminUserOut(BaseModel):
    id: int
    name: str
    email: EmailStr
    phone: str | None = None
    role: str
    is_active: bool = True
    email_verified: bool = False
    farm_count: int = 0
    last_login_at: datetime | None = None
    created_at: datetime | None = None


class AdminUserUpdate(BaseModel):
    role: str | None = None
    is_active: bool | None = None
    name: str | None = Field(default=None, min_length=2, max_length=120)


class AdminFarmOut(BaseModel):
    id: int
    name: str
    location: str | None = None
    area: float | None = None
    soil_type: str | None = None
    is_active: bool = True
    owner_id: int
    owner_name: str
    owner_email: str
    device_count: int = 0
    zone_count: int = 0
    created_at: datetime | None = None


class AdminFarmUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=120)
    location: str | None = None
    area: float | None = None
    soil_type: str | None = None
    irrigation_type: str | None = None
    is_active: bool | None = None


class AdminDeviceOut(BaseModel):
    id: int
    farm_id: int
    farm_name: str
    device_name: str
    device_type: str
    serial_number: str | None = None
    connection_status: str
    battery_percent: float | None = None
    signal_dbm: int | None = None
    last_data_time: datetime | None = None
    last_moisture: float | None = None
    calibration_due: bool = False


class AdminDeviceUpdate(BaseModel):
    connection_status: str | None = Field(default=None, max_length=40)
    battery_percent: float | None = Field(default=None, ge=0, le=100)
    signal_dbm: int | None = None
    notes: str | None = None
    device_name: str | None = Field(default=None, min_length=1, max_length=120)


class AdminOverviewOut(BaseModel):
    total_users: int
    active_users: int
    admin_users: int
    total_farms: int
    active_farms: int
    total_devices: int
    online_devices: int
    offline_devices: int
    avg_soil_moisture: float | None
    open_tickets: int
    system_health_pct: float
    recent_alerts: list[dict]
    recent_activity: list[str]
    note: str


class TicketCreate(BaseModel):
    subject: str = Field(min_length=3, max_length=200)
    description: str | None = None
    priority: Literal["low", "medium", "high"] = "medium"
    farm_id: int | None = None


class TicketUpdate(BaseModel):
    status: Literal["open", "pending", "resolved", "closed"] | None = None
    priority: Literal["low", "medium", "high"] | None = None
    subject: str | None = Field(default=None, min_length=3, max_length=200)


class TicketOut(BaseModel):
    id: int
    ticket_no: str
    user_id: int | None
    subject: str
    description: str | None
    priority: str
    status: str
    farm_id: int | None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class BillingOut(BaseModel):
    plan: str
    status: str
    farms_used: int
    farms_limit: int
    devices_used: int
    devices_limit: int | None
    storage_used_gb: float
    storage_limit_gb: float
    ai_queries_used: int
    ai_queries_limit: int
    plans: list[dict]
    invoices: list[dict]
    note: str


class AdminAnalyticsOut(BaseModel):
    avg_moisture: float | None
    avg_temperature: float | None
    irrigation_events: int
    predictions: int
    lab_reports: int
    moisture_series: list[dict]
    water_by_day: list[dict]
    feature_usage: list[dict]
    note: str


class AdminSettingsOut(BaseModel):
    settings: dict[str, str]
    integrations: list[dict]
    note: str


class AdminSettingsUpdate(BaseModel):
    settings: dict[str, str]
