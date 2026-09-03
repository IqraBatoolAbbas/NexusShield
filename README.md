# NexusShield

NexusShield is a lightweight, CPU-friendly, multi-layer firewall and context-aware
AI honeypot middleware MVP for GenAI applications.

## Application screens

- **Command Center**: system health, latest activity, layer coverage, and KPIs.
- **Security Playground**: live prompt scanning and seven-layer terminal trace.
- **Honeypot Console**: trapped actor table and behavioral signature learning.
- **Threat Analytics**: Chart.js threat mix, layer efficiency, and telemetry.
- **Policy & Feedback**: persistent threshold sliders and response toggles.
- **Audit Log**: encrypted event metadata and feedback status.
- **RBAC**: `admin` sees all tenant controls, `developer` sees testing/policy/API tools,
  and `auditor` sees honeypots, analytics, and audit verification only.
- **SaaS access**: unauthenticated visitors can view the pricing page; authenticated
  users receive a tenant-scoped JWT and can provision `ns_live_sec_...` keys.
- **Attack replay**: `POST /api/events/{event_id}/replay` re-runs a tenant-owned
  event through the current seven-layer policy for demos and regression checks.

The backend stores events, honeypot rooms, policies, and feedback in
`backend/data/nexusshield.sqlite3`. Threat traces are encrypted with AES-256-CBC
before they are persisted.

## Run locally

### Backend

```powershell
cd backend
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
py -3 -m uvicorn app.main:app --reload --port 8000
```

For the optional local Transformers/Chroma/Redis adapters:

```powershell
pip install -r requirements-ml.txt
$env:NEXUSSHIELD_ENABLE_LOCAL_MODEL="1"
```

### Frontend

```powershell
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173`. The dashboard works in demo mode with seeded analytics, and live scans use the FastAPI service when it is running.

The frontend is a client-side multi-view app, so navigation does not require a
router/server rewrite. All views use the REST API and refresh automatically.

## Authentication and roles

Signup lets the workspace owner choose `admin`, `developer`, or `auditor`. Admins
can change member roles with the team management API. Protected endpoints enforce
roles on the server, so hiding a sidebar item is not the security boundary:

```text
POST /api/auth/signup
POST /api/auth/login
PATCH /api/team/{member_id}/role
POST /api/audit/verify     # admin, auditor
PUT  /api/policy           # admin, developer
POST /api/keys             # admin, developer
```
