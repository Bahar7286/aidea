# AgriTwin Backend

FastAPI API for AgriTwin AI MVP (API version **0.5.6** — see `app/main.py`).

## Setup

```bash
cd backend
python -m venv .venv
# Windows
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

API docs: http://localhost:8000/docs · Health: `GET /health`

## Database

| Ortam | Kaynak |
|-------|--------|
| Yerel (varsayılan) | SQLite `sqlite:///./agritwin.db` |
| Prod | Supabase PostgreSQL (`DATABASE_URL`) — `psycopg2-binary` kurulu |

Schemas: `supabase/001_*.sql`, `002_*.sql` (opsiyonel; runtime `create_all` + migrate helpers).

## Demo seed

```bash
.venv\Scripts\python.exe -m scripts.seed_demo
```

Or set `SEED_DEMO_USERS=1` (Postgres’te boş bırakınca da startup upsert). Credentials: [`DEMO_USERS.md`](../DEMO_USERS.md).

## Endpoint groups (as-built)

| Group | Paths |
|-------|-------|
| Auth | `POST /auth/register`, `/verify`, `/login`, `/demo-login`, `GET/PATCH /auth/me`, forgot/reset |
| Farms | `CRUD /farms`, `/farms/{id}/overview`, `/twin`, `/data-sources` |
| Crop history | `GET/POST /farms/{id}/crop-history`, `PUT/DELETE /crop-history/{id}`, `GET .../crop-suggestions` (rotation; not Rx) |
| Agro materials | `GET /agro-materials`, `GET/PUT /farms/{id}/materials` (usage record; **not** fertilizer Rx) |
| Billing | `GET /billing/plans`, `PUT /billing/plan` (plan selection; no real payments) |
| Sensors / weather | `POST/GET /sensor-readings/{farm_id}`, `GET /datasets`, `POST /datasets/load`, `GET /weather/{farm_id}` (Open-Meteo) |
| AI | `POST /predict/irrigation`, `GET /predictions/{farm_id}`, hub `/recommendations/{farm_id}`, `/hub/{farm_id}` |
| Scenarios | `POST /simulate/scenario`, `/simulate/custom` |
| Irrigation | `POST /irrigation/start|stop`, `GET /status|history/{farm_id}` (user approval + confidence ≥ 60) |
| Devices / IoT | CRUD devices, calibrate, `POST /iot/simulate`, `POST /iot/ingest` |
| Anomalies | `GET /anomalies/{farm_id}` |
| Lab / zones | zones CRUD, lab upload (file + soil-gate for `lab_report`), confirm, summary |
| Admin | `/admin/overview|users|farms|devices|billing|tickets|analytics|settings` |

Hybrid AI: rule engine is the safety floor; optional OpenRouter (`OPENROUTER_API_KEY`) enriches Turkish explanations and lab parse/narrative.

```bash
pytest
```
