"""
SurakshaNet AI — SQLite Database Layer

Purpose:
- Store surveillance events permanently in SQLite.
- Support dashboard event history.
- Support analytics and report exports.
- Support demo heatmap data.
- Support mobile SOS demo events.
- Support authority response dispatch records.

Safety Rules:
- Do NOT delete existing tables.
- Do NOT recreate existing tables.
- Do NOT change existing public function names.
- Do NOT break old dashboard/event/report behavior.
- Use CREATE TABLE IF NOT EXISTS for new tables.
- Use ALTER TABLE only when a column is missing.

This file is intentionally self-contained and conservative because it is used by:
- backend startup
- /events route
- /analytics route
- /reports route
- future /sos route
- future /dispatches route
"""

import json
import sqlite3
from datetime import datetime
from pathlib import Path

from backend.app.demo_config import get_demo_location

# ---------------------------------------------------------------------
# Database path
# ---------------------------------------------------------------------

DB_DIR = Path("database")
DB_DIR.mkdir(exist_ok=True)

DB_PATH = DB_DIR / "surakshanet_events.db"


# ---------------------------------------------------------------------
# Connection helpers
# ---------------------------------------------------------------------


def get_connection():
    """
    Return a SQLite connection.

    Keep this simple so existing backend routes can continue using it safely.
    """

    return sqlite3.connect(DB_PATH)


def _safe_json_loads(value, fallback):
    """
    Safely parse JSON from database text.

    Args:
        value: JSON string from SQLite.
        fallback: value to return if parsing fails.

    Returns:
        Parsed JSON object or fallback.
    """

    try:
        if value is None:
            return fallback

        return json.loads(value)

    except Exception:
        return fallback


def _get_existing_columns(cursor, table_name: str):
    """
    Return existing column names for a SQLite table.

    Used for safe migration.
    """

    rows = cursor.execute(f"PRAGMA table_info({table_name})").fetchall()

    return {row[1] for row in rows}


def _add_missing_columns(cursor, table_name: str, columns: dict):
    """
    Add missing columns to an existing SQLite table.

    This is safer than recreating the table.

    Args:
        cursor: SQLite cursor.
        table_name: target table name.
        columns: dict like {"column_name": "SQL_TYPE"}
    """

    existing_columns = _get_existing_columns(cursor, table_name)

    for column_name, column_type in columns.items():
        if column_name not in existing_columns:
            cursor.execute(
                f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_type}"
            )


# ---------------------------------------------------------------------
# Database initialization
# ---------------------------------------------------------------------


def init_db():
    """
    Initialize SQLite database and run safe migrations.

    Existing behavior preserved:
    - events table remains the main event table.
    - old camera metadata fields remain supported.

    New additions:
    - location_lat
    - location_lng
    - location_label
    - source
    - dispatches table
    """

    connection = get_connection()
    cursor = connection.cursor()

    # -----------------------------------------------------------------
    # Main events table
    # -----------------------------------------------------------------
    # This preserves the original schema and keeps old data compatible.
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            type TEXT NOT NULL,
            severity TEXT,
            message TEXT,
            object_id INTEGER,
            zone TEXT,
            class_name TEXT,
            confidence REAL,
            bbox TEXT,
            camera_id TEXT,
            camera_name TEXT,
            camera_location TEXT,
            event_timestamp TEXT,
            raw_event TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
        """)

    # -----------------------------------------------------------------
    # Safe event table migration
    # -----------------------------------------------------------------
    # These fields are added only if they do not already exist.
    _add_missing_columns(
        cursor,
        "events",
        {
            # Existing metadata columns, kept here for older DB compatibility.
            "camera_id": "TEXT",
            "camera_name": "TEXT",
            "camera_location": "TEXT",
            "event_timestamp": "TEXT",
            # Demo Feature Completion V1 columns.
            "location_lat": "REAL",
            "location_lng": "REAL",
            "location_label": "TEXT",
            "source": "TEXT",
        },
    )

    # -----------------------------------------------------------------
    # Authority dispatch table
    # -----------------------------------------------------------------
    # New table for demo authority response panel.
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS dispatches (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            dispatch_id TEXT NOT NULL,
            event_id INTEGER,
            event_type TEXT,
            unit_type TEXT,
            unit_name TEXT,
            status TEXT,
            eta_minutes INTEGER,
            location_label TEXT,
            created_at TEXT NOT NULL
        )
        """)

    connection.commit()
    connection.close()


