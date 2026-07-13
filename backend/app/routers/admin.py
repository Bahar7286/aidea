"""Admin panel APIs (A01–A08). Aggregates platform data; billing is MVP demo."""

from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.database import get_db
from app.deps import ADMIN_ROLES, require_admin
from app.models import (
    Device,
    Farm,
    IrrigationEvent,
    LabReport,
    ManagementZone,
    Prediction,
    SensorReading,
    SupportTicket,
    SystemSetting,
    User,
)
from app.schemas import (
    AdminAnalyticsOut,
    AdminDeviceOut,
    AdminDeviceUpdate,
    AdminFarmOut,
    AdminFarmUpdate,
    AdminOverviewOut,
    AdminSettingsOut,
    AdminSettingsUpdate,
    AdminUserOut,
    AdminUserUpdate,
    BillingOut,
    TicketCreate,
    TicketOut,
    TicketUpdate,
    UserOut,
)

router = APIRouter(prefix="/admin", tags=["admin"])

DEFAULT_SETTINGS = {
    "system_name": "AgriTwin AI",
    "language": "tr",
    "timezone": "Europe/Istanbul",
    "currency": "TRY",
    "date_format": "DD.MM.YYYY",
    "maintenance_mode": "false",
    "auto_backup": "true",
    "session_timeout_min": "30",
    "notify_email": "true",
    "notify_irrigation": "true",
    "critical_moisture_pct": "20",
}


def _admin(user: User = Depends(get_current_user)) -> User:
    return require_admin(user)


