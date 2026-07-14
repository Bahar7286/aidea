"""Crop season history CRUD + rule-based next-crop suggestions."""

from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.crop_suggest import crop_family, suggest_next_crops
from app.database import get_db
from app.deps import get_owned_farm
from app.lab_interpret import normalize_code
from app.llm_explain import enrich_crop_suggestion_explanation
from app.models import (
    CropHistory,
    CropSeasonStatus,
    LabReport,
    Prediction,
    SensorReading,
    User,
)
from app.schemas import (
    CropHistoryCreate,
    CropHistoryListOut,
    CropHistoryOut,
    CropHistoryUpdate,
    CropSuggestionItemOut,
    CropSuggestionsOut,
)

router = APIRouter(tags=["crop-history"])


def _days_between(later: datetime, earlier: datetime) -> int:
    return max(0, (later.date() - earlier.date()).days)


def _history_out(row: CropHistory, now: datetime | None = None) -> CropHistoryOut:
    now = now or datetime.utcnow()
    days_plant = _days_between(now, row.planting_date) if row.planting_date else None
    days_harv = None
    if row.harvest_date and row.status == CropSeasonStatus.harvested:
        days_harv = _days_between(now, row.harvest_date)
    return CropHistoryOut(
        id=row.id,
        farm_id=row.farm_id,
        crop_type=row.crop_type,
        planting_date=row.planting_date,
        harvest_date=row.harvest_date,
        status=row.status.value if hasattr(row.status, "value") else str(row.status),
        yield_amount=row.yield_amount,
        yield_unit=row.yield_unit,
        notes=row.notes,
        source_type=row.source_type or "manual",
        created_at=row.created_at,
        days_since_planting=days_plant,
        days_since_harvest=days_harv,
        family=crop_family(row.crop_type),
    )


def _validate_dates(payload_status: str, planting: datetime, harvest: datetime | None) -> None:
    if payload_status == "harvested":
        if harvest is None:
            raise HTTPException(
                status_code=400,
                detail="Hasat edilmiş sezon için harvest_date zorunludur.",
            )
        if harvest.date() < planting.date():
            raise HTTPException(
                status_code=400,
                detail="Hasat tarihi ekim tarihinden önce olamaz.",
            )
    elif harvest is not None and harvest.date() < planting.date():
        raise HTTPException(
            status_code=400,
            detail="Hasat tarihi ekim tarihinden önce olamaz.",
        )


def _latest_lab_ph_om(db: Session, farm_id: int) -> tuple[float | None, float | None]:
    report = (
        db.query(LabReport)
        .filter(LabReport.farm_id == farm_id, LabReport.user_confirmed.is_(True))
        .order_by(LabReport.created_at.desc())
        .first()
    )
    if not report:
        return None, None
    ph: float | None = None
    om: float | None = None
    for p in report.parameters:
        code = normalize_code(p.parameter_code)
        if code == "ph" and ph is None:
            ph = p.value
        elif code in ("om", "organic_matter") and om is None:
            om = p.value
    return ph, om


def _soil_snapshot(db: Session, farm_id: int) -> tuple[float | None, str | None, str]:
    reading = (
        db.query(SensorReading)
        .filter(SensorReading.farm_id == farm_id)
        .order_by(SensorReading.timestamp.desc())
        .first()
    )
    pred = (
        db.query(Prediction)
        .filter(Prediction.farm_id == farm_id)
        .order_by(Prediction.created_at.desc())
        .first()
    )
    moisture = reading.soil_moisture if reading else None
    risk = None
    if pred and pred.risk_level:
        risk = pred.risk_level.value if hasattr(pred.risk_level, "value") else str(pred.risk_level)
    lab_ph, lab_om = _latest_lab_ph_om(db, farm_id)
    parts: list[str] = []
    if moisture is not None:
        parts.append(f"nem %{moisture:.0f}")
    if risk:
        parts.append(f"risk {risk}")
    if lab_ph is not None:
        parts.append(f"pH {lab_ph:.1f}")
    if lab_om is not None:
        parts.append(f"OM %{lab_om:.1f}")
    if reading and reading.source_type:
        src = (
            reading.source_type.value
            if hasattr(reading.source_type, "value")
            else str(reading.source_type)
        )
        parts.append(f"kaynak: {src}")
    summary = "; ".join(parts) if parts else "ölçüm yok"
    return moisture, risk, summary


