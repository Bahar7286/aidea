from datetime import datetime

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.anomaly_service import collect_farm_anomalies
from app.auth import get_current_user
from app.database import get_db
from app.deps import get_owned_farm
from app.models import User

router = APIRouter(tags=["anomalies"])


class AnomalyOut(BaseModel):
    code: str
    severity: str
    title: str
    message: str


class AnomalyReportOut(BaseModel):
    farm_id: int
    has_anomalies: bool
    count: int
    anomalies: list[AnomalyOut]


@router.get("/anomalies/{farm_id}", response_model=AnomalyReportOut)
def get_anomalies(
    farm_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    get_owned_farm(db, farm_id, current_user)
    findings = collect_farm_anomalies(db, farm_id)
    anomalies = [
        AnomalyOut(
            code=f.code,
            severity=f.severity,
            title=f.title,
            message=f.message,
        )
        for f in findings
    ]
    return AnomalyReportOut(
        farm_id=farm_id,
        has_anomalies=len(anomalies) > 0,
        count=len(anomalies),
        anomalies=anomalies,
    )
