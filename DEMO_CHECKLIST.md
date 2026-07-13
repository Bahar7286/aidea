# Domates Serası — Demo Checklist

Local MVP rehearsal path (no prod deploy required). Shared password: see `DEMO_USERS.md` (`Secret12`).

## Before the room

- [ ] `python -m scripts.seed_demo` from `backend` (venv active)
- [ ] Backend: `uvicorn app.main:app --reload --port 8000`
- [ ] Frontend: `NEXT_PUBLIC_API_URL=http://localhost:8000` + `npm run dev`
- [ ] Browser hard-refresh; logout any stale session
- [ ] Optional: screen-record backup if live demo risks fail

## Live flow (~8–10 min)

1. Login demo farmer → open **Domates Serası**
2. Dashboard: nem + risk + (if irrigations exist) su tasarrufu KPI
3. Data sources / simulate or load test dataset — show `simulation` / `test_dataset` labels
4. Run AI recommendation → open detail → 72h Recharts chart
5. Compare scenarios → approve **virtual** irrigation only
6. Irrigation screen: pump/valve + countdown (or anlık tamamla)
7. Hub reports: water used / savings note (kural tabanlı)
8. Hub settings: show profile edit (name/phone) — optional
9. If time: lab complementary warning wording (IoT ≠ lab replacement)

## Backup if live fails

- Seed script output screenshots
- Pre-recorded video of steps 1–7
- Swagger at `http://localhost:8000/docs` for API demo

## Not demo’d as “done” (blocked without user)

- Production URL / HTTPS / Vercel+backend deploy
- Full presentation rehearsal with judges
- Real OCR / Leaflet map / ML model
