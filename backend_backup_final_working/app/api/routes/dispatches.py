"""
SurakshaDrishti AI — Authority Dispatches API Route

Purpose:
- Expose authority response incidents to dashboard.
- Support realistic incident workflow:
  PENDING -> ASSIGNED -> DISPATCHED/RUNNING -> RESOLVED

Important:
- Does not call real emergency services.
- Does not modify Event Engine.
- Does not modify tracking/detection.
- Does not change camera pipeline.
"""

from fastapi import APIRouter, HTTPException, Query

from backend.app.database import (
    get_dispatches,
    get_dispatch_status_counts,
    update_dispatch_status,
)
from backend.app.websocket_manager import broadcast_event

router = APIRouter()


async def _broadcast_dispatch_update(dispatch: dict):
    """
    Broadcast dispatch status changes through the existing WebSocket system.

    We keep the current WebSocket manager unchanged by sending an event-like
    payload with type DISPATCH_UPDATE.
    """

    if not dispatch:
        return

    await broadcast_event(
        {
            "type": "DISPATCH_UPDATE",
            "severity": "INFO",
            "message": (
                f"{dispatch.get('unit_name', 'Authority unit')} status updated to "
                f"{dispatch.get('status', 'UNKNOWN')} for "
                f"{dispatch.get('location_label', 'Unknown location')}"
            ),
            "dispatch": dispatch,
            "source": "authority_response_center",
        }
    )


@router.get("/dispatches")
async def list_dispatches(
    limit: int = Query(default=50, ge=1, le=200),
):
    """
    Return latest authority dispatch / incident records.

    Example:
    {
        "dispatches": [...],
        "count": 3
    }
    """

    dispatches = get_dispatches(limit=limit)

    return {
        "dispatches": dispatches,
        "count": len(dispatches),
    }


@router.get("/dispatches/summary")
async def dispatches_summary():
    """
    Return status counters for Authority Response Center.

    UI labels:
    - pending
    - assigned
    - running
    - resolved
    """

    return get_dispatch_status_counts()


@router.post("/dispatches/{dispatch_id}/assign")
async def assign_dispatch(dispatch_id: str, payload: dict | None = None):
    """
    Assign an authority unit to a pending incident.

    Request body example:
    {
        "unit_type": "POLICE",
        "unit_name": "UNIT-01 ALPHA"
    }
    """

    payload = payload or {}

    dispatch = update_dispatch_status(
        dispatch_id=dispatch_id,
        status="ASSIGNED",
        unit_name=payload.get("unit_name"),
        unit_type=payload.get("unit_type"),
        eta_minutes=payload.get("eta_minutes"),
    )

    if not dispatch:
        raise HTTPException(status_code=404, detail="Dispatch not found")

    await _broadcast_dispatch_update(dispatch)

    return {
        "success": True,
        "dispatch": dispatch,
    }


@router.post("/dispatches/{dispatch_id}/dispatch")
async def mark_dispatch_running(dispatch_id: str, payload: dict | None = None):
    """
    Mark an assigned incident as dispatched/running.

    Database status:
    - DISPATCHED

    UI label:
    - Running
    """

    payload = payload or {}

    dispatch = update_dispatch_status(
        dispatch_id=dispatch_id,
        status="DISPATCHED",
        eta_minutes=payload.get("eta_minutes"),
    )

    if not dispatch:
        raise HTTPException(status_code=404, detail="Dispatch not found")

    await _broadcast_dispatch_update(dispatch)

    return {
        "success": True,
        "dispatch": dispatch,
    }


@router.post("/dispatches/{dispatch_id}/resolve")
async def resolve_dispatch(dispatch_id: str, payload: dict | None = None):
    """
    Resolve/close an authority incident.

    Request body example:
    {
        "resolution_note": "Incident checked and resolved by authority unit."
    }
    """

    payload = payload or {}

    dispatch = update_dispatch_status(
        dispatch_id=dispatch_id,
        status="RESOLVED",
        resolution_note=payload.get(
            "resolution_note",
            "Incident checked and resolved by authority unit.",
        ),
    )

    if not dispatch:
        raise HTTPException(status_code=404, detail="Dispatch not found")

    await _broadcast_dispatch_update(dispatch)

    return {
        "success": True,
        "dispatch": dispatch,
    }