@router.get("/farms/{farm_id}/crop-history", response_model=CropHistoryListOut)
def list_crop_history(
    farm_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    get_owned_farm(db, farm_id, current_user)
    now = datetime.utcnow()
    rows = (
        db.query(CropHistory)
        .filter(CropHistory.farm_id == farm_id)
        .order_by(CropHistory.planting_date.desc())
        .all()
    )
    items = [_history_out(r, now) for r in rows]
    current = next((i for i in items if i.status == "growing"), None)
    harvested = [i for i in items if i.status == "harvested" and i.harvest_date]
    last_h = max(harvested, key=lambda x: x.harvest_date) if harvested else None  # type: ignore[arg-type]
    days = last_h.days_since_harvest if last_h else None
    _, _, soil_summary = _soil_snapshot(db, farm_id)
    return CropHistoryListOut(
        items=items,
        current_crop=current,
        last_harvested=last_h,
        days_since_harvest=days,
        soil_condition_summary=soil_summary,
    )


@router.post(
    "/farms/{farm_id}/crop-history",
    response_model=CropHistoryOut,
    status_code=status.HTTP_201_CREATED,
)
def create_crop_history(
    farm_id: int,
    payload: CropHistoryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    get_owned_farm(db, farm_id, current_user, require_active=True)
    _validate_dates(payload.status, payload.planting_date, payload.harvest_date)

    if payload.status == "growing":
        existing = (
            db.query(CropHistory)
            .filter(
                CropHistory.farm_id == farm_id,
                CropHistory.status == CropSeasonStatus.growing,
            )
            .first()
        )
        if existing:
            raise HTTPException(
                status_code=400,
                detail="Bu arazide zaten yetişen bir sezon var. Önce hasat edin veya güncelleyin.",
            )

    status_enum = CropSeasonStatus(payload.status)
    row = CropHistory(
        farm_id=farm_id,
        crop_type=payload.crop_type.strip().lower(),
        planting_date=payload.planting_date,
        harvest_date=payload.harvest_date,
        status=status_enum,
        yield_amount=payload.yield_amount,
        yield_unit=payload.yield_unit,
        notes=payload.notes,
        source_type="manual",
    )
    if status_enum == CropSeasonStatus.harvested and row.harvest_date is None:
        raise HTTPException(status_code=400, detail="Hasat tarihi zorunlu.")
    db.add(row)
    db.commit()
    db.refresh(row)
    return _history_out(row)


@router.put("/crop-history/{history_id}", response_model=CropHistoryOut)
def update_crop_history(
    history_id: int,
    payload: CropHistoryUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    row = db.query(CropHistory).filter(CropHistory.id == history_id).first()
    if not row:
        raise HTTPException(status_code=404, detail="Ürün geçmişi kaydı bulunamadı.")
    get_owned_farm(db, row.farm_id, current_user, require_active=True)

    data = payload.model_dump(exclude_unset=True)
    new_status = data.get("status", row.status.value if hasattr(row.status, "value") else row.status)
    new_plant = data.get("planting_date", row.planting_date)
    new_harvest = data.get("harvest_date", row.harvest_date)
    _validate_dates(str(new_status), new_plant, new_harvest)

    if data.get("status") == "growing" or (
        "status" not in data and row.status == CropSeasonStatus.growing
    ):
        if str(new_status) == "growing":
            other = (
                db.query(CropHistory)
                .filter(
                    CropHistory.farm_id == row.farm_id,
                    CropHistory.status == CropSeasonStatus.growing,
                    CropHistory.id != row.id,
                )
                .first()
            )
            if other:
                raise HTTPException(
                    status_code=400,
                    detail="Başka bir yetişen sezon zaten kayıtlı.",
                )

    if "crop_type" in data and data["crop_type"]:
        row.crop_type = str(data["crop_type"]).strip().lower()
    if "planting_date" in data and data["planting_date"] is not None:
        row.planting_date = data["planting_date"]
    if "harvest_date" in data:
        row.harvest_date = data["harvest_date"]
    if "status" in data and data["status"]:
        row.status = CropSeasonStatus(data["status"])
    if "yield_amount" in data:
        row.yield_amount = data["yield_amount"]
    if "yield_unit" in data:
        row.yield_unit = data["yield_unit"]
    if "notes" in data:
        row.notes = data["notes"]

    if row.status == CropSeasonStatus.harvested and row.harvest_date is None:
        raise HTTPException(status_code=400, detail="Hasat edilmiş sezon için harvest_date zorunludur.")

    db.commit()
    db.refresh(row)
    return _history_out(row)


@router.delete("/crop-history/{history_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_crop_history(
    history_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    row = db.query(CropHistory).filter(CropHistory.id == history_id).first()
    if not row:
        raise HTTPException(status_code=404, detail="Ürün geçmişi kaydı bulunamadı.")
    get_owned_farm(db, row.farm_id, current_user, require_active=True)
    db.delete(row)
    db.commit()
    return None


@router.get("/farms/{farm_id}/crop-suggestions", response_model=CropSuggestionsOut)
def crop_suggestions(
    farm_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    get_owned_farm(db, farm_id, current_user)
    now = datetime.utcnow()
    rows = (
        db.query(CropHistory)
        .filter(CropHistory.farm_id == farm_id)
        .order_by(CropHistory.planting_date.desc())
        .all()
    )
    growing = next((r for r in rows if r.status == CropSeasonStatus.growing), None)
    harvested = [r for r in rows if r.status == CropSeasonStatus.harvested and r.harvest_date]
    last_h = max(harvested, key=lambda r: r.harvest_date) if harvested else None  # type: ignore[arg-type]
    days = _days_between(now, last_h.harvest_date) if last_h and last_h.harvest_date else None

    moisture, risk, _ = _soil_snapshot(db, farm_id)
    lab_ph, lab_om = _latest_lab_ph_om(db, farm_id)

    result = suggest_next_crops(
        previous_crop=last_h.crop_type if last_h else None,
        days_since_harvest=days,
        current_growing=growing.crop_type if growing else None,
        soil_moisture=moisture,
        risk_level=risk,
        lab_ph=lab_ph,
        lab_om=lab_om,
        now=now,
    )

    explanation = result.explanation
    llm_enriched = False
    enriched = enrich_crop_suggestion_explanation(
        explanation=explanation,
        context={
            "onceki_urun": result.previous_crop,
            "aile": result.previous_family,
            "hasattan_gun": result.days_since_harvest,
            "mevcut": result.current_crop,
            "toprak": result.soil_condition,
            "adaylar": [
                {"urun": s.crop_type, "skor": s.score, "uygun": s.suitable_now}
                for s in result.suggestions[:4]
            ],
        },
    )
    if enriched:
        explanation = enriched
        llm_enriched = True

    return CropSuggestionsOut(
        farm_id=farm_id,
        suggestions=[
            CropSuggestionItemOut(
                crop_type=s.crop_type,
                label_tr=s.label_tr,
                family=s.family,
                score=s.score,
                reasons=s.reasons,
                suitable_now=s.suitable_now,
            )
            for s in result.suggestions
        ],
        soil_condition=result.soil_condition,
        days_since_harvest=result.days_since_harvest,
        previous_crop=result.previous_crop,
        previous_family=result.previous_family,
        current_crop=result.current_crop,
        fallow_ok=result.fallow_ok,
        explanation=explanation,
        engine=result.engine,
        llm_enriched=llm_enriched,
    )