# ---------------------------------------------------------------------
# Event storage
# ---------------------------------------------------------------------


def save_event(event: dict):
    """
    Save one event to SQLite.

    This function remains compatible with existing event objects.

    Existing fields supported:
    - type
    - severity
    - message
    - object_id
    - zone
    - class
    - confidence
    - bbox
    - camera_id
    - camera_name
    - camera_location
    - timestamp
    - snapshot_url / snapshot_file
    - clip_url / clip_file

    New fields supported:
    - object_label
    - object_confidence
    - location_lat
    - location_lng
    - location_label
    - location
    - source

    Args:
        event: event dictionary

    Returns:
        int: inserted database row id
    """

    if event is None:
        event = {}

    connection = get_connection()
    cursor = connection.cursor()

    demo_location = get_demo_location()

    # -----------------------------------------------------------------
    # Location enrichment
    # -----------------------------------------------------------------
    # If the event already has location, keep it.
    # If missing, attach demo laptop location.
    location_lat = event.get("location_lat")
    location_lng = event.get("location_lng")
    location_label = event.get("location_label")

    if location_lat is None:
        location_lat = demo_location["lat"]

    if location_lng is None:
        location_lng = demo_location["lng"]

    if not location_label:
        location_label = demo_location["label"]

    event.setdefault("location_lat", location_lat)
    event.setdefault("location_lng", location_lng)
    event.setdefault("location_label", location_label)

    event.setdefault(
        "location",
        {
            "lat": location_lat,
            "lng": location_lng,
            "label": location_label,
        },
    )

    # -----------------------------------------------------------------
    # Object/class compatibility
    # -----------------------------------------------------------------
    # Old dashboard already understands `class`.
    # New UI can use `object_label`.
    class_name = (
        event.get("class") or event.get("class_name") or event.get("object_label")
    )

    confidence = (
        event.get("confidence")
        if event.get("confidence") is not None
        else event.get("object_confidence")
    )

    if class_name:
        event.setdefault("class", class_name)
        event.setdefault("class_name", class_name)
        event.setdefault("object_label", class_name)

    if confidence is not None:
        event.setdefault("confidence", confidence)
        event.setdefault("object_confidence", confidence)

    event.setdefault("source", "camera_ai")

    cursor.execute(
        """
        INSERT INTO events (
            type,
            severity,
            message,
            object_id,
            zone,
            class_name,
            confidence,
            bbox,
            camera_id,
            camera_name,
            camera_location,
            event_timestamp,
            raw_event,
            created_at,
            location_lat,
            location_lng,
            location_label,
            source
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            event.get("type", "UNKNOWN"),
            event.get("severity", "INFO"),
            event.get("message", ""),
            event.get("object_id"),
            event.get("zone"),
            class_name,
            confidence,
            json.dumps(event.get("bbox", [])),
            event.get("camera_id"),
            event.get("camera_name"),
            event.get("camera_location"),
            event.get("timestamp"),
            json.dumps(event),
            datetime.now().isoformat(),
            location_lat,
            location_lng,
            location_label,
            event.get("source", "camera_ai"),
        ),
    )

    connection.commit()

    event_id = cursor.lastrowid

    connection.close()

    return event_id


def get_events(limit: int = 100, event_type: str = None, severity: str = None):
    """
    Return event history for dashboard.

    Existing response shape is preserved.
    New fields are added safely.

    Args:
        limit: maximum number of events
        event_type: optional type filter
        severity: optional severity filter

    Returns:
        list[dict]: event dictionaries
    """

    connection = get_connection()
    cursor = connection.cursor()

    query = """
        SELECT
            id,
            type,
            severity,
            message,
            object_id,
            zone,
            class_name,
            confidence,
            bbox,
            raw_event,
            created_at,
            camera_id,
            camera_name,
            camera_location,
            event_timestamp,
            location_lat,
            location_lng,
            location_label,
            source
        FROM events
        WHERE 1 = 1
    """

    params = []

    if event_type:
        query += " AND type = ?"
        params.append(event_type)

    if severity:
        query += " AND severity = ?"
        params.append(severity)

    query += " ORDER BY id DESC LIMIT ?"
    params.append(limit)

    cursor.execute(query, params)

    rows = cursor.fetchall()

    connection.close()

    events = []

    for row in rows:
        raw_event = _safe_json_loads(row[9], {})

        # Core event fields
        raw_event["db_id"] = row[0]
        raw_event["type"] = raw_event.get("type", row[1])
        raw_event["severity"] = raw_event.get("severity", row[2])
        raw_event["message"] = raw_event.get("message", row[3])
        raw_event["object_id"] = raw_event.get("object_id", row[4])
        raw_event["zone"] = raw_event.get("zone", row[5])

        # Class/object fields
        raw_event["class"] = (
            raw_event.get("class")
            or raw_event.get("class_name")
            or raw_event.get("object_label")
            or row[6]
        )

        raw_event["class_name"] = raw_event.get("class_name") or raw_event.get("class")

        raw_event["confidence"] = (
            raw_event.get("confidence")
            if raw_event.get("confidence") is not None
            else row[7]
        )

        raw_event["object_label"] = (
            raw_event.get("object_label")
            or raw_event.get("class")
            or raw_event.get("class_name")
        )

        raw_event["object_confidence"] = (
            raw_event.get("object_confidence")
            if raw_event.get("object_confidence") is not None
            else raw_event.get("confidence")
        )

        # BBox and timestamps
        raw_event["bbox"] = raw_event.get(
            "bbox",
            _safe_json_loads(row[8], []),
        )

        raw_event["created_at"] = row[10]

        # Camera metadata
        raw_event["camera_id"] = raw_event.get("camera_id") or row[11]
        raw_event["camera_name"] = raw_event.get("camera_name") or row[12]
        raw_event["camera_location"] = raw_event.get("camera_location") or row[13]
        raw_event["timestamp"] = raw_event.get("timestamp") or row[14] or row[10]

        # Location metadata
        raw_event["location_lat"] = raw_event.get("location_lat") or row[15]
        raw_event["location_lng"] = raw_event.get("location_lng") or row[16]
        raw_event["location_label"] = raw_event.get("location_label") or row[17]
        raw_event["source"] = raw_event.get("source") or row[18] or "camera_ai"

        if not raw_event.get("location"):
            raw_event["location"] = {
                "lat": raw_event["location_lat"],
                "lng": raw_event["location_lng"],
                "label": raw_event["location_label"],
            }

        events.append(raw_event)

    return events


def clear_events():
    """
    Clear event history.

    Existing behavior preserved:
    - Only clears events.
    - Does not clear dispatches.
    """

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("DELETE FROM events")

    connection.commit()
    connection.close()


# ---------------------------------------------------------------------
# Analytics
# ---------------------------------------------------------------------


def get_analytics_summary():
    """
    Return dashboard-ready analytics summary.
    """

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("SELECT COUNT(*) FROM events")
    total_events = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM events WHERE severity = 'CRITICAL'")
    critical_count = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM events WHERE severity = 'HIGH'")
    high_count = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM events WHERE severity = 'MEDIUM'")
    medium_count = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM events WHERE severity = 'LOW'")
    low_count = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM events WHERE type = 'INTRUSION'")
    intrusion_count = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM events WHERE type = 'LOITERING'")
    loitering_count = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM events WHERE type = 'CROWD_ALERT'")
    crowd_count = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM events WHERE type = 'WEAPON_DETECTED'")
    weapon_count = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM events WHERE type = 'PPE_VIOLATION'")
    ppe_count = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM events WHERE type = 'SOS_ALERT'")
    sos_count = cursor.fetchone()[0]

    connection.close()

    high_priority = critical_count + high_count

    high_priority_percent = 0

    if total_events > 0:
        high_priority_percent = round((high_priority / total_events) * 100)

    return {
        "total_events": total_events,
        "severity": {
            "critical": critical_count,
            "high": high_count,
            "medium": medium_count,
            "low": low_count,
        },
        "events": {
            "intrusion": intrusion_count,
            "loitering": loitering_count,
            "crowd": crowd_count,
            "weapon": weapon_count,
            "ppe": ppe_count,
            "sos": sos_count,
        },
        "high_priority_count": high_priority,
        "high_priority_percent": high_priority_percent,
    }


def get_events_by_type():
    """
    Return event count grouped by type.
    """

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT type, COUNT(*) as count
        FROM events
        GROUP BY type
        ORDER BY count DESC
        """)

    rows = cursor.fetchall()

    connection.close()

    return [
        {
            "type": row[0],
            "count": row[1],
        }
        for row in rows
    ]


