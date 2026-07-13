from datetime import datetime, timedelta
from pathlib import Path

from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile, status
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.database import get_db
from app.deps import get_owned_farm
from app.lab_interpret import (
    compute_status,
    count_critical,
    demo_extraction,
    interpret_report,
    normalize_code,
)
from app.models import Device, LabParameter, LabReport, LabSourceType, ManagementZone, SensorReading, User
from app.schemas import (
    LabConfirmRequest,
    LabDetailOut,
    LabExtractDemoOut,
    LabInsightOut,
    LabParameterIn,
    LabReportCreate,
    LabReportOut,
    LabReportUpdate,
    LabSummaryOut,
    ZoneCreate,
    ZoneOut,
    ZoneUpdate,
)

router = APIRouter(tags=["lab-zones"])

UPLOAD_DIR = Path(__file__).resolve().parents[1] / "uploads" / "lab"

ALLOWED_LAB_CODES = {
    "ph",
    "ec",
    "om",
    "organic_matter",
    "lime",
    "p",
    "phosphorus",
    "k",
    "potassium",
    "n",
    "nitrogen",
    "zn",
    "zinc",
    "fe",
    "iron",
    "b",
    "boron",
    "mg",
    "magnesium",
    "na",
    "sodium",
    "texture",
    "saturation",
}


def _validate_params(parameters: list[LabParameterIn]) -> None:
    for p in parameters:
        if not p.unit.strip():
            raise HTTPException(
                status_code=400,
                detail=f"Parametre '{p.parameter_code}' için birim zorunludur.",
            )
        code = normalize_code(p.parameter_code)
        if code not in ALLOWED_LAB_CODES and p.parameter_code.lower().strip() not in ALLOWED_LAB_CODES:
            raise HTTPException(
                status_code=400,
                detail=(
                    f"Parametre '{p.parameter_code}' MVP lab paketinde değil. "
                    f"İzinli: {', '.join(sorted(ALLOWED_LAB_CODES))}"
                ),
            )


def _param_map(report: LabReport) -> dict[str, float]:
    out: dict[str, float] = {}
    for p in report.parameters:
        out[normalize_code(p.parameter_code)] = p.value
    return out


def _report_out(report: LabReport) -> LabReportOut:
    data = LabReportOut.model_validate(report)
    params = [
        {
            "parameter_code": p.parameter_code,
            "value": p.value,
            "unit": p.unit,
        }
        for p in report.parameters
    ]
    insights = interpret_report(params)
    data.critical_count = count_critical(insights)
    status_val = report.status or compute_status(report.user_confirmed, report.parameters)
    data.status = status_val
    pm = _param_map(report)
    data.ph = pm.get("ph")
    data.ec = pm.get("ec")
    data.om = pm.get("om")
    return data


def _replace_parameters(db: Session, report: LabReport, parameters: list[LabParameterIn]) -> None:
    report.parameters.clear()
    db.flush()
    for p in parameters:
        db.add(
            LabParameter(
                report_id=report.id,
                parameter_code=normalize_code(p.parameter_code),
                value=p.value,
                unit=p.unit.strip(),
                method=p.method,
                extracted_auto=p.extracted_auto,
                confidence_pct=p.confidence_pct,
            )
        )


