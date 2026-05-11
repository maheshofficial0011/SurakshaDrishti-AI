# 🟢 CHANGED: Events API now uses SQLite persistence + filtering
# REASON: Store alerts permanently and support dashboard history/search

from fastapi import APIRouter, Query

from backend.app.websocket_manager import broadcast_event
from backend.app.database import save_event, get_events, clear_events

router = APIRouter()


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
    # 🟢 CHANGED: Save incoming event to SQLite
    # REASON: Persistent event history

    event_id = save_event(event)

    event["db_id"] = event_id

    await broadcast_event(event)

    return {"status": "event added", "event_id": event_id}


@router.delete("/events")
async def delete_events():
    # 🟢 CHANGED: Added clear event history endpoint
    # REASON: Useful during testing/demo reset

    clear_events()

    return {"status": "events cleared"}
