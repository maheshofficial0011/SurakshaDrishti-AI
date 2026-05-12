# 🟢 CHANGED: Registered events + analytics + reports + auth routers
# REASON: Enable event APIs, analytics APIs, report export APIs, and auth

from fastapi import APIRouter

from backend.app.api.routes.events import router as events_router
from backend.app.api.routes.analytics import router as analytics_router
from backend.app.api.routes.reports import router as reports_router
from backend.app.api.routes.auth import router as auth_router

# 🟢 CHANGED: Registered demo SOS + dispatch routes
# REASON: Enable mobile SOS simulation and authority response dashboard panel

from backend.app.api.routes.sos import router as sos_router
from backend.app.api.routes.dispatches import router as dispatches_router

api_router = APIRouter()

# Existing routes preserved
api_router.include_router(events_router)
api_router.include_router(analytics_router)
api_router.include_router(reports_router)
api_router.include_router(auth_router)

# New additive demo routes
api_router.include_router(sos_router)
api_router.include_router(dispatches_router)