@router.post("/zones", response_model=ZoneOut, status_code=status.HTTP_201_CREATED)
def create_zone(
    payload: ZoneCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    get_owned_farm(db, payload.farm_id, current_user, require_active=True)
    exists = (
        db.query(ManagementZone)
        .filter(
            ManagementZone.farm_id == payload.farm_id,
            ManagementZone.name == payload.name,
        )
        .first()
    )
    if exists:
        raise HTTPException(status_code=400, detail="Bu arazi için aynı bölge adı zaten var.")
    zone = ManagementZone(
        farm_id=payload.farm_id,
        name=payload.name,
        notes=payload.notes,
    )
    db.add(zone)
    db.commit()
    db.refresh(zone)
    return ZoneOut.model_validate(zone)


@router.get("/zones/detail/{zone_id}", response_model=ZoneOut)
def get_zone(
    zone_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    zone = db.query(ManagementZone).filter(ManagementZone.id == zone_id).first()
    if not zone:
        raise HTTPException(status_code=404, detail="Bölge bulunamadı.")
    get_owned_farm(db, zone.farm_id, current_user)
    return ZoneOut.model_validate(zone)


@router.put("/zones/detail/{zone_id}", response_model=ZoneOut)
def update_zone(
    zone_id: int,
    payload: ZoneUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    zone = db.query(ManagementZone).filter(ManagementZone.id == zone_id).first()
    if not zone:
        raise HTTPException(status_code=404, detail="Bölge bulunamadı.")
    get_owned_farm(db, zone.farm_id, current_user, require_active=True)
    data = payload.model_dump(exclude_unset=True)
    if "name" in data and data["name"] is not None:
        name = data["name"].strip()
        clash = (
            db.query(ManagementZone)
            .filter(
                ManagementZone.farm_id == zone.farm_id,
                ManagementZone.name == name,
                ManagementZone.id != zone.id,
            )
            .first()
        )
        if clash:
            raise HTTPException(status_code=400, detail="Bu arazi için aynı bölge adı zaten var.")
        zone.name = name
    if "notes" in data:
        zone.notes = data["notes"]
    db.commit()
    db.refresh(zone)
    return ZoneOut.model_validate(zone)


@router.delete("/zones/detail/{zone_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_zone(
    zone_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    zone = db.query(ManagementZone).filter(ManagementZone.id == zone_id).first()
    if not zone:
        raise HTTPException(status_code=404, detail="Bölge bulunamadı.")
    get_owned_farm(db, zone.farm_id, current_user, require_active=True)
    # Detach references so history rows remain.
    db.query(LabReport).filter(LabReport.zone_id == zone.id).update({"zone_id": None})
    db.query(Device).filter(Device.zone_id == zone.id).update({"zone_id": None})
    db.query(SensorReading).filter(SensorReading.zone_id == zone.id).update({"zone_id": None})
    db.delete(zone)
    db.commit()
    return None


@router.get("/zones/{farm_id}", response_model=list[ZoneOut])
def list_zones(
    farm_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    get_owned_farm(db, farm_id, current_user)
    rows = db.query(ManagementZone).filter(ManagementZone.farm_id == farm_id).all()
    return [ZoneOut.model_validate(z) for z in rows]


@router.get("/lab-reports/extract-demo", response_model=LabExtractDemoOut)
def lab_extract_demo(current_user: User = Depends(get_current_user)):
    """Simulated extraction — not real OCR. Always labeled for UI."""
    _ = current_user
    rows, avg = demo_extraction()
    return LabExtractDemoOut(
        parameters=[LabParameterIn(**r) for r in rows],
        extraction_confidence=avg,
        message="Simüle çıkarım (MVP). Gerçek OCR / PDF ayrıştırma değildir.",
    )


@router.post("/lab-reports/upload", status_code=201)
async def upload_lab_file(
    farm_id: int = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    get_owned_farm(db, farm_id, current_user, require_active=True)
    name = file.filename or "report.bin"
    ext = Path(name).suffix.lower()
    if ext not in {".pdf", ".jpg", ".jpeg", ".png", ".xlsx", ".xls"}:
        raise HTTPException(status_code=400, detail="Desteklenen: PDF, JPG, PNG, Excel.")
    content = await file.read()
    if len(content) > 20 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="Dosya en fazla 20 MB olabilir.")
    dest_dir = UPLOAD_DIR / str(farm_id)
    dest_dir.mkdir(parents=True, exist_ok=True)
    safe = f"{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_{Path(name).name}"
    path = dest_dir / safe
    path.write_bytes(content)
    return {
        "file_name": safe,
        "original_name": name,
        "size_bytes": len(content),
        "message": "Dosya kaydedildi. OCR yok — değerleri manuel girin veya simüle çıkarım kullanın.",
    }


@router.post("/lab-reports", response_model=LabReportOut, status_code=status.HTTP_201_CREATED)
def create_lab_report(
    payload: LabReportCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    get_owned_farm(db, payload.farm_id, current_user, require_active=True)
    if payload.zone_id:
        zone = (
            db.query(ManagementZone)
            .filter(
                ManagementZone.id == payload.zone_id,
                ManagementZone.farm_id == payload.farm_id,
            )
            .first()
        )
        if not zone:
            raise HTTPException(status_code=404, detail="Bölge bulunamadı.")

    _validate_params(payload.parameters)
    status_val = compute_status(payload.user_confirmed, payload.parameters)

    report = LabReport(
        farm_id=payload.farm_id,
        zone_id=payload.zone_id,
        lab_name=payload.lab_name,
        report_number=payload.report_number,
        analysis_date=payload.analysis_date,
        sample_date=payload.sample_date,
        sample_depth_cm=payload.sample_depth_cm,
        sample_region=payload.sample_region,
        file_name=payload.file_name,
        source_type=LabSourceType(payload.source_type),
        user_confirmed=bool(payload.user_confirmed),
        notes=payload.notes,
        status=status_val,
        extraction_confidence=payload.extraction_confidence,
    )
    db.add(report)
    db.flush()
    for p in payload.parameters:
        db.add(
            LabParameter(
                report_id=report.id,
                parameter_code=normalize_code(p.parameter_code),
                value=p.value,
                unit=p.unit.strip(),
                method=p.method,
                extracted_auto=p.extracted_auto,
                confidence_pct=p.confidence_pct,
            )
        )
    db.commit()
    db.refresh(report)
    return _report_out(report)


@router.get("/lab-reports/detail/{report_id}", response_model=LabDetailOut)
def get_lab_detail(
    report_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    report = db.query(LabReport).filter(LabReport.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Laboratuvar raporu bulunamadı.")
    get_owned_farm(db, report.farm_id, current_user)
    insights_raw = interpret_report(
        [{"parameter_code": p.parameter_code, "value": p.value, "unit": p.unit} for p in report.parameters]
    )
    highs = [i for i in insights_raw if i["risk"] == "high"]
    meds = [i for i in insights_raw if i["risk"] == "medium"]
    if highs:
        ai_summary = (
            "Kritik bulgular var: "
            + "; ".join(i["message"] for i in highs[:2])
            + " Bu yorum nem/sulama dijital ikizine katkı sağlar; gübre reçetesi değildir."
        )
    elif meds:
        ai_summary = (
            "Dikkat edilecek noktalar: "
            + "; ".join(i["message"] for i in meds[:2])
            + " Değerleri laboratuvar kaynağı olarak saklayın."
        )
    else:
        ai_summary = (
            "Temel parametreler kabul edilebilir görünüyor. "
            "IoT nem ölçümlerinin yerini almaz; sulama kararında destek kayıttır."
        )
    return LabDetailOut(
        report=_report_out(report),
        insights=[LabInsightOut(**i) for i in insights_raw],
        ai_summary=ai_summary,
        source_note=f"Kaynak: {report.source_type.value} — laboratuvar verisi IoT sensörü değildir.",
    )


@router.put("/lab-reports/detail/{report_id}", response_model=LabReportOut)
def update_lab_report(
    report_id: int,
    payload: LabReportUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    report = db.query(LabReport).filter(LabReport.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Laboratuvar raporu bulunamadı.")
    get_owned_farm(db, report.farm_id, current_user, require_active=True)
    data = payload.model_dump(exclude_unset=True)
    params = data.pop("parameters", None)
    for key, value in data.items():
        setattr(report, key, value)
    if params is not None:
        typed = [LabParameterIn(**p) if isinstance(p, dict) else p for p in params]
        _validate_params(typed)
        _replace_parameters(db, report, typed)
    report.status = compute_status(report.user_confirmed, report.parameters)
    db.commit()
    db.refresh(report)
    return _report_out(report)


@router.delete("/lab-reports/detail/{report_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_lab_report(
    report_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    report = db.query(LabReport).filter(LabReport.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Laboratuvar raporu bulunamadı.")
    get_owned_farm(db, report.farm_id, current_user, require_active=True)
    db.delete(report)
    db.commit()
    return None


@router.get("/lab-reports/{farm_id}/summary", response_model=LabSummaryOut)
def lab_summary(
    farm_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    get_owned_farm(db, farm_id, current_user)
    rows = db.query(LabReport).filter(LabReport.farm_id == farm_id).all()
    total = len(rows)
    pending = verified = missing = critical = 0
    cutoff = datetime.utcnow() - timedelta(days=30)
    last_30 = 0
    for r in rows:
        st = r.status or compute_status(r.user_confirmed, r.parameters)
        if st == "pending":
            pending += 1
        elif st == "missing":
            missing += 1
        else:
            verified += 1
        if r.created_at and r.created_at >= cutoff:
            last_30 += 1
        insights = interpret_report(
            [{"parameter_code": p.parameter_code, "value": p.value, "unit": p.unit} for p in r.parameters]
        )
        critical += count_critical(insights)
    return LabSummaryOut(
        farm_id=farm_id,
        total=total,
        pending=pending,
        verified=verified,
        missing=missing,
        last_30_days=last_30,
        critical_findings=critical,
    )


@router.get("/lab-reports/{farm_id}", response_model=list[LabReportOut])
def list_lab_reports(
    farm_id: int,
    status_filter: str | None = Query(default=None, alias="status"),
    q: str | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    get_owned_farm(db, farm_id, current_user)
    rows = (
        db.query(LabReport)
        .filter(LabReport.farm_id == farm_id)
        .order_by(LabReport.created_at.desc())
        .all()
    )
    out = [_report_out(r) for r in rows]
    if status_filter and status_filter.lower() not in {"all", "tumu", "tümü"}:
        wanted = status_filter.lower()
        out = [r for r in out if (r.status or "").lower() == wanted]
    if q:
        needle = q.lower().strip()
        out = [
            r
            for r in out
            if needle in r.lab_name.lower()
            or (r.report_number and needle in r.report_number.lower())
            or (r.sample_region and needle in r.sample_region.lower())
        ]
    return out


@router.post("/lab-reports/{report_id}/confirm", response_model=LabReportOut)
def confirm_lab_report(
    report_id: int,
    payload: LabConfirmRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    report = db.query(LabReport).filter(LabReport.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Laboratuvar raporu bulunamadı.")
    get_owned_farm(db, report.farm_id, current_user, require_active=True)
    if payload.parameters:
        _validate_params(payload.parameters)
        _replace_parameters(db, report, payload.parameters)
    if not payload.confirmed:
        report.user_confirmed = False
        report.status = compute_status(False, report.parameters)
    else:
        if not report.parameters:
            raise HTTPException(status_code=400, detail="Onay için en az bir parametre gerekli.")
        report.user_confirmed = True
        report.status = compute_status(True, report.parameters)
        if report.status == "missing":
            raise HTTPException(
                status_code=400,
                detail="Eksik temel parametreler (en az pH + bir değer). Onaylanamadı.",
            )
    db.commit()
    db.refresh(report)
    return _report_out(report)
