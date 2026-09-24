import logging

from fastapi import FastAPI

from app.api.routes.health import router as health_router
from app.api.routes.users import router as users_router
from app.core.config import get_settings
from app.middleware.request_context import request_context_middleware

settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    debug=settings.app_debug,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)

app.middleware("http")(request_context_middleware)
app.include_router(health_router)
app.include_router(users_router)