def get_events_by_severity():
    """
    Return event count grouped by severity.
    """

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT severity, COUNT(*) as count
        FROM events
        GROUP BY severity
        ORDER BY count DESC
        """)

    rows = cursor.fetchall()

    connection.close()

    return [
        {
            "severity": row[0] or "INFO",
            "count": row[1],
        }
        for row in rows
    ]


def get_risk_zones():
    """
    Return most active zones.

    If the rule zone is missing, fall back to location_label.
    """

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            COALESCE(zone, location_label, 'Unknown Zone') as zone_name,
            COUNT(*) as count
        FROM events
        WHERE zone IS NOT NULL OR location_label IS NOT NULL
        GROUP BY zone_name
        ORDER BY count DESC
        """)

    rows = cursor.fetchall()

    connection.close()

    return [
        {
            "zone": row[0],
            "count": row[1],
        }
        for row in rows
    ]


# ---------------------------------------------------------------------
# Report/export helpers
# ---------------------------------------------------------------------


def get_events_for_export(
    event_type: str = None,
    severity: str = None,
    limit: int = 1000,
):
    """
    Return export-ready event rows.

    Existing report fields are preserved.
    New fields are included safely.
    """

    connection = get_connection()
    cursor = connection.cursor()

    query = """
        SELECT
            id,
            type,
            severity,
            message,
            object_id,
            zone,
            class_name,
            confidence,
            bbox,
            raw_event,
            created_at,
            camera_id,
            camera_name,
            camera_location,
            event_timestamp,
            location_lat,
            location_lng,
            location_label,
            source
        FROM events
        WHERE 1 = 1
    """

    params = []

    if event_type:
        query += " AND type = ?"
        params.append(event_type)

    if severity:
        query += " AND severity = ?"
        params.append(severity)

    query += " ORDER BY id DESC LIMIT ?"
    params.append(limit)

    cursor.execute(query, params)

    rows = cursor.fetchall()

    connection.close()

    export_rows = []

    for row in rows:
        raw_event = _safe_json_loads(row[9], {})

        export_rows.append(
            {
                "id": row[0],
                "type": row[1],
                "severity": row[2],
                "message": row[3],
                "object_id": row[4],
                "zone": row[5],
                "class_name": row[6],
                "confidence": row[7],
                "object_label": (
                    raw_event.get("object_label") or raw_event.get("class") or row[6]
                ),
                "object_confidence": (
                    raw_event.get("object_confidence")
                    or raw_event.get("confidence")
                    or row[7]
                ),
                "bbox": row[8],
                "camera_id": row[11],
                "camera_name": row[12],
                "camera_location": row[13],
                "event_timestamp": row[14],
                "location_lat": row[15],
                "location_lng": row[16],
                "location_label": row[17],
                "source": row[18],
                "created_at": row[10],
                "snapshot_url": raw_event.get("snapshot_url", ""),
                "snapshot_file": raw_event.get("snapshot_file", ""),
                "clip_url": raw_event.get("clip_url", ""),
                "clip_file": raw_event.get("clip_file", ""),
            }
        )

    return export_rows


