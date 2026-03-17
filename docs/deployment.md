# Deployment Guide

Backend → Railway (Docker), Frontend → Vercel.

## Prerequisites

- GNN checkpoint committed at `checkpoints/gnn_best.pt` ✅
- `backend/Dockerfile` uses `python:3.11-slim` ✅
- `frontend/src/services/api.ts` reads `VITE_API_URL` env var ✅

---

## Backend — Railway

1. Go to [railway.app](https://railway.app) → **New Project** → **Deploy from GitHub repo**
2. Select `ADMEPredictor`, set **Root Directory** to `backend`
3. Railway detects the Dockerfile automatically
4. Under **Settings → Environment**, add:
   - `PYTHONPATH` = `.`
5. Deploy — copy the public URL once it's live (e.g. `https://admepredictor-production.up.railway.app`)
6. Smoke test: `curl https://<railway-url>/health`

---

## Frontend — Vercel

1. Go to [vercel.com](https://vercel.com) → **New Project** → import `ADMEPredictor`
2. Set **Root Directory** to `frontend`
3. Framework preset: **Vite** (auto-detected)
4. Under **Environment Variables**, add:
   - `VITE_API_URL` = `https://<railway-url>` (no trailing slash, no `/api` suffix)
5. Deploy

---

## After Both Are Live

Tighten CORS in `backend/main.py`:

```python
allow_origins=["https://your-app.vercel.app"],
```

Redeploy the backend after changing this.

---

## What's Not in Production

- **RF model** (`checkpoints/rf/`) is gitignored (221MB). The GNN handles all four properties; RF is fallback-only and not needed for the live demo.

---

## Ongoing Deploys

Both services auto-deploy on push to `main` once connected to GitHub.
To force a redeploy without a code change, use the Railway/Vercel dashboard.
