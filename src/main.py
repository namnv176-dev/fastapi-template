from .api import router
from .core.config import settings, EnvironmentOption
from .core.setup import create_application

app = create_application(router=router, settings=settings)

if __name__ == "__main__":
    import uvicorn
    print(settings.ENVIRONMENT == EnvironmentOption.LOCAL)
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=settings.ENVIRONMENT == EnvironmentOption.LOCAL)