def get_daily_summary(date: str = None):
    """
    Return daily incident summary.

    Args:
        date: optional YYYY-MM-DD string

    Returns:
        dict summary for reports/dashboard
    """

    connection = get_connection()
    cursor = connection.cursor()

    if date:
        date_filter = f"{date}%"
    else:
        date_filter = datetime.now().strftime("%Y-%m-%d") + "%"

    # Total events
    cursor.execute(
        """
        SELECT COUNT(*)
        FROM events
        WHERE created_at LIKE ?
        """,
        (date_filter,),
    )

    total_events = cursor.fetchone()[0]

    # Event type distribution
    cursor.execute(
        """
        SELECT type, COUNT(*)
        FROM events
        WHERE created_at LIKE ?
        GROUP BY type
        ORDER BY COUNT(*) DESC
        """,
        (date_filter,),
    )

    by_type = [
        {
            "type": row[0],
            "count": row[1],
        }
        for row in cursor.fetchall()
    ]

    # Severity distribution
    cursor.execute(
        """
        SELECT severity, COUNT(*)
        FROM events
        WHERE created_at LIKE ?
        GROUP BY severity
        ORDER BY COUNT(*) DESC
        """,
        (date_filter,),
    )

    by_severity = [
        {
            "severity": row[0] or "INFO",
            "count": row[1],
        }
        for row in cursor.fetchall()
    ]

    # Risk zone distribution
    cursor.execute(
        """
        SELECT
            COALESCE(zone, location_label, 'Unknown Zone') as zone_name,
            COUNT(*)
        FROM events
        WHERE created_at LIKE ?
        AND (zone IS NOT NULL OR location_label IS NOT NULL)
        GROUP BY zone_name
        ORDER BY COUNT(*) DESC
        """,
        (date_filter,),
    )

    risk_zones = [
        {
            "zone": row[0],
            "count": row[1],
        }
        for row in cursor.fetchall()
    ]

    # Latest events
    cursor.execute(
        """
        SELECT
            raw_event,
            created_at,
            camera_id,
            camera_name,
            camera_location,
            event_timestamp,
            location_lat,
            location_lng,
            location_label,
            source
        FROM events
        WHERE created_at LIKE ?
        ORDER BY id DESC
        LIMIT 10
        """,
        (date_filter,),
    )

    latest_events = []

    for row in cursor.fetchall():
        event = _safe_json_loads(row[0], {})

        if not event:
            continue

        event["created_at"] = row[1]
        event["camera_id"] = event.get("camera_id") or row[2]
        event["camera_name"] = event.get("camera_name") or row[3]
        event["camera_location"] = event.get("camera_location") or row[4]
        event["timestamp"] = event.get("timestamp") or row[5] or row[1]

        event["location_lat"] = event.get("location_lat") or row[6]
        event["location_lng"] = event.get("location_lng") or row[7]
        event["location_label"] = event.get("location_label") or row[8]
        event["source"] = event.get("source") or row[9] or "camera_ai"

        if not event.get("location"):
            event["location"] = {
                "lat": event["location_lat"],
                "lng": event["location_lng"],
                "label": event["location_label"],
            }

        latest_events.append(event)

    connection.close()

    high_priority_count = 0

    for item in by_severity:
        if item["severity"] in ["CRITICAL", "HIGH"]:
            high_priority_count += item["count"]

    high_priority_percent = 0

    if total_events > 0:
        high_priority_percent = round((high_priority_count / total_events) * 100)

    return {
        "date": date_filter.replace("%", ""),
        "total_events": total_events,
        "high_priority_count": high_priority_count,
        "high_priority_percent": high_priority_percent,
        "by_type": by_type,
        "by_severity": by_severity,
        "risk_zones": risk_zones,
        "latest_events": latest_events,
    }


