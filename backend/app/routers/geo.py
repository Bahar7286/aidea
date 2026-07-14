"""Geo / TKGM MEGSIS proxy — unofficial public endpoints, no API key."""

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, Field

from app.auth import get_current_user
from app.models import User
from app.tkgm_client import (
    fetch_districts,
    fetch_neighborhoods,
    fetch_parcel,
    fetch_provinces,
    http_error_from_tkgm,
    TkgmNotFound,
    TkgmUnavailable,
)

router = APIRouter(prefix="/geo", tags=["geo"])


class GeoOption(BaseModel):
    id: int | str
    name: str


class CentroidOut(BaseModel):
    lat: float
    lng: float


class ParcelOut(BaseModel):
    mahalle: str | None = None
    mahalle_id: int | str | None = None
    ada: str
    parsel: str
    area_da: float | None = None
    centroid: CentroidOut
    geometry: dict = Field(description="GeoJSON geometry")


@router.get("/provinces", response_model=list[GeoOption])
def list_provinces(current_user: User = Depends(get_current_user)):
    del current_user
    try:
        return fetch_provinces()
    except (TkgmUnavailable, TkgmNotFound, ValueError) as exc:
        raise http_error_from_tkgm(exc) from exc


@router.get("/districts", response_model=list[GeoOption])
def list_districts(
    il_id: int = Query(..., description="TKGM il id (ilListe properties.id)"),
    current_user: User = Depends(get_current_user),
):
    del current_user
    try:
        return fetch_districts(il_id)
    except (TkgmUnavailable, TkgmNotFound, ValueError) as exc:
        raise http_error_from_tkgm(exc) from exc


@router.get("/neighborhoods", response_model=list[GeoOption])
def list_neighborhoods(
    ilce_id: int = Query(..., description="TKGM ilçe id"),
    current_user: User = Depends(get_current_user),
):
    del current_user
    try:
        return fetch_neighborhoods(ilce_id)
    except (TkgmUnavailable, TkgmNotFound, ValueError) as exc:
        raise http_error_from_tkgm(exc) from exc


@router.get("/parcel", response_model=ParcelOut)
def get_parcel(
    mahalle_id: int = Query(...),
    ada: str = Query(..., min_length=1),
    parsel: str = Query(..., min_length=1),
    current_user: User = Depends(get_current_user),
):
    del current_user
    try:
        return fetch_parcel(mahalle_id, ada, parsel)
    except (TkgmUnavailable, TkgmNotFound, ValueError) as exc:
        raise http_error_from_tkgm(exc) from exc
