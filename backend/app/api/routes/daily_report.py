import json
import sqlite3
from pathlib import Path
from datetime import datetime, date

from fastapi import APIRouter, Query
from fastapi.responses import StreamingResponse


router = APIRouter()


def project_root() -> Path:
    return Path(__file__).resolve().parents[4]


def find_db() -> Path:
    root = project_root()

    candidates = [
        root / "database" / "surakshanet_events.db",
        root / "database" / "surakshadrishti_events.db",
        root / "data" / "surakshanet_events.db",
        root / "backend" / "app" / "database.db",
    ]

    for path in candidates:
        if path.exists():
            return path

    raise FileNotFoundError("SQLite database not found")


def get_table_and_columns(conn):
    cur = conn.cursor()

    tables = [
        row[0]
        for row in cur.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        ).fetchall()
        if row[0] != "sqlite_sequence"
    ]

    preferred_tables = [
        "events",
        "alerts",
        "incidents",
        "event_logs",
        "sos_reports",
        "dispatches",
    ]

    for table in preferred_tables + tables:
        if table not in tables:
            continue

        columns = [
            col[1]
            for col in cur.execute(f"PRAGMA table_info({table})").fetchall()
        ]

        if columns:
            return table, columns

    return None, []


def safe_value(value):
    if value is None:
        return None

    if isinstance(value, bytes):
        return value.decode("utf-8", errors="ignore")

    return value


def fetch_events(limit: int):
    db_path = find_db()

    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row

    try:
        table, columns = get_table_and_columns(conn)

        if not table:
            return {
                "status": "NO_TABLE",
                "table": None,
                "columns": [],
                "events": [],
            }

        order_column = None
        for candidate in ["created_at", "timestamp", "event_time", "id"]:
            if candidate in columns:
                order_column = candidate
                break

        query = f"SELECT * FROM {table}"

        if order_column:
            query += f" ORDER BY {order_column} DESC"

        query += " LIMIT ?"

        rows = conn.execute(query, (limit,)).fetchall()

        events = []
        for row in rows:
            events.append({col: safe_value(row[col]) for col in columns})

        return {
            "status": "OK",
            "table": table,
            "columns": columns,
            "events": events,
        }

    finally:
        conn.close()


def build_daily_report(limit: int):
    result = fetch_events(limit=limit)

    today = date.today().isoformat()
    events = result.get("events", [])

    today_events = []
    type_counts = {}
    severity_counts = {}

    for event in events:
        event_text = str(event)

        if today in event_text:
            today_events.append(event)

        event_type = (
            event.get("type")
            or event.get("event_type")
            or event.get("alert_type")
            or event.get("class_name")
            or "UNKNOWN"
        )

        severity = (
            event.get("severity")
            or event.get("level")
            or event.get("priority")
            or "UNKNOWN"
        )

        type_counts[event_type] = type_counts.get(event_type, 0) + 1
        severity_counts[severity] = severity_counts.get(severity, 0) + 1

    return {
        "status": result.get("status", "OK"),
        "project": "SurakshaDrishti AI",
        "report_type": "daily_report",
        "date": today,
        "table": result.get("table"),
        "limit": limit,
        "total_events_scanned": len(events),
        "today_events_detected": len(today_events),
        "type_counts": type_counts,
        "severity_counts": severity_counts,
        "events": today_events if today_events else events,
        "generated_at": datetime.now().isoformat(),
    }


def daily_download_response(limit: int):
    payload = build_daily_report(limit=limit)

    json_text = json.dumps(
        payload,
        indent=2,
        ensure_ascii=False,
        default=str,
    )

    filename = f"surakshadrishti_daily_report_{date.today().isoformat()}.json"

    return StreamingResponse(
        iter([json_text]),
        media_type="application/octet-stream",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
            "Cache-Control": "no-store",
        },
    )


@router.get("/reports/daily")
def reports_daily(limit: int = Query(default=100, ge=1, le=5000)):
    return daily_download_response(limit=limit)


@router.get("/reports/events/daily")
def reports_events_daily(limit: int = Query(default=100, ge=1, le=5000)):
    return daily_download_response(limit=limit)


@router.get("/reports/daily/json")
def reports_daily_json(limit: int = Query(default=100, ge=1, le=5000)):
    return daily_download_response(limit=limit)