# ---------------------------------------------------------------------
# Heatmap support
# ---------------------------------------------------------------------


def get_heatmap_data():
    """
    Return heatmap-ready data for dashboard.

    Designed for Leaflet/react-leaflet frontend.

    The location is based on the configured demo laptop location unless events
    already contain explicit location fields.

    Returns:
        dict:
        {
            "location": {...},
            "event_count": int,
            "latest_event_type": str,
            "risk_level": str,
            "risk_score": int,
            "heat_points": [...]
        }
    """

    connection = get_connection()
    cursor = connection.cursor()

    demo_location = get_demo_location()

    cursor.execute("SELECT COUNT(*) FROM events")
    total_events = cursor.fetchone()[0]

    cursor.execute("""
        SELECT type
        FROM events
        ORDER BY id DESC
        LIMIT 1
        """)

    latest_row = cursor.fetchone()
    latest_event_type = latest_row[0] if latest_row else "NONE"

    if total_events >= 15:
        risk_level = "CRITICAL"
        risk_score = 95
    elif total_events >= 8:
        risk_level = "HIGH"
        risk_score = 75
    elif total_events >= 3:
        risk_level = "MEDIUM"
        risk_score = 45
    elif total_events >= 1:
        risk_level = "LOW"
        risk_score = 20
    else:
        risk_level = "NORMAL"
        risk_score = 5

    cursor.execute(
        """
        SELECT
            COALESCE(location_lat, ?),
            COALESCE(location_lng, ?),
            COALESCE(location_label, ?),
            COUNT(*) as event_count,
            MAX(type) as latest_type
        FROM events
        GROUP BY
            COALESCE(location_lat, ?),
            COALESCE(location_lng, ?),
            COALESCE(location_label, ?)
        ORDER BY event_count DESC
        """,
        (
            demo_location["lat"],
            demo_location["lng"],
            demo_location["label"],
            demo_location["lat"],
            demo_location["lng"],
            demo_location["label"],
        ),
    )

    rows = cursor.fetchall()

    connection.close()

    heat_points = []

    if rows:
        for row in rows:
            heat_points.append(
                {
                    "lat": row[0],
                    "lng": row[1],
                    "label": row[2],
                    "weight": row[3],
                    "event_count": row[3],
                    "latest_event_type": row[4],
                }
            )
    else:
        heat_points.append(
            {
                "lat": demo_location["lat"],
                "lng": demo_location["lng"],
                "label": demo_location["label"],
                "weight": 0,
                "event_count": 0,
                "latest_event_type": "NONE",
            }
        )

    return {
        "location": demo_location,
        "event_count": total_events,
        "latest_event_type": latest_event_type,
        "risk_level": risk_level,
        "risk_score": risk_score,
        "heat_points": heat_points,
    }


