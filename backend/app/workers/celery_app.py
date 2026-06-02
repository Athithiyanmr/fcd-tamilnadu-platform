from celery import Celery
from app.core.config import settings

celery_app = Celery(
    'fcd_tasks',
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=['app.workers.tasks']
)

celery_app.conf.update(
    task_serializer='json',
    result_serializer='json',
    accept_content=['json'],
    timezone='Asia/Kolkata',
    enable_utc=True,
    # Annual FCD run — 1 March at 06:00 IST
    beat_schedule={
        'annual-fcd-tamilnadu': {
            'task': 'app.workers.tasks.run_fcd_pipeline',
            'schedule': '0 0 1 3 *',  # cron: 1 March midnight UTC
            'args': ['TamilNadu', '2026'],
        },
    }
)
