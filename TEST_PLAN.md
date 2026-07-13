# AgriTwin AI — Unit / API Test Plan

**Date:** 2026-07-13  
**Scope:** As-built MVP (soil moisture + irrigation decisions). Not a full digital twin.  
**Out of scope for this plan:** Satellite, drone, fertilizer prescription, yield, real OCR, Leaflet map, ML models.

---

## 1. Stack & how to run

| Layer | Tool | Command |
|--------|------|---------|
| Backend unit + API | pytest | `cd backend && .venv\Scripts\python.exe -m pytest tests -q` |
| Frontend (planned) | Vitest / Playwright (not required yet) | Document critical paths below; implement P0 first |
| Manual smoke | Browser + local servers | See §6 |

Backend fixtures use in-memory SQLite (`StaticPool`) and `TestClient` — no external DB needed.

---

## 2. Current coverage (as of this plan)

Existing files under `backend/tests/`:

| File | Focus |
|------|--------|
| `test_auth_onboarding.py` | Register, verify, login, `PATCH /auth/me`, role |
| `test_happy_path.py` | Vertical slice + hub |
| `test_api_p0.py` | P0 API surface |
| `test_crud_complete.py` | Farm/zone/device/lab CRUD + auth me |
| `test_lab_zones.py` | Lab reports, zones, confirm |
| `test_devices.py` | Devices + calibrate |
| `test_twin_sources.py` | Twin view + data sources + datasets |
| `test_ai_engine.py` | Rule engine pure unit |
| `test_anomaly.py` | Anomaly + IoT–lab conflict + water usage |
| `test_recommendations.py` | Recommendations, hub, irrigation status fields |
| `test_admin.py` | Admin-only routes |

**Target:** keep all green after each feature PR. Prefer API tests for routers; pure unit tests for `ai_engine`, `anomaly`, `validation`, `water_report`.

---

## 3. Conventions

- Test names: `test_<behavior>` (pytest).
- Auth helper: register → verify code `123456` → Bearer token (match existing tests).
- Demo password in docs: `Secret12` — use in seeds, not hardcode secrets in CI env files.
- Assert Turkish error messages only when the API guarantees them.
- Never claim simulated readings as real sensors in assertions/UI copy checks.
- Virtual irrigation: reject when `user_approved=false`.

---

## 4. Matrix by module

### Auth — P0
| Case | Type | Notes |
|------|------|--------|
| Register + verify + login | API | Existing |
| `GET /auth/me` | API | Existing |
| `PATCH /auth/me` name/phone | API | Existing |
| `PATCH /auth/me` password wrong current | API | Existing |
| Role patch / verify gates | API | Existing |

### Farms / zones — P0
| Case | Type | Notes |
|------|------|--------|
| Create / list / get / update | API | Existing |
| Soft-delete + inactive mutations 403 | API | Existing |
| Zone CRUD | API | Existing |
| `GET /farms/{id}/overview` includes water fields | API | Extended |

### Devices / sensors / datasets — P0
| Case | Type | Notes |
|------|------|--------|
| Device create / update / delete | API | Existing |
| Manual reading + source_type | API | Existing |
| Simulate + ingest | API | Existing |
| Dataset list + load → `test_dataset` | API | Existing |
| Readings history limit cap 200 | API | Add if missing |

### Lab — P1
| Case | Type | Notes |
|------|------|--------|
| Manual entry requires unit + confirm | API | Existing |
| Unconfirmed OCR/sim extract not auto-saved as truth | API | Existing |
| Update / delete report | API | Existing |

### AI / irrigation — P0
| Case | Type | Notes |
|------|------|--------|
| Rule engine irrigation needed / confidence | Unit | Existing |
| Predict endpoint persists moisture_24/48/72 | API | Existing |
| Scenario / custom simulate | API | Existing |
| Start without approval → 400 | API | Existing |
| Status: `pump_status`, `remaining_seconds` | API | Added |
| Stop updates moisture when applicable | API | Existing |

### Anomaly / validation — P0/P1
| Case | Type | Notes |
|------|------|--------|
| Sudden moisture jump | Unit | Existing |
| Post-irrigation no rise | Unit | Existing |
| IoT–lab EC/pH conflict (confirmed lab only) | Unit | Added |
| Disclaimer: IoT does not replace lab | Unit | Message assert |
| Water usage vs calendar baseline | Unit | Added |

### Hub / reports — P1
| Case | Type | Notes |
|------|------|--------|
| Hub reports include `water_savings` | API | Added |
| Alerts include conflict codes when data set | API | Optional extend |
| Overview savings KPI fields null without sessions | API | Smoke |

### Admin — P1
| Case | Type | Notes |
|------|------|--------|
| Non-admin 403 | API | Existing |
| Overview / users / analytics | API | Existing |

---

## 5. Frontend critical paths (plan only — implement later)

Prefer Playwright smoke over unit-heavy component tests for MVP.

| Priority | Path | Assertions |
|----------|------|------------|
| P0 | Login → dashboard | Farm select, KPI cards, Source labels if reading is sim |
| P0 | Farm → AI → detail | Recharts 72h sparkline renders with prediction |
| P0 | History F15 | 72h period + Recharts line + table |
| P0 | Irrigation | Confirm gate; pump/valve; countdown while running |
| P1 | Hub settings | `updateMe` name/phone/password |
| P1 | Hub reports | Water used / savings visible after irrigation |
| P1 | Lab | Confirm before save; conflict alert if EC mismatch |
| P1 | Mobile | Primary buttons ≥ 44px (`min-h-11`) on hub/irrigation |

Do **not** snapshot entire dashboards. Prefer role-based locators and Turkish copy spots that must not regress (ConfirmGate, SourceBadge).

---

## 6. Manual smoke checklist

1. Start API (`uvicorn app.main:app --reload --port 8000`) and Next (`npm run dev`).
2. Login demo farmer (`DEMO_USERS.md`, password `Secret12`).
3. Domates Serası: overview → moisture KPI + savings (after ≥1 completed irrigation).
4. Sensors history: 72 Saat + chart.
5. AI detail: 72h Recharts chart.
6. Irrigation: start virtual session → countdown + pump open → stop.
7. Hub → Ayarlar: change name/phone; logout/login.
8. Lab confirm + mismatched EC → uyarı “IoT–lab” (complementary wording).

---

## 7. Gaps / deferred

| Item | Reason |
|------|--------|
| Frontend automated suite | Not yet scaffolded; follow §5 |
| Prod deploy E2E | Needs cloud credentials |
| Real OCR / Leaflet / ML | P2 |
| Performance / load tests | Post-MVP |

---

## 8. Definition of done for a PR

1. `pytest tests -q` green.
2. New pure logic (`anomaly`, `water_report`, AI rules) has unit tests.
3. New REST fields covered in at least one API test.
4. `Progress.md` checklist updated if a tracked item finishes.
