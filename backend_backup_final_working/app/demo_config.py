"""
SurakshaDrishti AI — Demo Configuration

Purpose:
- Keep demo-only location settings centralized.
- Used by:
  1. Laptop-location heatmap
  2. Mobile SOS demo
  3. Authority response dispatcher
  4. Event location enrichment

Important:
- This file does NOT use GPS.
- This file does NOT call external APIs.
- This file is safe for local laptop demo.
- Values can be changed from environment variables later.
"""

import os


def get_demo_location():
    """
    Return the configured demo/laptop location.

    Default values are demo-safe.
    You can override them using environment variables:

    DEMO_LAT
    DEMO_LNG
    DEMO_LOCATION_LABEL

    Returns:
        dict:
        {
            "lat": float,
            "lng": float,
            "label": str
        }
    """

    lat = float(os.getenv("DEMO_LAT", "11.1085"))
    lng = float(os.getenv("DEMO_LNG", "77.3411"))
    label = os.getenv("DEMO_LOCATION_LABEL", "Demo Laptop Location")

    return {
        "lat": lat,
        "lng": lng,
        "label": label,
    }


def enrich_event_with_demo_location(event: dict):
    """
    Add demo location fields to an event without breaking old fields.

    This function is additive:
    - It does not remove existing event fields.
    - It does not overwrite location fields if already present.
    - It keeps old dashboard/event contracts safe.

    Args:
        event: event dictionary

    Returns:
        dict: event with location_lat, location_lng, location_label, location
    """

    if event is None:
        event = {}

    location = get_demo_location()

    event.setdefault("location_lat", location["lat"])
    event.setdefault("location_lng", location["lng"])
    event.setdefault("location_label", location["label"])

    event.setdefault(
        "location",
        {
            "lat": location["lat"],
            "lng": location["lng"],
            "label": location["label"],
        },
    )

    return event
