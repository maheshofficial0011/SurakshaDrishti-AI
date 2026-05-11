# 🟢 CHANGED: Added reports export API
# REASON: Allow dashboard to download event history as JSON/CSV

import csv
import io
import json
from datetime import datetime

from fastapi import APIRouter, Query
from fastapi.responses import Response

# 🟢 CHANGED: Added daily summary database function
# REASON: Reports API should support daily incident summary

from backend.app.database import get_events_for_export, get_daily_summary

router = APIRouter()


@router.get("/reports/events/json")
async def export_events_json(
    type: str | None = Query(default=None),
    severity: str | None = Query(default=None),
    limit: int = Query(default=1000, ge=1, le=10000),
):
    events = get_events_for_export(
        event_type=type,
        severity=severity,
        limit=limit,
    )

    report = {
        "report_name": "SurakshaNet AI Event Report",
        "generated_at": datetime.now().isoformat(),
        "filters": {
            "type": type,
            "severity": severity,
            "limit": limit,
        },
        "count": len(events),
        "events": events,
    }

    file_name = (
        f"surakshanet_event_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    )

    return Response(
        content=json.dumps(report, indent=2),
        media_type="application/json",
        headers={"Content-Disposition": f"attachment; filename={file_name}"},
    )


@router.get("/reports/events/csv")
async def export_events_csv(
    type: str | None = Query(default=None),
    severity: str | None = Query(default=None),
    limit: int = Query(default=1000, ge=1, le=10000),
):
    events = get_events_for_export(
        event_type=type,
        severity=severity,
        limit=limit,
    )

    output = io.StringIO()

    fieldnames = [
        "id",
        "type",
        "severity",
        "message",
        "object_id",
        "zone",
        "camera_id",
        "camera_name",
        "camera_location",
        "event_timestamp",
        "class_name",
        "confidence",
        "bbox",
        "created_at",
        "snapshot_url",
        "snapshot_file",
    ]

    writer = csv.DictWriter(output, fieldnames=fieldnames)

    writer.writeheader()

    for event in events:
        writer.writerow(event)

    file_name = (
        f"surakshanet_event_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    )

    return Response(
        content=output.getvalue(),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={file_name}"},
    )


# 🟢 CHANGED: Added daily summary report endpoint
# REASON: Generate date-based daily incident reports


@router.get("/reports/daily-summary")
async def daily_summary_report(
    date: str | None = Query(default=None),
):
    summary = get_daily_summary(date=date)

    return {
        "report_name": "SurakshaNet AI Daily Incident Summary",
        "summary": summary,
    }


# 🟢 CHANGED: Added downloadable daily summary JSON
# REASON: Allow operator to export daily incident summary


@router.get("/reports/daily-summary/json")
async def export_daily_summary_json(
    date: str | None = Query(default=None),
):
    summary = get_daily_summary(date=date)

    report = {
        "report_name": "SurakshaNet AI Daily Incident Summary",
        "generated_at": datetime.now().isoformat(),
        "summary": summary,
    }

    report_date = summary["date"]

    file_name = f"surakshanet_daily_summary_{report_date}.json"

    return Response(
        content=json.dumps(report, indent=2),
        media_type="application/json",
        headers={"Content-Disposition": f"attachment; filename={file_name}"},
    )
