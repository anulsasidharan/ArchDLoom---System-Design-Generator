"""FastAPI application entry."""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.routes import generation as generation_routes
from app.api.routes import health as health_routes
from app.config import get_settings


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    yield


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description=(
            "ArchDLoom system design generator API: requirements ingestion, generation jobs, "
            "and downloadable architecture artifacts."
        ),
        openapi_url="/openapi.json",
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan,
    )
    app.include_router(health_routes.router)
    app.include_router(generation_routes.router, prefix="/api/v1")
    return app


app = create_app()
