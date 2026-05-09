# Backend Workspace

FastAPI service for ArchDLoom: requirements parsing, generation jobs, and downloadable architecture artifacts.

## Layout

- `app/` — Application package (API routes, configuration, database, models)
- `alembic/` — Database migrations
- `tests/` — Backend tests
- `pyproject.toml` — Dependencies and tooling (Ruff, pytest)
- `uv.lock` — Locked dependency versions (install with [`uv`](https://docs.astral.sh/uv/))

## Setup

Install [uv](https://docs.astral.sh/uv/getting-started/installation/), then:

```bash
cd backend
uv sync --extra dev
```

This creates `.venv/` and installs the package in editable mode with dev extras. Activate the venv if you prefer (`.\.venv\Scripts\activate` on Windows, `source .venv/bin/activate` on macOS/Linux), or prefix commands with `uv run`.

Set `DATABASE_URL` (see root `.env.example` and `docs/ENVIRONMENT.md`). Run migrations:

```bash
uv run alembic upgrade head
```

Start the API:

```bash
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

- OpenAPI: http://localhost:8000/docs  
- Health: http://localhost:8000/health  

## New migration (after model changes)

```bash
uv run alembic revision --autogenerate -m "describe change"
uv run alembic upgrade head
```

## Lockfile

After editing dependencies in `pyproject.toml`, refresh the lockfile:

```bash
uv lock
```
