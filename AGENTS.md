# AgriTwin AI — Agent Guide

## Product

AgriTwin AI is a web MVP for **soil moisture and irrigation decision support**.
It combines manual input, simulated IoT data, fixed test datasets, and laboratory analysis results into one soil **data platform** — IoT does not replace lab reports.
It runs a **rule-based** AI engine (ML planned later) with optional OpenRouter Turkish explanations; compares irrigation scenarios; and starts **virtual** irrigation only after user approval.

Claim: moisture- and irrigation-focused working digital twin prototype — not a full soil digital twin. Agro materials are **usage records + AI context only** — no fertilizer prescriptions.

## Stack (as-built)

- Frontend: Next.js App Router + TypeScript + Tailwind + Recharts + Leaflet (OSM)
- Backend: FastAPI + Pydantic v2 + SQLAlchemy 2.0 + JWT (API ≈ 0.5.x)
- DB: SQLite local; Supabase PostgreSQL in prod (`DATABASE_URL`)
- AI: rule engine + anomaly rules; optional OpenRouter hybrid explanations; Scikit-learn / XGBoost later
- Weather: Open-Meteo (`GET /weather/{farm_id}`)
- IoT: REST simulate (`source_type: simulation`) + CLI `iot/simulator/simulate.py` + `/iot/ingest`
- Deploy: Vercel frontend + Render API (see `Progress.md` / `GO_LIVE_PLAN.md`)

## Repo layout

```
frontend/     Next.js app (src/app) — ~39 App Router pages
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
| `techstack.md` | Technology decisions (as-built + roadmap) |
| `designsystem.md` | UI tokens, app shell, SourceBadge, ConfirmGate |
| `ekran-haritasi.md` | 38-screen inventory + MVP-20 UX/UI; **as-built App Router map §7** |
| `TKGM_PARSEL.md` | Unofficial TKGM MEGSIS parcel proxy design (FastAPI `/geo/*` + Leaflet) |
| `canvas.md` / `projeanalizi.md` | Strategy / vision — **MVP scope is mvp/prd/veri-mimarisi**, not the long-term vision |

## Working demo path

Demo login (`POST /auth/demo-login` or UI buttons) → Domates Serası → IoT simulate / manual / dataset → irrigation recommendation → compare scenarios → approve virtual irrigation → moisture + risk update.

Also shipped: zones, devices, lab (file-required upload + confirm), farm materials catalog, crop season history + next-crop suggestions (rotation context, not Rx), AI multi-surface + hub, subscription plan pick (no payments), admin shell.

## Lab / materials notes

- Lab: file required for `lab_report` path; units + user confirmation; no silent OCR commit; real OCR still P2.
- Materials: catalog association on farm; **usage context for AI**, never a prescription product claim.

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

See root `.env.example` (`OPENROUTER_API_KEY`, `SEED_DEMO_USERS`, CORS, etc.).

## Demo users

Four logins: [`DEMO_USERS.md`](DEMO_USERS.md). Seed:

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
- Keep `canvas.md` vision separate from shipped MVP scope.
