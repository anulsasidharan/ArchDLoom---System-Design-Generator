# Environment variables and secrets

ArchDLoom reads configuration from the process environment and optional `.env` files. The FastAPI app loads `.env` from the `backend/` directory first, then the repository root (see `app.config.Settings`).

## Backend (FastAPI)

| Variable | Required | Description |
| --- | --- | --- |
| `DATABASE_URL` | Yes (for DB + Alembic) | PostgreSQL connection string, e.g. `postgresql://user:pass@localhost:5432/archdloom` |
| `REDIS_URL` | For jobs/cache (later) | e.g. `redis://localhost:6379/0` |
| `ENVIRONMENT` | No | `development`, `staging`, or `production` (default: `development`) |
| `SECRET_KEY` | Production | Signing / session secret; change from the default in real deployments |
| `ANTHROPIC_API_KEY` | For generation | Claude API key used by requirement parsing and document generation services |
| `CELERY_BROKER_URL` | Workers | Defaults to `REDIS_URL` if unset when wiring Celery |
| `AWS_ACCESS_KEY_ID` | Optional | S3 access for assets and generated bundles |
| `AWS_SECRET_ACCESS_KEY` | Optional | S3 secret |
| `S3_BUCKET_NAME` | Optional | Target bucket for uploads and exports |
| `S3_REGION` | Optional | e.g. `us-east-1` |

## Claude (Anthropic) API

1. Create an API key in the [Anthropic Console](https://console.anthropic.com/).
2. Set `ANTHROPIC_API_KEY` in your environment or in `backend/.env` (never commit real keys).
3. For local Docker Compose, you can add `ANTHROPIC_API_KEY=...` to the root `.env`; the `api` service should pass it through when you extend `docker-compose.yml` with that variable.
4. CI must not use real keys: use mock services or skip integration tests that call the network.

## Frontend (Next.js)

| Variable | Required | Description |
| --- | --- | --- |
| `NEXT_PUBLIC_API_URL` | No (default in dev) | Base URL of the FastAPI service, e.g. `http://localhost:8000` |
| `NEXT_PUBLIC_ENVIRONMENT` | No | Echo of deploy environment for client-side display |

## Local development quick reference

- Copy the root `.env.example` to `.env` and adjust ports if needed.
- Run Postgres and Redis via `docker compose up -d db redis`.
- From `backend/`, install with `pip install -e ".[dev]"` and run `alembic upgrade head` with `DATABASE_URL` pointing at the local database.
- Start the API with `uvicorn app.main:app --reload` from `backend/`.
- From the repo root, `npm install` then `npm run dev:frontend` for the Next.js app.

## Security notes

- Treat `.env` and any file containing keys as **local-only**; they are listed in `.gitignore`.
- Rotate `ANTHROPIC_API_KEY` and `SECRET_KEY` if they leak.
- In production, prefer a secret manager (AWS Secrets Manager, GCP Secret Manager, etc.) over plain environment files on disk.
