"""Application settings loaded from environment (see docs/ENVIRONMENT.md)."""

from functools import lru_cache

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

    database_url: str = "postgresql://archdloom:archdloom@localhost:5432/archdloom"
    redis_url: str = "redis://localhost:6379/0"

    anthropic_api_key: str | None = None
    secret_key: str = "change-me-in-production"
    celery_broker_url: str | None = None

    aws_access_key_id: str | None = None
    aws_secret_access_key: str | None = None
    s3_bucket_name: str | None = None
    s3_region: str | None = None


@lru_cache
def get_settings() -> Settings:
    return Settings()
