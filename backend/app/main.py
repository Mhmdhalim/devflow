import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes.auth import router as auth_router
from app.api.routes.comments import router as comments_router
from app.api.routes.health import router as health_router
from app.api.routes.issue_labels import router as issue_labels_router
from app.api.routes.issues import router as issues_router
from app.api.routes.labels import router as labels_router
from app.api.routes.organization_access import router as organization_access_router
from app.api.routes.organizations import (
    router as organizations_router,
)
from app.api.routes.projects import router as projects_router
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

if settings.cors_origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=False,
        allow_methods=["*"],
        allow_headers=["*"],
    )

app.middleware("http")(request_context_middleware)

app.include_router(health_router)
app.include_router(users_router)
app.include_router(auth_router)
app.include_router(organizations_router)
app.include_router(organization_access_router)
app.include_router(projects_router)
app.include_router(issues_router)
app.include_router(comments_router)
app.include_router(labels_router)
app.include_router(issue_labels_router)
