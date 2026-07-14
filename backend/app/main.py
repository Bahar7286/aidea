from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import Base, engine
from app.db_migrate import ensure_sqlite_columns
from app.demo_bootstrap import maybe_seed_on_startup, ensure_catalog_on_startup
from app.routers import (
    admin,
    anomalies,
    auth,
    agro_materials,
    billing,
    crop_history,
    devices,
    farms,
    geo,
    irrigation,
    labs,
    recommendations,
    scenarios,
    sensors,
)

Base.metadata.create_all(bind=engine)
ensure_sqlite_columns()
ensure_catalog_on_startup()
maybe_seed_on_startup()

app = FastAPI(title="AgriTwin AI API", version="0.5.7")

origins = [o.strip() for o in settings.cors_origins.split(",") if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins or ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(farms.router)
app.include_router(geo.router)
app.include_router(agro_materials.router)
app.include_router(billing.router)
app.include_router(sensors.router)
app.include_router(devices.router)
app.include_router(scenarios.router)
app.include_router(irrigation.router)
app.include_router(anomalies.router)
app.include_router(labs.router)
app.include_router(crop_history.router)
app.include_router(recommendations.router)
app.include_router(admin.router)


@app.get("/health")
def health():
    return {"status": "ok", "service": "agritwin-api"}
