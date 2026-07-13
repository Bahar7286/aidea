# AgriTwin Backend

## Setup

```bash
cd backend
python -m venv .venv
# Windows
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

API docs: http://localhost:8000/docs

## Endpoints (v0.3)

| Group | Paths |
|-------|-------|
| Auth | `POST /auth/register`, `POST /auth/login`, `GET /auth/me` |
| Farms | `POST/GET /farms`, `GET/PUT/DELETE /farms/{id}` |
| Sensors | `POST/GET /sensor-readings/{farm_id}`, `POST /predict/irrigation`, `GET /predictions/{farm_id}` |
| Devices / IoT | `POST /devices`, `GET /devices/{farm_id}`, `POST /devices/test-connection`, `POST /iot/simulate` |
| Scenarios | `POST /simulate/scenario` |
| Irrigation | `POST /irrigation/start`, `POST /irrigation/stop`, `GET /irrigation/history/{farm_id}` |
| Anomalies | `GET /anomalies/{farm_id}` |

SQLite is used by default (`agritwin.db`). For Supabase, set `DATABASE_URL` and apply `supabase/001_initial_schema.sql`.

```bash
pytest
```
