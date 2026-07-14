"""Farm agro-material association helpers."""

from __future__ import annotations

from datetime import datetime

from fastapi import HTTPException
from sqlalchemy.orm import Session, joinedload

from app.models import AgroMaterial, FarmMaterialUse


def load_farm_uses(db: Session, farm_id: int) -> list[FarmMaterialUse]:
    return (
        db.query(FarmMaterialUse)
        .options(joinedload(FarmMaterialUse.material))
        .filter(FarmMaterialUse.farm_id == farm_id)
        .all()
    )


def _parse_last_applied(last) -> datetime | None:
    if last is None:
        return None
    if isinstance(last, datetime):
        return last.replace(tzinfo=None) if last.tzinfo else last
    if isinstance(last, str):
        try:
            return datetime.fromisoformat(last.replace("Z", "+00:00")).replace(
                tzinfo=None
            )
        except ValueError:
            return None
    return None


def _field(raw, name: str, default=None):
    if hasattr(raw, name):
        return getattr(raw, name)
    if isinstance(raw, dict):
        return raw.get(name, default)
    return default


def sync_farm_materials(
    db: Session,
    farm_id: int,
    *,
    material_ids: list[int] | None = None,
    items: list | None = None,
) -> list[FarmMaterialUse]:
    """Replace farm material associations.

    Prefer `items` (rich). `material_ids` is a shorthand (notes/frequency cleared).
    Enforces at most one is_last_fertilizer and one is_last_pesticide per farm;
    last-used rows must match material kind (fertilizer / plant_protection).
    """
    if items is not None:
        desired: dict[int, dict] = {}
        for raw in items:
            mid = int(_field(raw, "material_id"))
            desired[mid] = {
                "notes": _field(raw, "notes"),
                "frequency": _field(raw, "frequency"),
                "last_applied_at": _parse_last_applied(_field(raw, "last_applied_at")),
                "is_last_fertilizer": bool(_field(raw, "is_last_fertilizer", False)),
                "is_last_pesticide": bool(_field(raw, "is_last_pesticide", False)),
            }
    elif material_ids is not None:
        desired = {
            int(m): {
                "notes": None,
                "frequency": None,
                "last_applied_at": None,
                "is_last_fertilizer": False,
                "is_last_pesticide": False,
            }
            for m in material_ids
        }
    else:
        return load_farm_uses(db, farm_id)

    if desired:
        found_rows = (
            db.query(AgroMaterial)
            .filter(
                AgroMaterial.id.in_(list(desired.keys())),
                AgroMaterial.is_active.is_(True),
            )
            .all()
        )
        by_id = {m.id: m for m in found_rows}
        missing = set(desired.keys()) - set(by_id.keys())
        if missing:
            raise HTTPException(
                status_code=400,
                detail=f"Geçersiz veya pasif malzeme id: {sorted(missing)}",
            )

        # Normalize last flags: only one per category; kind must match.
        last_fert_ids = [
            mid
            for mid, meta in desired.items()
            if meta["is_last_fertilizer"] and by_id[mid].kind == "fertilizer"
        ]
        last_pest_ids = [
            mid
            for mid, meta in desired.items()
            if meta["is_last_pesticide"] and by_id[mid].kind == "plant_protection"
        ]
        for mid, meta in desired.items():
            mat = by_id[mid]
            if meta["is_last_fertilizer"] and mat.kind != "fertilizer":
                raise HTTPException(
                    status_code=400,
                    detail="Son kullanılan gübre yalnızca gübre sınıfından seçilebilir.",
                )
            if meta["is_last_pesticide"] and mat.kind != "plant_protection":
                raise HTTPException(
                    status_code=400,
                    detail="Son kullanılan ilaç yalnızca bitki koruma sınıfından seçilebilir.",
                )
            meta["is_last_fertilizer"] = bool(
                last_fert_ids and mid == last_fert_ids[-1]
            )
            meta["is_last_pesticide"] = bool(
                last_pest_ids and mid == last_pest_ids[-1]
            )
    else:
        by_id = {}

    existing = (
        db.query(FarmMaterialUse).filter(FarmMaterialUse.farm_id == farm_id).all()
    )
    by_mid = {u.material_id: u for u in existing}
    keep = set(desired.keys())
    for mid, row in list(by_mid.items()):
        if mid not in keep:
            db.delete(row)
    for mid, meta in desired.items():
        row = by_mid.get(mid)
        if row:
            row.notes = meta["notes"]
            row.frequency = meta["frequency"]
            row.last_applied_at = meta["last_applied_at"]
            row.is_last_fertilizer = meta["is_last_fertilizer"]
            row.is_last_pesticide = meta["is_last_pesticide"]
        else:
            db.add(
                FarmMaterialUse(
                    farm_id=farm_id,
                    material_id=mid,
                    notes=meta["notes"],
                    frequency=meta["frequency"],
                    last_applied_at=meta["last_applied_at"],
                    is_last_fertilizer=meta["is_last_fertilizer"],
                    is_last_pesticide=meta["is_last_pesticide"],
                )
            )
    db.flush()
    return load_farm_uses(db, farm_id)


def rule_material_context(
    db: Session, farm_id: int, ec: float | None = None
) -> tuple[str | None, list[str]]:
    from app.agro_catalog import commentary_from_materials, format_materials_summary

    uses = load_farm_uses(db, farm_id)
    summary = format_materials_summary(uses)
    notes = commentary_from_materials(uses, ec=ec)
    return summary, notes
