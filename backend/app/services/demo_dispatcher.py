"""
SurakshaNet AI — Demo Authority Dispatcher Service

Purpose:
- Create realistic authority response records for dashboard demo.
- Keep this separate from the existing alert_system.dispatcher module.
- Avoid changing Event Engine, tracking, detection, or pipeline behavior.

This is a demo-safe dispatcher:
- No real police/ambulance/fire API calls.
- No external network calls.
- No background jobs.
- Only creates local dispatch records saved in SQLite.

Used by:
- POST /sos
- POST /events for critical/high priority events
"""

from datetime import datetime
from backend.app.demo_config import get_demo_location


def _build_dispatch_id(event_id=None):
    """
    Create a readable demo dispatch id.

    Example:
    DSP-0001
    DSP-0042
    """

    if event_id is None:
        return f"DSP-{int(datetime.now().timestamp())}"

    try:
        return f"DSP-{int(event_id):04d}"
    except Exception:
        return f"DSP-{int(datetime.now().timestamp())}"


def _select_units_for_event(event: dict):
    """
    Pick authority units based on event type.

    This is intentionally simple and deterministic for demo reliability.
    """

    event_type = (event.get("type") or "").upper()
    severity = (event.get("severity") or "").upper()

    if event_type == "SOS_ALERT":
        return [
            {
                "unit_type": "POLICE",
                "unit_name": "UNIT-01 ALPHA",
                "eta_minutes": 3,
            },
            {
                "unit_type": "AMBULANCE",
                "unit_name": "AMBULANCE-01",
                "eta_minutes": 5,
            },
        ]

    if event_type == "WEAPON_DETECTED":
        return [
            {
                "unit_type": "POLICE",
                "unit_name": "UNIT-01 ALPHA",
                "eta_minutes": 3,
            }
        ]

    if event_type in ["INTRUSION", "CROWD_ALERT"] or severity in ["CRITICAL", "HIGH"]:
        return [
            {
                "unit_type": "POLICE",
                "unit_name": "UNIT-01 ALPHA",
                "eta_minutes": 4,
            }
        ]

    return []


def create_dispatches_for_event(event: dict, event_id=None):
    """
    Create demo dispatch objects for an event.

    Args:
        event:
            Event dictionary saved/broadcast by backend.
        event_id:
            SQLite event row id.

    Returns:
        list[dict]: dispatch records ready to save and broadcast.
    """

    if not event:
        return []

    units = _select_units_for_event(event)

    if not units:
        return []

    location = event.get("location") or get_demo_location()
    location_label = (
        event.get("location_label")
        or event.get("camera_location")
        or location.get("label")
        or "Demo Laptop Location"
    )

    created_at = datetime.now().isoformat()
    dispatches = []

    for index, unit in enumerate(units, start=1):
        base_dispatch_id = _build_dispatch_id(event_id)

        dispatch = {
            "dispatch_id": (
                base_dispatch_id
                if len(units) == 1
                else f"{base_dispatch_id}-{index}"
            ),
            "event_id": event_id,
            "event_type": event.get("type", "UNKNOWN"),
            "unit_type": unit["unit_type"],
            "unit_name": unit["unit_name"],
            "status": "DISPATCHED",
            "eta_minutes": unit["eta_minutes"],
            "location_label": location_label,
            "created_at": created_at,
        }

        dispatches.append(dispatch)

    return dispatches
