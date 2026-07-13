from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models import Farm, User


def get_owned_farm(
    db: Session,
    farm_id: int,
    user: User,
    *,
    require_active: bool = False,
) -> Farm:
    farm = db.query(Farm).filter(Farm.id == farm_id, Farm.user_id == user.id).first()
    if not farm:
        raise HTTPException(status_code=404, detail="Arazi bulunamadı.")
    if require_active and farm.is_active is False:
        raise HTTPException(
            status_code=403,
            detail="Pasif arazi üzerinde işlem yapılamaz. Önce araziyi aktifleştirin.",
        )
    return farm


ADMIN_ROLES = {"admin", "super_admin"}


def require_admin(user: User) -> User:
    if user.role not in ADMIN_ROLES:
        raise HTTPException(status_code=403, detail="Yönetici yetkisi gerekli.")
    if hasattr(user, "is_active") and user.is_active is False:
        raise HTTPException(status_code=403, detail="Hesap pasif.")
    return user