# ---------------------------------------------------------------------
# Dispatch support
# ---------------------------------------------------------------------


def save_dispatch(dispatch: dict):
    """
    Save one authority dispatch record.

    Args:
        dispatch: dispatch dictionary

    Returns:
        int: inserted dispatch database row id
    """

    if dispatch is None:
        dispatch = {}

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        INSERT INTO dispatches (
            dispatch_id,
            event_id,
            event_type,
            unit_type,
            unit_name,
            status,
            eta_minutes,
            location_label,
            created_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            dispatch.get("dispatch_id"),
            dispatch.get("event_id"),
            dispatch.get("event_type"),
            dispatch.get("unit_type"),
            dispatch.get("unit_name"),
            dispatch.get("status", "DISPATCHED"),
            dispatch.get("eta_minutes", 3),
            dispatch.get("location_label"),
            dispatch.get("created_at") or datetime.now().isoformat(),
        ),
    )

    connection.commit()

    dispatch_db_id = cursor.lastrowid

    connection.close()

    return dispatch_db_id


def get_dispatches(limit: int = 50):
    """
    Return latest authority dispatch records.
    """

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT
            id,
            dispatch_id,
            event_id,
            event_type,
            unit_type,
            unit_name,
            status,
            eta_minutes,
            location_label,
            created_at
        FROM dispatches
        ORDER BY id DESC
        LIMIT ?
        """,
        (limit,),
    )

    rows = cursor.fetchall()

    connection.close()

    return [
        {
            "id": row[0],
            "dispatch_id": row[1],
            "event_id": row[2],
            "event_type": row[3],
            "unit_type": row[4],
            "unit_name": row[5],
            "status": row[6],
            "eta_minutes": row[7],
            "location_label": row[8],
            "created_at": row[9],
        }
        for row in rows
    ]
