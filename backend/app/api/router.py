# 🟢 CHANGED: Registered events + analytics + reports routers
# REASON: Enable event APIs, analytics APIs, and report export APIs

from fastapi import APIRouter

from backend.app.api.routes.events import router as events_router
from backend.app.api.routes.analytics import router as analytics_router
from backend.app.api.routes.reports import router as reports_router
from backend.app.api.routes.auth import router as auth_router

api_router = APIRouter()

api_router.include_router(events_router)
api_router.include_router(analytics_router)
api_router.include_router(reports_router)
api_router.include_router(auth_router)
