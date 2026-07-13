"""AI recommendation list/detail + farm hub (reports/alerts/settings)."""

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.anomaly_service import collect_farm_anomalies
from app.agro_catalog import commentary_from_materials, format_materials_summary
from app.materials_service import load_farm_uses
from app.auth import get_current_user
from app.database import get_db
from app.deps import get_owned_farm
from app.models import (
    IrrigationEvent,
    IrrigationStatus,
    LabParameter,
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
from app.weather import weather_for_farm

router = APIRouter(tags=["recommendations-hub"])

MIN_CONFIDENCE = 60.0
STALE_HOURS = 24.0


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


def _build_insight_items(
    db: Session,
    farm_id: int,
    preds: list[Prediction],
    reading: SensorReading | None,
) -> list[RecommendationItemOut]:
    items: list[RecommendationItemOut] = []
    now = datetime.utcnow()
    latest_pred = preds[0] if preds else None
    base_ts = (
        reading.timestamp
        if reading
        else (latest_pred.created_at if latest_pred else now)
    )

    # --- Moisture forecast trend ---
    if latest_pred and (
        latest_pred.moisture_24h is not None
        or latest_pred.moisture_48h is not None
        or latest_pred.moisture_72h is not None
    ):
        m0 = reading.soil_moisture if reading else None
        m72 = latest_pred.moisture_72h
        trend = ""
        pri = "medium"
        if m0 is not None and m72 is not None:
            delta = m72 - m0
            if delta <= -8:
                trend = (
                    f"72 saatte nem ≈%{m72:.0f} (şimdi %{m0:.0f}). "
                    "Kuruma eğilimi — sulama planını gözden geçirin."
                )
                pri = "high"
            elif delta >= 5:
                trend = (
                    f"Nem 72s ≈%{m72:.0f}’ye yükselme eğiliminde. "
                    "Aşırı sulamadan kaçının."
                )
            else:
                trend = (
                    f"24/48/72s projeksiyon: "
                    f"%{latest_pred.moisture_24h or '—'} / "
                    f"%{latest_pred.moisture_48h or '—'} / "
                    f"%{latest_pred.moisture_72h or '—'}."
                )
                pri = "low"
        else:
            trend = "Nem projeksiyonu mevcut; canlı ölçümle birlikte izleyin."
            pri = "low"
        items.append(
            RecommendationItemOut(
                id="insight-moisture-forecast",
                prediction_id=latest_pred.id,
                category="moisture_forecast",
                title="Nem eğilimi (24–72s)",
                summary=trend,
                priority=pri,  # type: ignore[arg-type]
                confidence_score=latest_pred.confidence_score,
                created_at=latest_pred.created_at,
                automation_allowed=False,
            )
        )

    # --- Data quality / stale ---
    if reading is None:
        items.append(
            RecommendationItemOut(
                id="insight-no-data",
                category="data_quality",
                title="Ölçüm verisi yok",
                summary="Öneri üretmek için manuel, IoT simülasyon veya test veri seti ekleyin.",
                priority="high",
                created_at=base_ts,
                automation_allowed=False,
            )
        )
    else:
        age_h = (now - reading.timestamp).total_seconds() / 3600
        if age_h >= STALE_HOURS:
            items.append(
                RecommendationItemOut(
                    id="insight-stale-data",
                    category="data_quality",
                    title="Veri güncelliği düşük",
                    summary=(
                        f"Son okuma ≈{age_h:.0f} saat önce ({reading.source_type.value}). "
                        "Canlı sensör veya simülasyonu yenileyin."
                    ),
                    priority="medium",
                    created_at=reading.timestamp,
                    automation_allowed=False,
                )
            )
        if reading.data_confidence is not None and reading.data_confidence < 60:
            items.append(
                RecommendationItemOut(
                    id="insight-low-confidence",
                    category="data_quality",
                    title="Düşük veri güveni",
                    summary=(
                        f"Veri güveni %{reading.data_confidence:.0f}. "
                        "Otomasyon önerilmez; ölçümü doğrulayın."
                    ),
                    priority="high",
                    confidence_score=reading.data_confidence,
                    created_at=reading.timestamp,
                    automation_allowed=False,
                )
            )
        if reading.source_type.value == "simulation":
            items.append(
                RecommendationItemOut(
                    id="insight-sim-badge",
                    category="data_quality",
                    title="Simülasyon kaynağı",
                    summary=(
                        "Gösterilen IoT değerleri simülasyondur — gerçek saha sensörü değildir."
                    ),
                    priority="low",
                    created_at=reading.timestamp,
                    automation_allowed=False,
                )
            )

    # --- Lab vs IoT compare (complementary, not fertilizer Rx) ---
    lab = (
        db.query(LabReport)
        .filter(LabReport.farm_id == farm_id, LabReport.user_confirmed.is_(True))
        .order_by(LabReport.created_at.desc())
        .first()
    )
    if lab and reading:
        lab_ph = (
            db.query(LabParameter)
            .filter(
                LabParameter.report_id == lab.id,
                LabParameter.parameter_code.ilike("%ph%"),
            )
            .first()
        )
        if (
            lab_ph
            and lab_ph.value is not None
            and reading.ph is not None
            and abs(float(lab_ph.value) - float(reading.ph)) >= 0.8
        ):
            items.append(
                RecommendationItemOut(
                    id="insight-lab-iot-ph",
                    category="lab_iot_compare",
                    title="Lab ile IoT pH farkı",
                    summary=(
                        f"Lab pH {lab_ph.value}{lab_ph.unit or ''} vs IoT {reading.ph}. "
                        "Lab kimya profilidir; sürekli nem IoT’den — gübre reçetesi üretilmez."
                    ),
                    priority="medium",
                    created_at=lab.created_at,
                    automation_allowed=False,
                )
            )
        elif reading.ec is not None and reading.ec >= 2.5:
            items.append(
                RecommendationItemOut(
                    id="insight-lab-iot-ec",
                    category="lab_iot_compare",
                    title="EC / tuzluluk izleme",
                    summary=(
                        f"IoT EC {reading.ec}. Lab profili ile birlikte izleyin; "
                        "gübreleme reçetesi MVP kapsamı dışıdır."
                    ),
                    priority="low",
                    created_at=reading.timestamp,
                    automation_allowed=False,
                )
            )
        elif lab:
            items.append(
                RecommendationItemOut(
                    id="insight-lab-present",
                    category="lab_iot_compare",
                    title="Lab + nem birlikte",
                    summary=(
                        "Onaylı lab raporu mevcut. IoT nemi tamamlar; laboratuvarın yerini almaz."
                    ),
                    priority="low",
                    created_at=lab.created_at,
                    automation_allowed=False,
                )
            )


    # --- Farm materials profile (context only; no fertilizer Rx) ---
    uses = load_farm_uses(db, farm_id)
    if uses:
        summary = format_materials_summary(uses) or ""
        notes = commentary_from_materials(
            uses, ec=reading.ec if reading else None
        )
        note_txt = notes[0] if notes else (
            "Kayıtlı gübre/ilaç sınıfları sulama ve EC yorumuna bağlam sağlar; doz reçetesi üretilmez."
        )
        items.append(
            RecommendationItemOut(
                id="insight-farm-materials",
                category="other",
                title="Arazi gübre / ilaç profili",
                summary=(
                    f"{note_txt} "
                    f"Seçimler: {summary[:220]}{'…' if len(summary) > 220 else ''}"
                ),
                priority="low",
                created_at=base_ts,
                automation_allowed=False,
            )
        )

    # --- Water savings insight ---
    events = db.query(IrrigationEvent).filter(IrrigationEvent.farm_id == farm_id).all()
    finished = [
        e
        for e in events
        if e.status in {IrrigationStatus.completed, IrrigationStatus.stopped}
    ]
    if finished:
        water = compute_water_usage([e.water_amount for e in finished])
        if water.session_count and water.savings_liters:
            items.append(
                RecommendationItemOut(
                    id="insight-water-savings",
                    category="other",
                    title="Tahmini su tasarrufu",
                    summary=(
                        f"≈{water.savings_liters:.0f} L tasarruf (kural tabanlı). "
                        f"{water.note}"
                    ),
                    priority="low",
                    created_at=base_ts,
                    automation_allowed=False,
                )
            )

    return items


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
        sources.append(
            f"Toprak nemi %{reading.soil_moisture:.0f} ({reading.source_type.value})"
        )
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
        block = (
            f"Güven %{pred.confidence_score:.0f} — otomasyon için "
            f"en az %{MIN_CONFIDENCE:.0f} gerekir."
        )

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
    farm = get_owned_farm(db, farm_id, current_user)
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
                automation_allowed=p.irrigation_needed
                and p.confidence_score >= MIN_CONFIDENCE,
            )
        )

    reading = (
        db.query(SensorReading)
        .filter(SensorReading.farm_id == farm_id)
        .order_by(SensorReading.timestamp.desc())
        .first()
    )

    # Anomalies → data_quality / weather_context
    findings = collect_farm_anomalies(db, farm_id)
    for f in findings:
        cat = (
            "weather_context"
            if "temp" in f.code or "rain" in f.code or "hava" in f.code.lower()
            else "data_quality"
        )
        items.append(
            RecommendationItemOut(
                id=f"anom-{f.code}",
                prediction_id=None,
                category=cat,  # type: ignore[arg-type]
                title=f.title,
                summary=f.message,
                priority="high" if f.severity == "critical" else "medium",
                created_at=reading.timestamp
                if reading
                else (preds[0].created_at if preds else None),  # type: ignore[arg-type]
                automation_allowed=False,
            )
        )

    # Insights (forecast, stale, lab, water)
    # Avoid broken placeholder: build without re-fetching farm via wrong user
    insight_items = _build_insight_items(db, farm_id, preds, reading)
    # Strip the broken farm lookup from helper — rewrite helper cleanly without that call
    items.extend([i for i in insight_items if i.id != "insight-broken"])

    # Live weather context (Open-Meteo)
    try:
        wx = weather_for_farm(farm)
        if not wx.get("error") and (
            wx.get("temperature_c") is not None
            or wx.get("precip_probability_pct") is not None
        ):
            precip = wx.get("precip_probability_pct")
            temp = wx.get("temperature_c")
            humid = wx.get("humidity_pct")
            parts = []
            if temp is not None:
                parts.append(f"{temp:.0f}°C")
            if humid is not None:
                parts.append(f"nem %{humid:.0f}")
            if precip is not None:
                parts.append(f"yağış ihtimali %{precip:.0f}")
            summary = "Open-Meteo: " + ", ".join(parts) + "."
            pri = "medium" if precip is not None and precip >= 50 else "low"
            if precip is not None and precip >= 60 and reading and reading.soil_moisture and reading.soil_moisture >= 30:
                summary += " Yağış olası — gereksiz sulamayı erteleyebilirsiniz."
                pri = "medium"
            items.append(
                RecommendationItemOut(
                    id="insight-weather",
                    category="weather_context",
                    title="Hava durumu bağlamı",
                    summary=summary,
                    priority=pri,  # type: ignore[arg-type]
                    created_at=reading.timestamp if reading else datetime.utcnow(),
                    automation_allowed=False,
                )
            )
    except Exception:
        pass

    if category and category not in {"all", "tumu", "tümü"}:
        if category in {"fertilizer", "disease", "gubreleme", "hastalik"}:
            items = []
        elif category == "climate":
            items = [i for i in items if i.category in {"climate", "weather_context"}]
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
