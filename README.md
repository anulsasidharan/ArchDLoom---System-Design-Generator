# ArchDLoom - System Design Generator

ArchDLoom is an AI-powered monorepo for generating production-oriented system design documentation (PRD, HLD, LLD, evolution plans, and architecture diagrams).

This repository now includes the Phase 1 monorepo foundation:
- Shared root tooling and conventions
- `backend/` Python service workspace
- `frontend/` Next.js workspace
- Starter project structure for upcoming implementation phases

## Monorepo Layout

```text
archdloom/
├── backend/                # FastAPI service workspace
│   ├── app/
│   ├── tests/
│   └── pyproject.toml
├── frontend/               # Next.js app workspace
│   ├── app/
│   ├── components/
│   ├── lib/
│   └── package.json
├── docs/                   # Project documentation
├── scripts/                # Utility/setup scripts
├── .github/workflows/      # CI workflow definitions
├── package.json            # Root workspace scripts
├── .editorconfig
├── TASKS.md
└── CLAUDE.md
```

## Tooling Baseline

- **Node workspaces** from the repository root for frontend workflows
- **Python backend** via `backend/pyproject.toml` and `uv` (lockfile: `backend/uv.lock`)
- **Editor consistency** via `.editorconfig`
- **Task tracking** in `TASKS.md` by phase and branch

## Quick Start

### 1) Install frontend dependencies

```bash
npm install
```

### 2) Verify workspace scripts

```bash
npm run lint
npm run test
```

These are currently scaffold scripts and will be expanded as features are implemented.

## Development Workflow

1. Pick the branch tied to the next task in `TASKS.md`.
2. Keep changes scoped to that task only.
3. Mark the task status as complete when done.
4. Merge tasks in order within each phase.

## Current Status

Phase 1 monorepo scaffolding is in place. Next tasks can now build on this structure (Docker, migrations, API bootstrap, and Next.js app wiring).
