import os
from celery import Celery
from app.config import settings

celery_app = Celery(
    "talent_pool_worker",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=["app.tasks.sync_tasks"]
)

# Optional configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)

# Configure periodic tasks
celery_app.conf.beat_schedule = {
    "sync-talent-pool-data-every-hour": {
        "task": "app.tasks.sync_tasks.sync_talent_pool_data",
        "schedule": 3600.0,  # Every hour (in seconds)
    },
    "retry-failed-sync-jobs": {
        "task": "app.tasks.sync_tasks.retry_failed_sync_jobs",
        "schedule": 900.0,  # Every 15 minutes (in seconds)
    },
}

if __name__ == "__main__":
    celery_app.start()