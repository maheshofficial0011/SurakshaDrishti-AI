"""
SurakshaNet AI — SOS Demo API Route

Purpose:
- Simulate a mobile app SOS alert for demo.
- Create a critical SOS event.
- Save it to SQLite.
- Broadcast it to dashboard through the existing WebSocket system.
- Trigger demo authority response dispatcher.

Important:
- This does NOT create a real mobile app.
- This does NOT call police/ambulance APIs.
- This does NOT use GPS.
- It uses the configured demo laptop location.
"""

from datetime import datetime

from fastapi import APIRouter

from backend.app.database import save_event, save_dispatch
from backend.app.demo_config import enrich_event_with_demo_location
from backend.app.services.demo_dispatcher import create_dispatches_for_event
from backend.app.websocket_manager import broadcast_event

router = APIRouter()


@router.post("/sos")
async def trigger_sos(payload: dict | None = None):
    """
    Trigger a demo SOS alert.

    Request body example:
    {
        "user_name": "Demo User",
        "phone": "demo",
        "message": "Emergency SOS triggered from mobile app demo"
    }

    Returns:
        Created SOS event and dispatch records.
    """

    payload = payload or {}

    user_name = payload.get("user_name", "Demo User")
    phone = payload.get("phone", "demo")
    message = payload.get(
        "message",
        "Emergency SOS triggered from mobile app demo",
    )

    sos_event = {
        "type": "SOS_ALERT",
        "severity": "CRITICAL",
        "message": f"SOS alert from {user_name}: {message}",
        "source": "mobile_app",
        "user_name": user_name,
        "phone": phone,
        "timestamp": datetime.now().isoformat(),
        "class": "sos",
        "class_name": "sos",
        "object_label": "mobile_sos",
        "object_confidence": 1.0,
        "confidence": 1.0,
        "camera_id": "MOBILE-SOS",
        "camera_name": "Mobile SOS Demo",
        "camera_location": "Demo Mobile App",
    }

    sos_event = enrich_event_with_demo_location(sos_event)

    event_id = save_event(sos_event)
    sos_event["db_id"] = event_id

    await broadcast_event(sos_event)

    dispatches = create_dispatches_for_event(sos_event, event_id=event_id)

    for dispatch in dispatches:
        dispatch_db_id = save_dispatch(dispatch)
        dispatch["id"] = dispatch_db_id

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

    return {
        "success": True,
        "event": sos_event,
        "dispatches": dispatches,
    }