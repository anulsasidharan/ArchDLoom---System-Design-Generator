# Backend Workspace

FastAPI service for ArchDLoom: requirements parsing, generation jobs, and downloadable architecture artifacts.

## Layout

- `app/` — Application package (API routes, configuration, database, models)
- `alembic/` — Database migrations
- `tests/` — Backend tests
- `pyproject.toml` — Dependencies and tooling (Ruff, pytest)

## Setup

```bash
cd backend
python -m venv .venv
.\.venv\Scripts\activate    # Windows
# source .venv/bin/activate  # macOS / Linux
pip install -e ".[dev]"
```

Set `DATABASE_URL` (see root `.env.example` and `docs/ENVIRONMENT.md`). Run migrations:

```bash
alembic upgrade head
```

Start the API:

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

- OpenAPI: http://localhost:8000/docs  
- Health: http://localhost:8000/health  

## New migration (after model changes)

```bash
alembic revision --autogenerate -m "describe change"
alembic upgrade head
```
