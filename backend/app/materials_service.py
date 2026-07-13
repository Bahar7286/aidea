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


def sync_farm_materials(
    db: Session,
    farm_id: int,
    *,
    material_ids: list[int] | None = None,
    items: list | None = None,
) -> list[FarmMaterialUse]:
    """Replace farm material associations.

    Prefer `items` (rich). `material_ids` is a shorthand (notes/frequency cleared).
    """
    if items is not None:
        desired: dict[int, dict] = {}
        for raw in items:
            mid = raw.material_id if hasattr(raw, "material_id") else raw["material_id"]
            notes = raw.notes if hasattr(raw, "notes") else raw.get("notes")
            freq = raw.frequency if hasattr(raw, "frequency") else raw.get("frequency")
            last = (
                raw.last_applied_at
                if hasattr(raw, "last_applied_at")
                else raw.get("last_applied_at")
            )
            desired[int(mid)] = {
                "notes": notes,
                "frequency": freq,
                "last_applied_at": last,
            }
    elif material_ids is not None:
        desired = {int(m): {"notes": None, "frequency": None, "last_applied_at": None} for m in material_ids}
    else:
        return load_farm_uses(db, farm_id)

    if desired:
        found = {
            m.id
            for m in db.query(AgroMaterial)
            .filter(AgroMaterial.id.in_(list(desired.keys())), AgroMaterial.is_active.is_(True))
            .all()
        }
        missing = set(desired.keys()) - found
        if missing:
            raise HTTPException(
                status_code=400,
                detail=f"Geçersiz veya pasif malzeme id: {sorted(missing)}",
            )

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
        last = meta["last_applied_at"]
        if isinstance(last, str):
            try:
                last = datetime.fromisoformat(last.replace("Z", "+00:00")).replace(tzinfo=None)
            except ValueError:
                last = None
        if row:
            row.notes = meta["notes"]
            row.frequency = meta["frequency"]
            row.last_applied_at = last
        else:
            db.add(
                FarmMaterialUse(
                    farm_id=farm_id,
                    material_id=mid,
                    notes=meta["notes"],
                    frequency=meta["frequency"],
                    last_applied_at=last,
                )
            )
    db.flush()
    return load_farm_uses(db, farm_id)



def rule_material_context(db: Session, farm_id: int, ec: float | None = None) -> tuple[str | None, list[str]]:
    from app.agro_catalog import commentary_from_materials, format_materials_summary

    uses = load_farm_uses(db, farm_id)
    summary = format_materials_summary(uses)
    notes = commentary_from_materials(uses, ec=ec)
    return summary, notes
