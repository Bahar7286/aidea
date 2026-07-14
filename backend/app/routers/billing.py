"""Farmer-facing subscription plans (demo billing — no payment gateway)."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.database import get_db
from app.models import Device, Farm, Prediction, SystemSetting, User
from app.schemas import UserOut

router = APIRouter(prefix="/billing", tags=["billing"])

PLANS: list[dict] = [
    {
        "id": "free",
        "name": "Ücretsiz",
        "price_try": 0,
        "price_label": "0 ₺ / ay",
        "farms_limit": 2,
        "devices_limit": 5,
        "features": [
            "2 arazi",
            "5 cihaz",
            "Temel AI sulama önerisi",
            "Manuel / simülasyon veri",
            "Sanal sulama (onaylı)",
            "Lab görüntüleme (sınırlı)",
        ],
        "soft_paywall": False,
    },
    {
        "id": "pro",
        "name": "Pro (demo)",
        "price_try": 0,
        "price_label": "Demo — ödeme yok",
        "farms_limit": 20,
        "devices_limit": 100,
        "features": [
            "20 arazi",
            "100 cihaz",
            "AI + senaryo karşılaştırması",
            "Lab yükleme / doğrulama",
            "Dijital ikiz haritası",
            "Sanal sulama otomasyonu (onaylı)",
            "Öncelikli demo destek",
        ],
        "soft_paywall": False,
    },
]


class PlanSelectIn(BaseModel):
    plan_id: str = Field(min_length=2, max_length=40)


class BillingPlansOut(BaseModel):
    current_plan: str
    plans: list[dict]
    farms_used: int
    devices_used: int
    ai_queries_used: int
    note: str


def _get_or_set_plan(db: Session, user: User) -> str:
    plan = (getattr(user, "subscription_plan", None) or "free").lower()
    if plan not in {p["id"] for p in PLANS}:
        plan = "free"
        user.subscription_plan = plan
    # Soft flag in system settings (optional override)
    row = (
        db.query(SystemSetting)
        .filter(SystemSetting.key == f"user_plan:{user.id}")
        .first()
    )
    if row and row.value in {p["id"] for p in PLANS}:
        plan = row.value
        if user.subscription_plan != plan:
            user.subscription_plan = plan
    return plan


@router.get("/plans", response_model=BillingPlansOut)
def list_plans(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    plan = _get_or_set_plan(db, current_user)
    farm_ids = [
        f.id
        for f in db.query(Farm).filter(Farm.user_id == current_user.id).all()
    ]
    devices = (
        db.query(Device).filter(Device.farm_id.in_(farm_ids)).count() if farm_ids else 0
    )
    preds = (
        db.query(Prediction).filter(Prediction.farm_id.in_(farm_ids)).count()
        if farm_ids
        else 0
    )
    enriched = []
    for p in PLANS:
        enriched.append({**p, "current": p["id"] == plan})
    db.commit()
    return BillingPlansOut(
        current_plan=plan,
        plans=enriched,
        farms_used=len(farm_ids),
        devices_used=devices,
        ai_queries_used=preds,
        note=(
            "MVP demo abonelik: gerçek ödeme alınmaz. Plan seçimi hesabınızda saklanır; "
            "limitler soft paywall olarak gösterilir."
        ),
    )


@router.put("/plan", response_model=UserOut)
def select_plan(
    payload: PlanSelectIn,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    plan_id = payload.plan_id.lower().strip()
    if plan_id not in {p["id"] for p in PLANS}:
        raise HTTPException(status_code=400, detail="Geçersiz plan.")
    current_user.subscription_plan = plan_id
    key = f"user_plan:{current_user.id}"
    row = db.query(SystemSetting).filter(SystemSetting.key == key).first()
    if row:
        row.value = plan_id
    else:
        db.add(SystemSetting(key=key, value=plan_id))
    db.commit()
    db.refresh(current_user)
    return UserOut.model_validate(current_user)
