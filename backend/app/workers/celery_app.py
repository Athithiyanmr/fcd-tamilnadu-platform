"""Celery application — configured from settings."""
from celery import Celery
from app.core.config import settings

celery_app = Celery(
    "fcd_worker",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=["app.workers.tasks"],
)

celery_app.conf.update(
    task_track_started=True,
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="Asia/Kolkata",
    enable_utc=True,
    task_acks_late=True,           # don't ack until task completes (crash-safe)
    worker_prefetch_multiplier=1,  # one task at a time per worker (safe for heavy FCD jobs)
)


@celery_app.task(name="health_check")
def health_check():
    return {"status": "ok"}
