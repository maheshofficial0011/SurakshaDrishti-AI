import csv
import io
import json
import sqlite3
from pathlib import Path
from datetime import datetime, date

from fastapi import APIRouter, Query
from fastapi.responses import StreamingResponse, JSONResponse

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


def fetch_events(limit: int = 100):
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


def build_csv(events, columns):
    output = io.StringIO()
    writer = csv.writer(output)

    if not columns:
        writer.writerow(["status", "message", "generated_at"])
        writer.writerow(["NO_DATA", "No exportable records found", datetime.now().isoformat()])
        return output.getvalue()

    writer.writerow(columns)

    for event in events:
        writer.writerow([event.get(col, "") for col in columns])

    return output.getvalue()


def download_response(content: str, filename: str, media_type: str):
    return StreamingResponse(
        iter([content]),
        media_type=media_type,
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
            "Cache-Control": "no-store",
        },
    )


def csv_download(limit: int = 100):
    result = fetch_events(limit=limit)
    csv_text = build_csv(result["events"], result["columns"])

    filename = f"surakshadrishti_events_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

    return download_response(
        content=csv_text,
        filename=filename,
        media_type="text/csv",
    )


def json_download(limit: int = 100):
    result = fetch_events(limit=limit)

    payload = {
        "status": result["status"],
        "project": "SurakshaDrishti AI",
        "export_type": "events_json",
        "table": result["table"],
        "count": len(result["events"]),
        "limit": limit,
        "generated_at": datetime.now().isoformat(),
        "events": result["events"],
    }

    json_text = json.dumps(payload, indent=2, ensure_ascii=False, default=str)

    filename = f"surakshadrishti_events_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

    return download_response(
        content=json_text,
        filename=filename,
        media_type="application/json",
    )


def daily_download(limit: int = 100):
    result = fetch_events(limit=limit)
    today = date.today().isoformat()

    events = result["events"]
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

    payload = {
        "status": result["status"],
        "project": "SurakshaDrishti AI",
        "report_type": "daily_report",
        "date": today,
        "table": result["table"],
        "total_events_scanned": len(events),
        "today_events_detected": len(today_events),
        "type_counts": type_counts,
        "severity_counts": severity_counts,
        "events": today_events if today_events else events,
        "generated_at": datetime.now().isoformat(),
    }

    json_text = json.dumps(payload, indent=2, ensure_ascii=False, default=str)

    filename = f"surakshadrishti_daily_report_{today}.json"

    return download_response(
        content=json_text,
        filename=filename,
        media_type="application/json",
    )


# CSV download routes
@router.get("/reports/events/csv")
def reports_events_csv(limit: int = Query(default=100, ge=1, le=5000)):
    return csv_download(limit)


@router.get("/reports/export/csv")
def reports_export_csv(limit: int = Query(default=100, ge=1, le=5000)):
    return csv_download(limit)


@router.get("/reports/csv")
def reports_csv(limit: int = Query(default=100, ge=1, le=5000)):
    return csv_download(limit)


@router.get("/events/export/csv")
def events_export_csv(limit: int = Query(default=100, ge=1, le=5000)):
    return csv_download(limit)


@router.get("/export/csv")
def export_csv(limit: int = Query(default=100, ge=1, le=5000)):
    return csv_download(limit)


# JSON download routes
@router.get("/reports/events/json")
def reports_events_json(limit: int = Query(default=100, ge=1, le=5000)):
    return json_download(limit)


@router.get("/reports/export/json")
def reports_export_json(limit: int = Query(default=100, ge=1, le=5000)):
    return json_download(limit)


@router.get("/reports/json")
def reports_json(limit: int = Query(default=100, ge=1, le=5000)):
    return json_download(limit)


@router.get("/events/export/json")
def events_export_json(limit: int = Query(default=100, ge=1, le=5000)):
    return json_download(limit)


@router.get("/export/json")
def export_json(limit: int = Query(default=100, ge=1, le=5000)):
    return json_download(limit)


# Daily report download routes
@router.get("/reports/daily")
def reports_daily(limit: int = Query(default=100, ge=1, le=5000)):
    return daily_download(limit)


@router.get("/reports/events/daily")
def reports_events_daily(limit: int = Query(default=100, ge=1, le=5000)):
    return daily_download(limit)


@router.get("/reports/daily/json")
def reports_daily_json(limit: int = Query(default=100, ge=1, le=5000)):
    return daily_download(limit)


# Browser preview route, only if needed
@router.get("/reports/preview/json")
def reports_preview_json(limit: int = Query(default=100, ge=1, le=5000)):
    result = fetch_events(limit=limit)
    return JSONResponse(
        content={
            "status": result["status"],
            "table": result["table"],
            "count": len(result["events"]),
            "events": result["events"],
        }
    )