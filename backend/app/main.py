"""Minimal ASGI entrypoint for local and Docker runs (expanded in P1-4)."""

from fastapi import FastAPI

app = FastAPI(title="ArchDLoom API", version="0.1.0")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
