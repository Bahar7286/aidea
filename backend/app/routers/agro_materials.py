"""Agro-material reference catalog + farm associations."""

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.agro_catalog import ensure_agro_catalog
from app.auth import get_current_user
from app.database import get_db
from app.deps import get_owned_farm
from app.materials_service import load_farm_uses, sync_farm_materials
from app.models import AgroMaterial, User
from app.schemas import (
    AgroMaterialOut,
    FarmMaterialUseOut,
    FarmMaterialsSync,
)

router = APIRouter(tags=["agro-materials"])


@router.get("/agro-materials", response_model=list[AgroMaterialOut])
def list_catalog(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    kind: str | None = Query(default=None, description="fertilizer|plant_protection"),
):
    ensure_agro_catalog(db)
    db.commit()
    q = db.query(AgroMaterial).filter(AgroMaterial.is_active.is_(True))
    if kind:
        q = q.filter(AgroMaterial.kind == kind)
    rows = q.order_by(AgroMaterial.sort_order, AgroMaterial.id).all()
    return [AgroMaterialOut.model_validate(r) for r in rows]


@router.get("/farms/{farm_id}/materials", response_model=list[FarmMaterialUseOut])
def list_farm_materials(
    farm_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    get_owned_farm(db, farm_id, current_user)
    uses = load_farm_uses(db, farm_id)
    return [FarmMaterialUseOut.model_validate(u) for u in uses]


@router.put("/farms/{farm_id}/materials", response_model=list[FarmMaterialUseOut])
def put_farm_materials(
    farm_id: int,
    payload: FarmMaterialsSync,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    get_owned_farm(db, farm_id, current_user, require_active=True)
    uses = sync_farm_materials(db, farm_id, items=payload.items)
    db.commit()
    return [FarmMaterialUseOut.model_validate(u) for u in uses]


@router.delete(
    "/farms/{farm_id}/materials/{use_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_farm_material(
    farm_id: int,
    use_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    from app.models import FarmMaterialUse

    get_owned_farm(db, farm_id, current_user, require_active=True)
    row = (
        db.query(FarmMaterialUse)
        .filter(FarmMaterialUse.id == use_id, FarmMaterialUse.farm_id == farm_id)
        .first()
    )
    if row:
        db.delete(row)
        db.commit()
    return None
