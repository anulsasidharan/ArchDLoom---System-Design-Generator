from typing import Annotated

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from app.config import Settings, get_settings

router = APIRouter(tags=["health"])


class HealthResponse(BaseModel):
    status: str = Field(description="Service liveness.")
    environment: str
    version: str
    database: str = Field(description="connected | unreachable | unchecked")


def _probe_database(settings: Settings) -> str:
    if not settings.database_url:
        return "unchecked"
    try:
        from sqlalchemy import text

        from app.db.session import engine

        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return "connected"
    except Exception:
        return "unreachable"


@router.get("/health", response_model=HealthResponse)
def health(settings: Annotated[Settings, Depends(get_settings)]) -> HealthResponse:
    return HealthResponse(
        status="ok",
        environment=settings.environment,
        version=settings.app_version,
        database=_probe_database(settings),
    )
