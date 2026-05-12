# 🟢 CHANGED: Events API now uses SQLite persistence + filtering
# REASON: Store alerts permanently and support dashboard history/search

from fastapi import APIRouter, Query

from backend.app.websocket_manager import broadcast_event
from backend.app.database import (
    save_event,
    get_events,
    clear_events,
    save_dispatch,
)
from backend.app.demo_config import enrich_event_with_demo_location
from backend.app.services.demo_dispatcher import create_dispatches_for_event

router = APIRouter()


def _should_create_dispatch(event: dict):
    """
    Decide whether an event should create authority response dispatch.

    This is intentionally conservative:
    - HIGH and CRITICAL alerts create dispatch.
    - SOS_ALERT always creates dispatch.
    - Normal/low/info events do not create dispatch.
    """

    event_type = (event.get("type") or "").upper()
    severity = (event.get("severity") or "").upper()

    return event_type == "SOS_ALERT" or severity in ["HIGH", "CRITICAL"]


async def _save_broadcast_and_dispatch(event: dict):
    """
    Shared safe event flow.

    Existing behavior preserved:
    - save event to SQLite
    - attach db_id
    - broadcast event over WebSocket

    New additive behavior:
    - enrich event with demo laptop location
    - create dispatch records for high-priority events
    - broadcast dispatch update as a normal WebSocket message

    Returns:
        tuple: (event, dispatches)
    """

    event = enrich_event_with_demo_location(event)

    event_id = save_event(event)
    event["db_id"] = event_id

    # Existing WebSocket behavior is preserved:
    # frontend still receives normal event objects.
    await broadcast_event(event)

    dispatches = []

    if _should_create_dispatch(event):
        dispatches = create_dispatches_for_event(event, event_id=event_id)

        for dispatch in dispatches:
            dispatch_db_id = save_dispatch(dispatch)
            dispatch["id"] = dispatch_db_id

            # Broadcast dispatch as event-like payload to avoid changing
            # existing websocket manager format.
            await broadcast_event(
                {
                    "type": "DISPATCH_UPDATE",
                    "severity": "INFO",
                    "message": (
                        f"{dispatch['unit_name']} dispatched to "
                        f"{dispatch['location_label']} "
                        f"(ETA {dispatch['eta_minutes']} min)"
                    ),
                    "dispatch": dispatch,
                    "source": "authority_dispatcher",
                }
            )

    return event, dispatches


@router.get("/events")
async def list_events(
    type: str | None = Query(default=None),
    severity: str | None = Query(default=None),
    limit: int = Query(default=100, ge=1, le=500),
):
    # 🟢 CHANGED: Added database filters
    # REASON: Dashboard can request specific event history

    events = get_events(
        limit=limit,
        event_type=type,
        severity=severity,
    )

    return {
        "events": events,
        "filters": {
            "type": type,
            "severity": severity,
            "limit": limit,
        },
        "count": len(events),
    }


@router.post("/events")
async def add_event(event: dict):
    """
    Add one event to the system.

    Compatible with existing pipeline:
    - Pipeline still posts event JSON to /events.
    - Backend still saves and broadcasts it.
    - Extra dispatch behavior only happens for high-priority events.
    """

    event, dispatches = await _save_broadcast_and_dispatch(event)

    return {
        "status": "event added",
        "event_id": event["db_id"],
        "event": event,
        "dispatches": dispatches,
    }


@router.delete("/events")
async def delete_events():
    # 🟢 CHANGED: Added clear event history endpoint
    # REASON: Useful during testing/demo reset

    clear_events()

    return {"status": "events cleared"}


# 🟢 CHANGED: Added manual demo/test alert endpoint
# REASON: Helps verify dashboard, websocket, database, and alert flow without camera movement


@router.post("/events/test")
async def create_test_event():
    test_event = {
        "type": "INTRUSION",
        "severity": "HIGH",
        "message": "Manual test intrusion alert generated from backend",
        "object_id": 999,
        "zone": "Demo Zone",
        "camera_id": "CAM-TEST",
        "camera_name": "Demo Test Camera",
        "camera_location": "Demo Area",
        "class": "person",
        "class_name": "person",
        "object_label": "person",
        "object_confidence": 0.95,
        "source": "manual_test",
    }

    event, dispatches = await _save_broadcast_and_dispatch(test_event)

    return {
        "status": "test event generated",
        "event": event,
        "dispatches": dispatches,
    }