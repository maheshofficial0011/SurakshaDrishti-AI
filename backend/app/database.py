# 🟢 CHANGED: Fixed SQLite event database layer
# REASON: Previous file had migration code accidentally pasted inside SQL table creation

import sqlite3
import json
from datetime import datetime
from pathlib import Path

DB_DIR = Path("database")
DB_DIR.mkdir(exist_ok=True)

DB_PATH = DB_DIR / "surakshanet_events.db"


def get_connection():
    return sqlite3.connect(DB_PATH)


def init_db():
    connection = get_connection()
    cursor = connection.cursor()

    # 🟢 CHANGED: Correct table schema with camera metadata columns
    # REASON: Events now need camera_id, camera_name, camera_location, and event timestamp

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

    # 🟢 CHANGED: Safe migration for existing SQLite databases
    # REASON: Old database may not already have camera metadata columns

    existing_columns = [
        row[1] for row in cursor.execute("PRAGMA table_info(events)").fetchall()
    ]

    new_columns = {
        "camera_id": "TEXT",
        "camera_name": "TEXT",
        "camera_location": "TEXT",
        "event_timestamp": "TEXT",
    }

    for column_name, column_type in new_columns.items():
        if column_name not in existing_columns:
            cursor.execute(f"ALTER TABLE events ADD COLUMN {column_name} {column_type}")

    connection.commit()
    connection.close()


def save_event(event: dict):
    connection = get_connection()
    cursor = connection.cursor()

    # 🟢 CHANGED: Save camera metadata with event
    # REASON: Reports and dashboard need source camera information

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
            created_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            event.get("type", "UNKNOWN"),
            event.get("severity", "INFO"),
            event.get("message", ""),
            event.get("object_id"),
            event.get("zone"),
            event.get("class"),
            event.get("confidence"),
            json.dumps(event.get("bbox", [])),
            event.get("camera_id"),
            event.get("camera_name"),
            event.get("camera_location"),
            event.get("timestamp"),
            json.dumps(event),
            datetime.now().isoformat(),
        ),
    )

    connection.commit()
    event_id = cursor.lastrowid
    connection.close()

    return event_id


# 🟢 CHANGED: Added filterable event query
# REASON: Dashboard and analytics need filtering by type, severity, and limit


def get_events(limit: int = 100, event_type: str = None, severity: str = None):
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
            event_timestamp
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
        try:
            raw_event = json.loads(row[9])
        except Exception:
            raw_event = {}

        raw_event["db_id"] = row[0]
        raw_event["type"] = raw_event.get("type", row[1])
        raw_event["severity"] = raw_event.get("severity", row[2])
        raw_event["message"] = raw_event.get("message", row[3])
        raw_event["object_id"] = raw_event.get("object_id", row[4])
        raw_event["zone"] = raw_event.get("zone", row[5])
        raw_event["class"] = raw_event.get("class", row[6])
        raw_event["confidence"] = raw_event.get("confidence", row[7])
        raw_event["bbox"] = raw_event.get("bbox", json.loads(row[8]) if row[8] else [])
        raw_event["created_at"] = row[10]

        # 🟢 CHANGED: Return camera metadata to frontend
        # REASON: Dashboard alert cards and reports need event source info

        raw_event["camera_id"] = raw_event.get("camera_id") or row[11]
        raw_event["camera_name"] = raw_event.get("camera_name") or row[12]
        raw_event["camera_location"] = raw_event.get("camera_location") or row[13]
        raw_event["timestamp"] = raw_event.get("timestamp") or row[14] or row[10]

        events.append(raw_event)

    return events


def clear_events():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("DELETE FROM events")

    connection.commit()
    connection.close()


# 🟢 CHANGED: Added analytics summary query
# REASON: Backend should provide dashboard-ready event analytics


def get_analytics_summary():
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
        },
        "high_priority_count": high_priority,
        "high_priority_percent": high_priority_percent,
    }


# 🟢 CHANGED: Added event type analytics
# REASON: Dashboard/reporting needs event distribution


def get_events_by_type():
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


# 🟢 CHANGED: Added severity analytics
# REASON: Dashboard needs severity distribution


def get_events_by_severity():
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


# 🟢 CHANGED: Added risk zone analytics
# REASON: Identify most active/high-risk restricted zones


def get_risk_zones():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT zone, COUNT(*) as count
        FROM events
        WHERE zone IS NOT NULL
        GROUP BY zone
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


# 🟢 CHANGED: Added export-ready event query
# REASON: Reports need structured event rows for JSON/CSV export


def get_events_for_export(
    event_type: str = None,
    severity: str = None,
    limit: int = 1000,
):
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
            event_timestamp
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
                "bbox": row[8],
                "created_at": row[10],
                "camera_id": row[11],
                "camera_name": row[12],
                "camera_location": row[13],
                "event_timestamp": row[14],
            }
        )

    return export_rows


# 🟢 CHANGED: Added daily summary analytics
# REASON: Generate date-based incident reports for dashboard/export


def get_daily_summary(date: str = None):
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

    # By event type
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

    # By severity
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

    # Risk zones
    cursor.execute(
        """
        SELECT zone, COUNT(*)
        FROM events
        WHERE created_at LIKE ?
        AND zone IS NOT NULL
        GROUP BY zone
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

    # Latest incidents
    cursor.execute(
        """
        SELECT
            raw_event,
            created_at,
            camera_id,
            camera_name,
            camera_location,
            event_timestamp
        FROM events
        WHERE created_at LIKE ?
        ORDER BY id DESC
        LIMIT 10
        """,
        (date_filter,),
    )

    latest_events = []

    for row in cursor.fetchall():
        try:
            event = json.loads(row[0])
            event["created_at"] = row[1]
            event["camera_id"] = event.get("camera_id") or row[2]
            event["camera_name"] = event.get("camera_name") or row[3]
            event["camera_location"] = event.get("camera_location") or row[4]
            event["timestamp"] = event.get("timestamp") or row[5] or row[1]
            latest_events.append(event)
        except Exception:
            continue

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
