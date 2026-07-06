from celery import Celery
from app.core.config import settings

celery_app = Celery(
    "online_cinema",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=["app.tasks.cleanup"],
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    enable_utc=True,
    beat_schedule={
        "cleanup-expired-tokens-every-hour": {
            "task": "app.tasks.cleanup.delete_expired_tokens",
            "schedule": 36.0,
        },
    },
)
