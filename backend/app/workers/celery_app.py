"""Celery application instance (used by worker processes and task producers)."""

from __future__ import annotations

from celery import Celery

from app.config import get_settings


def make_celery() -> Celery:
    settings = get_settings()
    broker = settings.celery_broker_url or settings.redis_url
    backend = settings.celery_result_backend or broker
    app = Celery(
        "archdloom",
        broker=broker,
        backend=backend,
        include=["app.workers.tasks"],
    )
    app.conf.update(
        task_serializer="json",
        accept_content=["json"],
        result_serializer="json",
        timezone="UTC",
        enable_utc=True,
    )
    return app


celery_app = make_celery()
