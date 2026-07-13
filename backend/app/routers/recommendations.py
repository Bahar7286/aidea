"""AI recommendation list/detail + farm hub (reports/alerts/settings)."""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.anomaly_service import collect_farm_anomalies
from app.auth import get_current_user
from app.database import get_db
from app.deps import get_owned_farm
from app.models import (
    IrrigationEvent,
    IrrigationStatus,
    LabReport,
    Prediction,
    SensorReading,
    User,
)
from app.schemas import (
    HubAlertOut,
    HubOut,
    HubReportOut,
    PredictionOut,
    RecommendationDetailOut,
    RecommendationItemOut,
    RecommendationSummaryOut,
)
from app.water_report import compute_water_usage

router = APIRouter(tags=["recommendations-hub"])

MIN_CONFIDENCE = 60.0


def _priority(risk: str) -> str:
    if risk in {"critical", "high"}:
        return "high"
    if risk == "medium":
        return "medium"
    return "low"


def _title(pred: Prediction) -> str:
    if pred.irrigation_needed:
        return "Sulama zamanı önerisi"
    if pred.risk_level.value in {"high", "critical"}:
        return "Nem riski uyarısı"
    return "Sulama durumu stabil"


@router.get(
    "/recommendations/detail/{prediction_id}",
    response_model=RecommendationDetailOut,
)
def recommendation_detail(
    prediction_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    pred = db.query(Prediction).filter(Prediction.id == prediction_id).first()
    if not pred:
        raise HTTPException(status_code=404, detail="Öneri bulunamadı.")
    get_owned_farm(db, pred.farm_id, current_user)
    reading = (
        db.query(SensorReading)
        .filter(SensorReading.farm_id == pred.farm_id)
        .order_by(SensorReading.timestamp.desc())
        .first()
    )
    duration = pred.irrigation_duration or 0
    water_mm = round(duration * 0.2, 1) if duration else None
    factors = [
        f"Risk seviyesi: {pred.risk_level.value}",
        f"Güven skoru: %{pred.confidence_score:.0f}",
        f"Sulama gerekli: {'evet' if pred.irrigation_needed else 'hayır'}",
    ]
    if pred.moisture_24h is not None:
        factors.append(f"24s tahmini nem: %{pred.moisture_24h:.0f}")
    if pred.moisture_48h is not None:
        factors.append(f"48s tahmini nem: %{pred.moisture_48h:.0f}")
    if pred.moisture_72h is not None:
        factors.append(f"72s tahmini nem: %{pred.moisture_72h:.0f}")

    sources: list[str] = []
    if reading:
        sources.append(f"Toprak nemi %{reading.soil_moisture:.0f} ({reading.source_type.value})")
        if reading.air_temperature is not None:
            sources.append(f"Hava sıcaklığı {reading.air_temperature:.0f}°C")
        if reading.rainfall_probability is not None:
            sources.append(f"Yağış olasılığı %{reading.rainfall_probability:.0f}")
        if reading.last_irrigation_hours_ago is not None:
            sources.append(f"Son sulama {reading.last_irrigation_hours_ago:.0f} saat önce")
        if reading.data_confidence is not None:
            sources.append(f"Veri güveni %{reading.data_confidence:.0f}")
    else:
        sources.append("Sensör okuması yok")

    automation = pred.irrigation_needed and pred.confidence_score >= MIN_CONFIDENCE
    block = None
    if not pred.irrigation_needed:
        block = "AI sulama önermiyor."
    elif pred.confidence_score < MIN_CONFIDENCE:
        block = f"Güven %{pred.confidence_score:.0f} — otomasyon için en az %{MIN_CONFIDENCE:.0f} gerekir."

    return RecommendationDetailOut(
        prediction=PredictionOut.model_validate(pred),
        title=_title(pred),
        priority=_priority(pred.risk_level.value),  # type: ignore[arg-type]
        automation_allowed=automation,
        factors=factors,
        data_sources=sources,
        current_moisture=reading.soil_moisture if reading else None,
        estimated_water_mm=water_mm,
        can_apply=automation,
        apply_block_reason=block,
    )


@router.get("/recommendations/{farm_id}", response_model=RecommendationSummaryOut)
def list_recommendations(
    farm_id: int,
    category: str | None = Query(default=None),
    priority: str | None = Query(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    get_owned_farm(db, farm_id, current_user)
    preds = (
        db.query(Prediction)
        .filter(Prediction.farm_id == farm_id)
        .order_by(Prediction.created_at.desc())
        .limit(30)
        .all()
    )
    items: list[RecommendationItemOut] = []
    for p in preds:
        pri = _priority(p.risk_level.value)
        items.append(
            RecommendationItemOut(
                id=f"pred-{p.id}",
                prediction_id=p.id,
                category="irrigation",
                title=_title(p),
                summary=(p.explanation[:160] + ("…" if len(p.explanation) > 160 else "")),
                priority=pri,  # type: ignore[arg-type]
                risk_level=p.risk_level.value,  # type: ignore[arg-type]
                confidence_score=p.confidence_score,
                irrigation_needed=p.irrigation_needed,
                created_at=p.created_at,
                automation_allowed=p.irrigation_needed and p.confidence_score >= MIN_CONFIDENCE,
            )
        )

    # Climate / anomaly items as secondary recommendations
    findings = collect_farm_anomalies(db, farm_id)
    reading = (
        db.query(SensorReading)
        .filter(SensorReading.farm_id == farm_id)
        .order_by(SensorReading.timestamp.desc())
        .first()
    )
    for f in findings:
        items.append(
            RecommendationItemOut(
                id=f"anom-{f.code}",
                prediction_id=None,
                category=(
                    "climate"
                    if "temp" in f.code or "rain" in f.code
                    else "other"
                ),
                title=f.title,
                summary=f.message,
                priority="high" if f.severity == "critical" else "medium",
                created_at=reading.timestamp if reading else preds[0].created_at if preds else None,  # type: ignore[arg-type]
                automation_allowed=False,
            )
        )

    if category and category not in {"all", "tumu", "tümü"}:
        # MVP: fertilizer/disease → empty; irrigation/climate/other filter
        if category in {"fertilizer", "disease", "gubreleme", "hastalik"}:
            items = []
        else:
            items = [i for i in items if i.category == category]
    if priority and priority not in {"all", "tumu"}:
        items = [i for i in items if i.priority == priority]

    high = sum(1 for i in items if i.priority == "high")
    medium = sum(1 for i in items if i.priority == "medium")
    low = sum(1 for i in items if i.priority == "low")
    return RecommendationSummaryOut(
        farm_id=farm_id,
        total=len(items),
        high=high,
        medium=medium,
        low=low,
        items=items,
    )


@router.get("/hub/{farm_id}", response_model=HubOut)
def farm_hub(
    farm_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    farm = get_owned_farm(db, farm_id, current_user)
    findings = collect_farm_anomalies(db, farm_id)
    alerts: list[HubAlertOut] = [
        HubAlertOut(code=f.code, severity=f.severity, title=f.title, message=f.message)
        for f in findings
    ]

    pred = (
        db.query(Prediction)
        .filter(Prediction.farm_id == farm_id)
        .order_by(Prediction.created_at.desc())
        .first()
    )
    if pred and pred.irrigation_needed and pred.risk_level.value in {"high", "critical"}:
        alerts.insert(
            0,
            HubAlertOut(
                code="irrigation_priority",
                severity=pred.risk_level.value,
                title="Yüksek öncelikli sulama önerisi",
                message=pred.explanation[:200],
            ),
        )

    counts = {"critical": 0, "high": 0, "medium": 0, "low": 0, "info": 0}
    for a in alerts:
        key = a.severity if a.severity in counts else "info"
        counts[key] = counts.get(key, 0) + 1

    irr_events = (
        db.query(IrrigationEvent).filter(IrrigationEvent.farm_id == farm_id).all()
    )
    irr_count = len(irr_events)
    finished = [
        e
        for e in irr_events
        if e.status in {IrrigationStatus.completed, IrrigationStatus.stopped}
    ]
    water = compute_water_usage([e.water_amount for e in finished])
    lab_count = db.query(LabReport).filter(LabReport.farm_id == farm_id).count()
    pred_count = db.query(Prediction).filter(Prediction.farm_id == farm_id).count()

    savings_label = None
    if water.session_count:
        savings_label = (
            f"{water.savings_liters:.0f} L"
            + (f" (%{water.savings_pct:.0f})" if water.savings_pct is not None else "")
        )

    reports = [
        HubReportOut(
            key="irrigation",
            title="Sulama raporu",
            description="Sanal sulama olayları ve süre özeti",
            available=True,
            record_count=irr_count,
            metric_label="Kullanılan su",
            metric_value=f"{water.water_used_liters:.0f} L" if water.session_count else "—",
        ),
        HubReportOut(
            key="water_savings",
            title="Tahmini su tasarrufu",
            description=water.note,
            available=True,
            record_count=water.session_count,
            metric_label="Tasarruf (kural)",
            metric_value=savings_label or "—",
        ),
        HubReportOut(
            key="moisture",
            title="Nem / AI öneri özeti",
            description="Son tahminler ve güven skorları",
            available=True,
            record_count=pred_count,
        ),
        HubReportOut(
            key="lab",
            title="Laboratuvar özeti",
            description="Onaylı toprak analizleri",
            available=True,
            record_count=lab_count,
        ),
        HubReportOut(
            key="yield",
            title="Verim raporu",
            description="MVP kapsamı dışı",
            available=False,
            record_count=0,
        ),
        HubReportOut(
            key="disease",
            title="Hastalık raporu",
            description="MVP kapsamı dışı",
            available=False,
            record_count=0,
        ),
        HubReportOut(
            key="fertilizer",
            title="Gübre raporu",
            description="MVP kapsamı dışı",
            available=False,
            record_count=0,
        ),
    ]

    return HubOut(
        farm_id=farm.id,
        farm_name=farm.name,
        alerts=alerts,
        alert_counts=counts,
        reports=reports,
        settings={
            "user_name": current_user.name,
            "user_role": current_user.role,
            "email": current_user.email,
            "phone": getattr(current_user, "phone", None),
            "min_confidence_automation": MIN_CONFIDENCE,
            "virtual_irrigation_only": True,
            "critical_moisture_pct": 20,
        },
        note="Raporlar MVP'de özet/meta veridir; PDF indirme P2. Su tasarrufu kural tabanlıdır.",
        water_used_liters=water.water_used_liters if water.session_count else None,
        water_savings_liters=water.savings_liters if water.session_count else None,
        water_savings_pct=water.savings_pct,
        water_usage_note=water.note if water.session_count else None,
    )
