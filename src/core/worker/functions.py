import logging
import time

from src.core.celery import celery_app


# -------- background tasks --------
@celery_app.task(name="sample_background_task")
def sample_background_task(name: str) -> str:
    logging.info(f"Task {name} started")
    time.sleep(5)
    logging.info(f"Task {name} completed")
    return f"Task {name} is complete!"
