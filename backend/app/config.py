"""Application settings loaded from environment (see docs/ENVIRONMENT.md)."""

from functools import lru_cache

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(".env", "../.env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "ArchDLoom API"
    app_version: str = "0.1.0"
    environment: str = "development"

    database_url: str = "postgresql+psycopg://archdloom:archdloom@localhost:5432/archdloom"
    redis_url: str = "redis://localhost:6379/0"

    @field_validator("database_url", mode="before")
    @classmethod
    def use_psycopg3_driver(cls, v: object) -> object:
        """Map bare postgresql:// to psycopg3; SQLAlchemy's default driver is psycopg2."""
        if isinstance(v, str) and v.startswith("postgresql://"):
            return "postgresql+psycopg://" + v[len("postgresql://") :]
        return v

    anthropic_api_key: str | None = None
    anthropic_model: str = "claude-3-5-sonnet-20241022"
    secret_key: str = "change-me-in-production"
    celery_broker_url: str | None = None
    celery_result_backend: str | None = None

    aws_access_key_id: str | None = None
    aws_secret_access_key: str | None = None
    s3_bucket_name: str | None = None
    s3_region: str | None = None

    #: Optional directory for resolving relative `icon_url` paths (defaults to `backend/static/icons`).
    icon_assets_root: str | None = None


@lru_cache
def get_settings() -> Settings:
    return Settings()
