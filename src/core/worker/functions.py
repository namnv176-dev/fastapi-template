import time

from src.core.celery import celery_app


# -------- background tasks --------
@celery_app.task(bind=True)
def sample_background_task(self, name: str) -> str:
    print(f"Task {name} started")
    time.sleep(5)
    print(f"Task {name} completed")
    return f"Task {name} is complete!"

@celery_app.task(bind=True)
async def asample_background_task(self, name: str) -> str:
    print(f"Task {name} started")
    await asyncio.sleep(5)
    print(f"Task {name} completed")
    return f"Task {name} is complete!"



def main():
    a = sample_background_task("test")
    print(a)

if __name__ == "__main__":
    main()


# a = sample_background_task.delay("test")
# a = await sample_background_task.apply_async(args=["test"])
