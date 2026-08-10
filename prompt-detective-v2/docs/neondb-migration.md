# Prompt Detective → NeonDB Migration Runbook

This guide captures everything required to rebuild the database schema on NeonDB, update the Render backend, keep the Vercel frontend in sync, and validate the end-to-end stack. All steps are aligned with free-tier limits across NeonDB, Render, and Vercel.

## 1. Schema Overview

The canonical schema is expressed in `backend/migrations/20251031_neondb_init.sql`. Tables and key traits:

- `users`: core account profile, auth flags, usage counters, timestamps.
- `api_keys`: hashed API keys bound to users.
- `analysis_jobs`: per-upload processing status and results.
- `usage_logs`: audit trail for platform actions.
- `subscriptions`: paid plan state, billing metadata, Razorpay linkage.
- `payments`: Razorpay payments and metadata.
- `credit_packs`: bolt-on analysis credits.
- `admin_notes`: private staff notes per user.
- `otp_codes`: short lived verification codes.
- `email_logs`: transactional email tracking.
- `waitlist_subscribers`: prelaunch marketing capture with unique email+plan.
- `contact_messages`: support tickets originating from the frontend.

Each table already includes indexes, constraints, and cascading rules tuned for PostgreSQL. Re-run the SQL script verbatim to bootstrap a new Neon project.

## 2. NeonDB Setup

1. Create a free Neon project at https://neon.tech (PostgreSQL 15+).
2. Generate a pooled connection string from the **Connection Details → Pooled** tab. The host ends with `-pooler.neon.tech`.
3. Ensure the string uses `postgresql://` (or update from `postgres://`). Do not embed it in code; store it as `DATABASE_URL`.
4. Add `?sslmode=require` if Neon did not append it automatically.
5. Optional but recommended tuning for free-tier compatibility:
   - `DB_POOL_ENABLED=true`
   - `DB_POOL_SIZE=5`
   - `DB_MAX_OVERFLOW=0`
   - `DB_POOL_TIMEOUT=30`
   - `DB_POOL_RECYCLE=300`
   - `DB_PRE_PING=true`
   - `DB_STATEMENT_TIMEOUT_MS=30000`
   - `DB_CONNECT_RETRIES=5`

Record admin credentials securely (Neon dashboard → Project settings). Do not commit them.

## 3. Deploying the Schema

Run the schema script against an empty Neon database using any of the following:

```bash
# Option A: psql (recommended)
psql "$DATABASE_URL" -f backend/migrations/20251031_neondb_init.sql

# Option B: via Render job/one-off task
python -c "from sqlalchemy import text, create_engine;\nengine = create_engine('$DATABASE_URL');\nwith engine.connect() as conn:\n    with open('backend/migrations/20251031_neondb_init.sql') as ddl:\n        conn.execute(text(ddl.read()))"
```

Confirm tables with:

```bash
psql "$DATABASE_URL" -c "\dt"
```

## 4. Backend (Render) Configuration

Environment variables required on Render:


 In Render’s backend service, set the following env vars to the new values before redeploying (enter the values without wrapping quotes):
- Redeploy the Render service after setting env vars so the new engine boots with Neon.
- Confirm Render outbound networking allows `*.neon.tech` (it does by default).
- Keep `run_migrations.py` enabled so legacy sqlite columns are ignored.

## 5. Frontend (Vercel) Configuration

- No direct database access from the frontend. Verify only the API base URL (`NEXT_PUBLIC_API_BASE_URL` or similar) points to the Render deployment.
- Ensure the Render backend CORS list (`ALLOWED_ORIGINS`) includes the Vercel domain.
- Update any Vercel environment variable referencing the backend origin if a new hostname is used.

## 6. Connection & Stack Validation

1. Run backend self-check from the project root (Windows PowerShell example):

   ```powershell
   cd backend
   python tools/test_neondb_connection.py
   ```

   Expected output: table confirmation, CRUD smoke test, pool status.

2. Start the FastAPI server locally (optional) and hit `/health`:

   ```powershell
   uvicorn app.main:app --reload
   Invoke-WebRequest http://127.0.0.1:8000/health
   ```

3. Deploy to Render and verify `/health` from the public URL.
4. Exercise critical user flows from the Vercel frontend (login, signup, analysis job, contact form) and monitor backend logs for database errors.

## 7. Deployment Order & Commands

1. **Database** – execute `backend/migrations/20251031_neondb_init.sql` on Neon.
2. **Backend** – set Render env vars, redeploy (Render dashboard → Manual Deploy → Latest commit).
3. **Frontend** – update Vercel env vars if needed, redeploy (Vercel dashboard → Deploy).

Verification checklist after each stage:

- Database: `psql "$DATABASE_URL" -c "SELECT COUNT(*) FROM users;"`
- Backend: `Invoke-WebRequest https://<render-app>/health`
- Frontend: Load https://<vercel-app>/ and ensure authenticated routes respond.

Rollback plan:

1. Flip Render `DATABASE_URL` back to the previous database (if still available) and redeploy.
2. Restore Neon schema from backup (`pg_dump` output) if required.
3. Pause frontend deployment by reverting to the last known good Vercel build.

## 8. Architecture (text diagram)

```
[Vercel Frontend (Next/Vite)]
        | HTTPS
        v
[Render FastAPI Backend]
        | (pooled SSL, 30 s timeout)
        v
[NeonDB PostgreSQL (Pooled Endpoint)]
```

Optional integrations (Cloudinary, Razorpay, Brevo) remain unchanged.

## 9. Troubleshooting

| Symptom | Likely Cause | Resolution |
|---------|--------------|------------|
| `psycopg2.OperationalError: connection timed out` | Missing `sslmode=require` or incorrect host | Use pooled host `<project>-pooler.neon.tech` and append `?sslmode=require`. |
| `too many connections` on Neon | Pool size too large | Keep `DB_POOL_SIZE<=5`, `DB_MAX_OVERFLOW=0`, rely on Neon pooling. |
| Backend freezes during cold start | Connection warm-up still in progress | Engine now retries with exponential backoff; increase `DB_CONNECT_RETRIES` if needed. |
| `relation "users" does not exist` | Schema script not executed | Re-run `backend/migrations/20251031_neondb_init.sql` against Neon. |
| CORS errors on frontend | Render allowed origins missing Vercel URL | Add the deployed Vercel origin to `ALLOWED_ORIGINS`. |

## 10. Future Schema Changes

- Update models in `backend/app/models/`.
- Generate a follow-up SQL migration (copy `20251031_neondb_init.sql`, keep only diffs).
- Apply to Neon with `psql "$DATABASE_URL" -f <new_script>.sql`.
- Commit the migration script and redeploy backend after ensuring `tools/test_neondb_connection.py` still passes.

Keep this runbook alongside the repo to ensure future contributors can reproduce the Neon setup quickly.
