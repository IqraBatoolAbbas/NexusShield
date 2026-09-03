# Vercel Deployment Guide

NexusShield can be deployed from the repository root as one Vercel project.
The root `vercel.json` builds the React frontend and routes `/api/*` to the
FastAPI function at `api/index.py`.

## Before deployment

- Push the repository to a **public** GitHub repository.
- Confirm `.env`, database files, credentials, keys, and certificates are not
  tracked.
- Rotate any secret that was ever committed.
- Keep the repository root as Vercel's project root; do not select
  `frontend/` as the root directory.

## Vercel configuration

Import the repository in Vercel with the default framework detection. The
repository already contains:

- `vercel.json` for frontend and API routing
- `api/index.py` with the Mangum ASGI adapter
- Root `requirements.txt` referencing backend dependencies
- `frontend` static-build configuration

Add these Vercel Environment Variables:

```text
NEXUSSHIELD_JWT_SECRET=<long-random-secret>
NEXUSSHIELD_LOG_KEY=<long-random-encryption-password>
NEXUSSHIELD_ALLOWED_ORIGINS=https://<your-project>.vercel.app
VITE_API_URL=/api
```

Redeploy after adding or changing variables. The production frontend calls
the API through `/api`, so no separate backend URL is needed.

## Database limitations

Vercel serverless functions do not offer durable local disk storage. When
`VERCEL=1`, NexusShield writes its fallback SQLite file under `/tmp`, which is
appropriate only for a demo and may reset between cold starts.

For durable production data, replace the SQLite connection layer with one of:

- Turso/libSQL
- Neon PostgreSQL
- Supabase PostgreSQL

Keep connection strings and credentials in Vercel Environment Variables, never
in source control.

## Verify after deployment

1. Open the Vercel URL and confirm the public Home page loads.
2. Create a demo account with a selected role.
3. Confirm role-specific sidebar items.
4. Scan a safe prompt and a fake jailbreak prompt.
5. Confirm `/api/analytics` and `/api/scan` requests succeed.
6. Verify that no browser console errors or exposed secrets appear.

## Local fallback

Vercel deployment changes do not affect local development:

```powershell
cd backend
py -3 -m uvicorn app.main:app --reload --port 8000

cd frontend
npm run dev
```
