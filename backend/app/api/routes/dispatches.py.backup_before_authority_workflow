"""
SurakshaNet AI — Dispatches API Route

Purpose:
- Expose latest demo authority response dispatches to dashboard.
- Used by the Authority Response panel.
- Read-only for now to keep the demo stable.

Important:
- Does not call real emergency services.
- Does not modify Event Engine.
- Does not modify tracking/detection.
"""

from fastapi import APIRouter, Query

from backend.app.database import get_dispatches

router = APIRouter()


@router.get("/dispatches")
async def list_dispatches(
    limit: int = Query(default=50, ge=1, le=200),
):
    """
    Return latest authority dispatch records.

    Example response:
    {
        "dispatches": [
            {
                "dispatch_id": "DSP-0001",
                "event_id": 1,
                "event_type": "SOS_ALERT",
                "unit_type": "POLICE",
                "unit_name": "UNIT-01 ALPHA",
                "status": "DISPATCHED",
                "eta_minutes": 3,
                "location_label": "Demo Laptop Location",
                "created_at": "..."
            }
        ],
        "count": 1
    }
    """

    dispatches = get_dispatches(limit=limit)

    return {
        "dispatches": dispatches,
        "count": len(dispatches),
    }