@router.post("/bootstrap", response_model=UserOut)
def bootstrap_admin(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Promote current user to admin if no admin exists yet (MVP bootstrap)."""
    existing = (
        db.query(User)
        .filter(User.role.in_(list(ADMIN_ROLES)))
        .count()
    )
    if existing > 0 and current_user.role not in ADMIN_ROLES:
        raise HTTPException(
            status_code=403,
            detail="Zaten bir yönetici var. Yalnızca mevcut admin yetki verebilir.",
        )
    current_user.role = "admin"
    current_user.is_active = True
    db.commit()
    db.refresh(current_user)
    return UserOut.model_validate(current_user)


@router.get("/overview", response_model=AdminOverviewOut)
def admin_overview(
    db: Session = Depends(get_db),
    _: User = Depends(_admin),
):
    users = db.query(User).all()
    farms = db.query(Farm).all()
    devices = db.query(Device).all()
    total_users = len(users)
    active_users = sum(1 for u in users if getattr(u, "is_active", True))
    admin_users = sum(1 for u in users if u.role in ADMIN_ROLES)
    total_farms = len(farms)
    active_farms = sum(1 for f in farms if getattr(f, "is_active", True) is not False)
    online = sum(
        1
        for d in devices
        if (d.connection_status or "").lower() in {"active", "online", "normal"}
    )
    offline = len(devices) - online

    avg_row = db.query(func.avg(SensorReading.soil_moisture)).scalar()
    open_tickets = (
        db.query(SupportTicket)
        .filter(SupportTicket.status.in_(["open", "pending"]))
        .count()
    )

    health = 100.0
    if devices:
        health = round(max(70.0, 100.0 * online / max(len(devices), 1)), 1)
    if open_tickets > 5:
        health = max(70.0, health - 5)

    preds = (
        db.query(Prediction)
        .order_by(Prediction.created_at.desc())
        .limit(5)
        .all()
    )
    alerts = []
    for p in preds:
        if p.irrigation_needed or p.risk_level.value in {"high", "critical"}:
            farm = next((f for f in farms if f.id == p.farm_id), None)
            alerts.append(
                {
                    "title": f"{farm.name if farm else 'Arazi'} — nem riski",
                    "severity": p.risk_level.value,
                    "message": p.explanation[:120],
                }
            )

    low_batt = [
        d for d in devices if d.battery_percent is not None and d.battery_percent < 20
    ]
    for d in low_batt[:3]:
        alerts.append(
            {
                "title": f"{d.device_name} — düşük pil",
                "severity": "medium",
                "message": f"Pil %{d.battery_percent:.0f}",
            }
        )

    activity: list[str] = []
    for u in sorted(users, key=lambda x: x.created_at or datetime.min, reverse=True)[:5]:
        activity.append(f"{u.name} kayıt oldu ({u.role})")
    for f in sorted(farms, key=lambda x: x.created_at or datetime.min, reverse=True)[:5]:
        activity.append(f"Arazi eklendi: {f.name}")

    return AdminOverviewOut(
        total_users=total_users,
        active_users=active_users,
        admin_users=admin_users,
        total_farms=total_farms,
        active_farms=active_farms,
        total_devices=len(devices),
        online_devices=online,
        offline_devices=max(0, offline),
        avg_soil_moisture=round(float(avg_row), 1) if avg_row is not None else None,
        open_tickets=open_tickets,
        system_health_pct=health,
        recent_alerts=alerts[:8],
        recent_activity=activity[:10],
        note="Yönetim paneli gerçek platform KPI’larıdır; abonelik gelirleri MVP’de demo alanıdır.",
    )


@router.get("/users", response_model=list[AdminUserOut])
def admin_list_users(
    q: str | None = None,
    status_filter: str | None = Query(default=None, alias="status"),
    role: str | None = None,
    db: Session = Depends(get_db),
    _: User = Depends(_admin),
):
    rows = db.query(User).order_by(User.created_at.desc()).all()
    out: list[AdminUserOut] = []
    for u in rows:
        farms = db.query(Farm).filter(Farm.user_id == u.id).count()
        active = getattr(u, "is_active", True)
        if status_filter == "active" and not active:
            continue
        if status_filter == "passive" and active:
            continue
        if status_filter == "pending" and u.email_verified:
            continue
        if role and u.role != role:
            continue
        if q:
            needle = q.lower()
            if needle not in u.name.lower() and needle not in u.email.lower():
                continue
        out.append(
            AdminUserOut(
                id=u.id,
                name=u.name,
                email=u.email,
                phone=u.phone,
                role=u.role,
                is_active=bool(active),
                email_verified=bool(u.email_verified),
                farm_count=farms,
                last_login_at=getattr(u, "last_login_at", None),
                created_at=u.created_at,
            )
        )
    return out


@router.patch("/users/{user_id}", response_model=AdminUserOut)
def admin_update_user(
    user_id: int,
    payload: AdminUserUpdate,
    db: Session = Depends(get_db),
    admin: User = Depends(_admin),
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Kullanıcı bulunamadı.")
    allowed = {
        "farmer",
        "agronomist",
        "cooperative",
        "consultant",
        "admin",
        "super_admin",
        "operator",
    }
    if payload.role is not None:
        if payload.role not in allowed:
            raise HTTPException(status_code=400, detail="Geçersiz rol.")
        if user.id == admin.id and payload.role not in ADMIN_ROLES:
            raise HTTPException(
                status_code=400,
                detail="Kendi yönetici rolünüzü kaldıramazsınız.",
            )
        user.role = payload.role
    if payload.is_active is not None:
        if user.id == admin.id and payload.is_active is False:
            raise HTTPException(status_code=400, detail="Kendinizi pasifleştiremezsiniz.")
        user.is_active = payload.is_active
    if payload.name is not None:
        user.name = payload.name
    db.commit()
    db.refresh(user)
    farms = db.query(Farm).filter(Farm.user_id == user.id).count()
    return AdminUserOut(
        id=user.id,
        name=user.name,
        email=user.email,
        phone=user.phone,
        role=user.role,
        is_active=bool(getattr(user, "is_active", True)),
        email_verified=bool(user.email_verified),
        farm_count=farms,
        last_login_at=getattr(user, "last_login_at", None),
        created_at=user.created_at,
    )


@router.get("/farms", response_model=list[AdminFarmOut])
def admin_list_farms(
    q: str | None = None,
    status_filter: str | None = Query(default=None, alias="status"),
    db: Session = Depends(get_db),
    _: User = Depends(_admin),
):
    farms = db.query(Farm).order_by(Farm.created_at.desc()).all()
    out: list[AdminFarmOut] = []
    for f in farms:
        owner = db.query(User).filter(User.id == f.user_id).first()
        active = getattr(f, "is_active", True) is not False
        if status_filter == "active" and not active:
            continue
        if status_filter == "passive" and active:
            continue
        if q:
            needle = q.lower()
            blob = f"{f.name} {f.location or ''} {owner.name if owner else ''}".lower()
            if needle not in blob:
                continue
        devices = db.query(Device).filter(Device.farm_id == f.id).count()
        zones = db.query(ManagementZone).filter(ManagementZone.farm_id == f.id).count()
        out.append(
            AdminFarmOut(
                id=f.id,
                name=f.name,
                location=f.location,
                area=f.area,
                soil_type=f.soil_type,
                is_active=active,
                owner_id=f.user_id,
                owner_name=owner.name if owner else "—",
                owner_email=owner.email if owner else "—",
                device_count=devices,
                zone_count=zones,
                created_at=f.created_at,
            )
        )
    return out


def _admin_farm_out(db: Session, farm: Farm) -> AdminFarmOut:
    owner = db.query(User).filter(User.id == farm.user_id).first()
    devices = db.query(Device).filter(Device.farm_id == farm.id).count()
    zones = db.query(ManagementZone).filter(ManagementZone.farm_id == farm.id).count()
    return AdminFarmOut(
        id=farm.id,
        name=farm.name,
        location=farm.location,
        area=farm.area,
        soil_type=farm.soil_type,
        is_active=getattr(farm, "is_active", True) is not False,
        owner_id=farm.user_id,
        owner_name=owner.name if owner else "—",
        owner_email=owner.email if owner else "—",
        device_count=devices,
        zone_count=zones,
        created_at=farm.created_at,
    )


@router.patch("/farms/{farm_id}", response_model=AdminFarmOut)
def admin_update_farm(
    farm_id: int,
    payload: AdminFarmUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(_admin),
):
    farm = db.query(Farm).filter(Farm.id == farm_id).first()
    if not farm:
        raise HTTPException(status_code=404, detail="Arazi bulunamadı.")
    data = payload.model_dump(exclude_unset=True)
    for key, value in data.items():
        setattr(farm, key, value)
    db.commit()
    db.refresh(farm)
    return _admin_farm_out(db, farm)


@router.get("/devices", response_model=list[AdminDeviceOut])
def admin_list_devices(
    q: str | None = None,
    status_filter: str | None = Query(default=None, alias="status"),
    db: Session = Depends(get_db),
    _: User = Depends(_admin),
):
    devices = db.query(Device).order_by(Device.id.desc()).all()
    out: list[AdminDeviceOut] = []
    for d in devices:
        farm = db.query(Farm).filter(Farm.id == d.farm_id).first()
        st = (d.connection_status or "active").lower()
        online = st in {"active", "online", "normal"}
        if status_filter == "online" and not online:
            continue
        if status_filter == "offline" and online:
            continue
        if q:
            needle = q.lower()
            blob = f"{d.device_name} {d.serial_number or ''} {farm.name if farm else ''}".lower()
            if needle not in blob:
                continue
        last = (
            db.query(SensorReading)
            .filter(SensorReading.device_id == d.id)
            .order_by(SensorReading.timestamp.desc())
            .first()
        )
        cal_due = d.last_calibration_at is None or (
            d.last_calibration_at < datetime.utcnow() - timedelta(days=90)
        )
        out.append(
            AdminDeviceOut(
                id=d.id,
                farm_id=d.farm_id,
                farm_name=farm.name if farm else "—",
                device_name=d.device_name,
                device_type=d.device_type,
                serial_number=d.serial_number,
                connection_status=d.connection_status,
                battery_percent=d.battery_percent,
                signal_dbm=d.signal_dbm,
                last_data_time=d.last_data_time,
                last_moisture=last.soil_moisture if last else None,
                calibration_due=cal_due,
            )
        )
    return out


def _admin_device_out(db: Session, device: Device) -> AdminDeviceOut:
    farm = db.query(Farm).filter(Farm.id == device.farm_id).first()
    last = (
        db.query(SensorReading)
        .filter(SensorReading.device_id == device.id)
        .order_by(SensorReading.timestamp.desc())
        .first()
    )
    cal_due = device.last_calibration_at is None or (
        device.last_calibration_at < datetime.utcnow() - timedelta(days=90)
    )
    return AdminDeviceOut(
        id=device.id,
        farm_id=device.farm_id,
        farm_name=farm.name if farm else "—",
        device_name=device.device_name,
        device_type=device.device_type,
        serial_number=device.serial_number,
        connection_status=device.connection_status,
        battery_percent=device.battery_percent,
        signal_dbm=device.signal_dbm,
        last_data_time=device.last_data_time,
        last_moisture=last.soil_moisture if last else None,
        calibration_due=cal_due,
    )


@router.patch("/devices/{device_id}", response_model=AdminDeviceOut)
def admin_update_device(
    device_id: int,
    payload: AdminDeviceUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(_admin),
):
    device = db.query(Device).filter(Device.id == device_id).first()
    if not device:
        raise HTTPException(status_code=404, detail="Cihaz bulunamadı.")
    data = payload.model_dump(exclude_unset=True)
    if "connection_status" in data and data["connection_status"]:
        raw = data["connection_status"].lower().strip()
        if raw in {"active", "online", "aktif", "normal"}:
            data["connection_status"] = "active"
        elif raw in {"warning", "uyari", "uyarı", "alert"}:
            data["connection_status"] = "warning"
        elif raw in {"offline", "cevrimdisi", "çevrimdışı", "inactive"}:
            data["connection_status"] = "offline"
    for key, value in data.items():
        setattr(device, key, value)
    db.commit()
    db.refresh(device)
    return _admin_device_out(db, device)


@router.get("/billing", response_model=BillingOut)
def admin_billing(
    db: Session = Depends(get_db),
    _: User = Depends(_admin),
):
    farms = db.query(Farm).count()
    devices = db.query(Device).count()
    preds = db.query(Prediction).count()
    plan = "professional" if farms > 3 or devices > 10 else "starter"
    plans = [
        {
            "id": "starter",
            "name": "Başlangıç",
            "price_try": 0,
            "farms": 5,
            "devices": 20,
            "features": ["Temel AI", "Manuel veri"],
        },
        {
            "id": "professional",
            "name": "Profesyonel",
            "price_try": 1790,
            "farms": 100,
            "devices": None,
            "features": ["Sınırsız sensör", "Senaryo", "7/24 destek"],
            "current": plan == "professional",
        },
        {
            "id": "corporate",
            "name": "Kurumsal",
            "price_try": 4990,
            "farms": 500,
            "devices": None,
            "features": ["Çoklu organizasyon", "SLA"],
        },
    ]
    return BillingOut(
        plan=plan,
        status="active",
        farms_used=farms,
        farms_limit=100 if plan == "professional" else 5,
        devices_used=devices,
        devices_limit=None if plan != "starter" else 20,
        storage_used_gb=round(0.12 * max(farms, 1), 1),
        storage_limit_gb=500,
        ai_queries_used=preds,
        ai_queries_limit=5000,
        plans=plans,
        invoices=[
            {
                "no": "INV-DEMO-001",
                "date": datetime.utcnow().date().isoformat(),
                "amount": 1788.0,
                "status": "paid",
            }
        ],
        note="Abonelik/fatura MVP demo verisidir; gerçek ödeme entegre değildir.",
    )


@router.get("/tickets", response_model=list[TicketOut])
def list_tickets(
    status_filter: str | None = Query(default=None, alias="status"),
    db: Session = Depends(get_db),
    _: User = Depends(_admin),
):
    q = db.query(SupportTicket).order_by(SupportTicket.created_at.desc())
    if status_filter and status_filter not in {"all", "tumu"}:
        q = q.filter(SupportTicket.status == status_filter)
    return [TicketOut.model_validate(t) for t in q.all()]


@router.post("/tickets", response_model=TicketOut, status_code=201)
def create_ticket(
    payload: TicketCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Any logged-in user can open a ticket; listing is admin-only."""
    n = db.query(SupportTicket).count() + 1
    ticket = SupportTicket(
        ticket_no=f"TK-{datetime.utcnow().year}-{n:04d}",
        user_id=current_user.id,
        subject=payload.subject,
        description=payload.description,
        priority=payload.priority,
        status="open",
        farm_id=payload.farm_id,
    )
    db.add(ticket)
    db.commit()
    db.refresh(ticket)
    return TicketOut.model_validate(ticket)


@router.patch("/tickets/{ticket_id}", response_model=TicketOut)
def update_ticket(
    ticket_id: int,
    payload: TicketUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(_admin),
):
    ticket = db.query(SupportTicket).filter(SupportTicket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Talep bulunamadı.")
    data = payload.model_dump(exclude_unset=True)
    for k, v in data.items():
        setattr(ticket, k, v)
    ticket.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(ticket)
    return TicketOut.model_validate(ticket)


@router.delete("/tickets/{ticket_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_ticket(
    ticket_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(_admin),
):
    ticket = db.query(SupportTicket).filter(SupportTicket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Talep bulunamadı.")
    db.delete(ticket)
    db.commit()
    return None


@router.get("/analytics", response_model=AdminAnalyticsOut)
def admin_analytics(
    days: int = Query(default=30, ge=7, le=365),
    db: Session = Depends(get_db),
    _: User = Depends(_admin),
):
    cutoff = datetime.utcnow() - timedelta(days=days)
    readings = (
        db.query(SensorReading)
        .filter(SensorReading.timestamp >= cutoff)
        .order_by(SensorReading.timestamp.asc())
        .limit(500)
        .all()
    )
    moist = [r.soil_moisture for r in readings]
    temps = [r.air_temperature for r in readings if r.air_temperature is not None]
    irr = (
        db.query(IrrigationEvent)
        .filter(IrrigationEvent.start_time >= cutoff)
        .all()
    )
    # Moisture series by day
    by_day: dict[str, list[float]] = {}
    for r in readings:
        key = r.timestamp.date().isoformat()
        by_day.setdefault(key, []).append(r.soil_moisture)
    moisture_series = [
        {"date": k, "avg": round(sum(v) / len(v), 1)} for k, v in sorted(by_day.items())
    ]
    water_by_day: dict[str, float] = {}
    for e in irr:
        key = (e.start_time or datetime.utcnow()).date().isoformat()
        water_by_day[key] = water_by_day.get(key, 0) + float(e.water_amount or 0)
    water_series = [{"date": k, "liters": round(v, 1)} for k, v in sorted(water_by_day.items())]

    return AdminAnalyticsOut(
        avg_moisture=round(sum(moist) / len(moist), 1) if moist else None,
        avg_temperature=round(sum(temps) / len(temps), 1) if temps else None,
        irrigation_events=len(irr),
        predictions=db.query(Prediction).filter(Prediction.created_at >= cutoff).count(),
        lab_reports=db.query(LabReport).filter(LabReport.created_at >= cutoff).count(),
        moisture_series=moisture_series[-30:],
        water_by_day=water_series[-30:],
        feature_usage=[
            {"feature": "AI tahmin", "count": db.query(Prediction).count()},
            {"feature": "Sanal sulama", "count": db.query(IrrigationEvent).count()},
            {"feature": "Lab rapor", "count": db.query(LabReport).count()},
            {"feature": "Cihaz", "count": db.query(Device).count()},
        ],
        note="Analitik gerçek DB kayıtlarından; gelir/harita alanları demo değildir bu endpoint’te.",
    )


def _load_settings(db: Session) -> dict[str, str]:
    rows = db.query(SystemSetting).all()
    data = dict(DEFAULT_SETTINGS)
    for r in rows:
        data[r.key] = r.value
    return data


@router.get("/settings", response_model=AdminSettingsOut)
def get_settings(
    db: Session = Depends(get_db),
    _: User = Depends(_admin),
):
    return AdminSettingsOut(
        settings=_load_settings(db),
        integrations=[
            {"name": "Weather API", "status": "demo", "connected": False},
            {"name": "Supabase", "status": "optional", "connected": False},
            {"name": "MQTT / IoT Gateway", "status": "simulation", "connected": True},
        ],
        note="Entegrasyonlar MVP’de yapılandırma önizlemesidir; gerçek 3. parti bağ yok.",
    )


@router.put("/settings", response_model=AdminSettingsOut)
def update_settings(
    payload: AdminSettingsUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(_admin),
):
    for key, value in payload.settings.items():
        row = db.query(SystemSetting).filter(SystemSetting.key == key).first()
        if row:
            row.value = str(value)
            row.updated_at = datetime.utcnow()
        else:
            db.add(SystemSetting(key=key, value=str(value)))
    db.commit()
    return AdminSettingsOut(
        settings=_load_settings(db),
        integrations=[
            {"name": "Weather API", "status": "demo", "connected": False},
            {"name": "Supabase", "status": "optional", "connected": False},
            {"name": "MQTT / IoT Gateway", "status": "simulation", "connected": True},
        ],
        note="Entegrasyonlar MVP’de yapılandırma önizlemesidir; gerçek 3. parti bağ yok.",
    )
