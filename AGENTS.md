# AgriTwin AI — Agent Guide

## Product

AgriTwin AI is a web MVP for **soil moisture and irrigation decision support**.
It combines manual input, simulated IoT data, fixed test datasets, and (P1) laboratory analysis results into one soil **data platform** — IoT does not replace lab reports.
It runs a **rule-based** AI engine (ML planned later) with safety bounds; compares irrigation scenarios; and starts **virtual** irrigation only after user approval.

Claim: limited but working digital twin focused on moisture and irrigation — not a full soil digital twin. No fertilizer prescriptions in MVP.

## Stack (current)

- Frontend: Next.js App Router + TypeScript + Tailwind (shadcn/ui + Recharts planned)
- Backend: FastAPI + Pydantic v2 + SQLAlchemy 2.0 + JWT
- DB: SQLite by default; Supabase PostgreSQL optional (`DATABASE_URL`)
- AI: rule engine + anomaly rules now; Scikit-learn / XGBoost later
- IoT: REST simulate (`source_type: simulation`) + CLI `iot/simulator/simulate.py`

## Repo layout

```
frontend/     Next.js app (src/app)
backend/      FastAPI API + SQLAlchemy models + tests
ai/           Rule engine copy + datasets/
iot/          Sensor simulation CLI
.cursor/rules Cursor agent rules
*.md          Product docs at repo root (no docs/ folder)
```

## Key docs

| File | Purpose |
|------|---------|
| `prd.md` | Requirements, API, acceptance criteria |
| `mvp.md` | MVP scope and demo scenario |
| `veri-mimarisi.md` | Four data sources, lab upload, layered architecture |
| `iot-mimarisi.md` | Field node, sensors, LoRa/Wi-Fi, calibration, ingest |
| `plan.md` | Phased development plan |
| `Progress.md` | Progress checklists (source of truth for status) |
| `techstack.md` | Technology decisions |
| `designsystem.md` | UI tokens, app shell, SourceBadge, ConfirmGate |
| `ekran-haritasi.md` | 38-screen inventory + MVP-20 UX/UI; **as-built App Router map §7** |
| `canvas.md` / `projeanalizi.md` | Strategy / vision — **MVP scope is mvp/prd/veri-mimarisi**, not the long-term vision |

## Working demo path

Register → create farm → IoT simulate / manual data → irrigation recommendation → compare scenarios → approve virtual irrigation → moisture + risk update.

## Next P1 data feature

Lab analysis: upload report or manual entry with **units + user confirmation** (`veri-mimarisi.md`). Do not auto-save OCR results.

## Run (local)

```bash
# Backend
cd backend
python -m venv .venv
# Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000

# Frontend
cd frontend
# set NEXT_PUBLIC_API_URL=http://localhost:8000 in .env.local
npm install
npm run dev
```

See root `.env.example`.

## Demo users

Four logins (plan + credentials): [`DEMO_USERS.md`](DEMO_USERS.md). Seed:

```bash
cd backend
.venv\Scripts\python.exe -m scripts.seed_demo
```

Shared password: `Secret12`. Primary farmer path uses **Domates Serası**.

## Rules of engagement

- Prefer smallest correct change.
- Label all non-manual data sources in API and UI.
- Update `Progress.md` when completing checklist items.
- Do not implement satellite/drone/fertilizer prescription/yield features in MVP.
- Lab data complements IoT; never claim continuous IoT can replace lab chemistry.
