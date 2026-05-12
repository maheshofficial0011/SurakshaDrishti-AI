# 🟢 CHANGED: Added backend analytics API routes
# REASON: Dashboard and reports need reusable analytics endpoints

from fastapi import APIRouter

from backend.app.database import (
    get_analytics_summary,
    get_events_by_type,
    get_events_by_severity,
    get_risk_zones,
    get_heatmap_data,
)

router = APIRouter()


@router.get("/analytics/summary")
async def analytics_summary():
    return get_analytics_summary()


@router.get("/analytics/by-type")
async def analytics_by_type():
    return {"items": get_events_by_type()}


@router.get("/analytics/by-severity")
async def analytics_by_severity():
    return {"items": get_events_by_severity()}


@router.get("/analytics/risk-zones")
async def analytics_risk_zones():
    return {"items": get_risk_zones()}


@router.get("/analytics/heatmap")
async def analytics_heatmap():
    """
    Return heatmap-ready data for the dashboard.

    This endpoint is additive and does not affect existing analytics routes.
    Used by the Leaflet dashboard panel.
    """

    return get_heatmap_data()