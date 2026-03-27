from celery import Celery

from src.core.config import settings

celery_app = Celery(
    "worker",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
)

# Optional: Configuration overrides
celery_app.conf.update(
    task_track_started=True,
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    # Celery 5.x uses task_ignore_result=False by default,
    # but we can explicitly set it if needed.
)

# Auto-discover tasks from modules
celery_app.autodiscover_tasks(["src.core.worker"], related_name="functions")
