# AgriTwin Frontend

Next.js App Router + TypeScript + Tailwind.

## Setup

```bash
cd frontend
# Create .env.local:
# NEXT_PUBLIC_API_URL=http://localhost:8000
npm install
npm run dev
```

Open http://localhost:3000

## Pages

| Route | Purpose |
|-------|---------|
| `/` | Landing |
| `/register`, `/login` | Auth |
| `/dashboard` | Farm list |
| `/farms/new` | Create farm |
| `/farms/[id]` | Manual data, IoT simulate, AI, scenarios, virtual irrigation, anomalies |

Backend must be running on port 8000 (see `../AGENTS.md` and `../backend/README.md`).

```bash
npm run build
```
