# SurakshaNet AI

SurakshaNet AI is a real-time AI surveillance prototype with live camera streaming, AI detection, person tracking, event rules, realtime alerts, backend APIs, SQLite storage, analytics, reports, and a professional dashboard.

---

## Demo Guide

For presentation/demo instructions, see:

```text
docs/demo_guide.md
```

The demo guide includes:

- exact run order
- demo flow
- test alert instructions
- snapshot verification
- export/report demo
- troubleshooting checklist
- final demo checklist

---

## Current Working Features

- Live webcam feed
- YOLO-based detection pipeline
- Person tracking
- Intrusion detection
- Loitering detection
- Crowd alert logic
- Alert cooldown system
- FastAPI backend
- WebSocket realtime alerts
- React dashboard
- Professional SOC-style UI
- Alert toast notifications
- Alert sound effect
- SQLite event database
- Event history
- Event filters
- Backend analytics API
- Dashboard analytics sync
- JSON event report export
- CSV event report export
- Daily incident summary export
- Camera ID and timestamp metadata

---

## System Architecture

```text
Camera Feed
    ↓
AI Detection
    ↓
Person Tracking
    ↓
Behavior / Event Engine
    ↓
Alert Dispatcher
    ↓
FastAPI Backend
    ↓
SQLite Database
    ↓
WebSocket Realtime Events
    ↓
React Dashboard
```

Main Project Structure
backend/
app/
main.py
database.py
websocket_manager.py
api/
router.py
routes/
events.py
analytics.py
reports.py

ai_engine/
inference/
detector.py

tracking/
bytetrack/
tracker.py

event_engine/
engine.py

alert_system/
dispatcher.py

pipelines/
tracking_pipeline.py

frontend/
dashboard/
src/
App.jsx
Run Instructions

Open three terminals.

Terminal 1 — Backend
uvicorn backend.app.main:app --reload

Backend URL:

http://127.0.0.1:8000
Terminal 2 — AI Pipeline
python pipelines/tracking_pipeline.py

This starts webcam, detection, tracking, event rules, frame streaming, and backend event sending.

Press q to stop the camera window.

Terminal 3 — Frontend Dashboard
cd frontend/dashboard
npm run dev

Dashboard URL:

http://localhost:5173
API Endpoints
Backend Health
GET /
GET /health
Events
GET /events
GET /events?type=INTRUSION
GET /events?severity=HIGH
GET /events?limit=20
POST /events
DELETE /events
Video Stream
POST /frame
GET /video_feed
WebSocket
WS /ws/events
Analytics
GET /analytics/summary
GET /analytics/by-type
GET /analytics/by-severity
GET /analytics/risk-zones
Reports
GET /reports/events/json
GET /reports/events/csv
GET /reports/daily-summary
GET /reports/daily-summary/json
Event Types
INTRUSION
LOITERING
CROWD_ALERT
WEAPON_DETECTED
PPE_VIOLATION

Weapon and PPE detection are hooks and require proper trained/custom models for reliable real detection.

Event Metadata Example
{
"type": "INTRUSION",
"severity": "HIGH",
"object_id": 0,
"zone": "Main Gate",
"bbox": [100, 120, 300, 420],
"camera_id": "CAM-01",
"camera_name": "Main Gate Camera",
"camera_location": "Main Gate",
"timestamp": "2026-05-11T14:30:00",
"created_at": "2026-05-11T14:30:00"
}
Database

SQLite database location:

database/surakshanet_events.db

The database stores event history, camera metadata, timestamps, raw event JSON, and report-ready data.

Known Limitations
Only one camera is fully wired right now.
Weapon detection depends on available model quality.
PPE detection is currently a hook unless a PPE model is added.
Authentication is not added yet.
Production deployment is not configured yet.
SQLite is suitable for local prototype/demo.
Audio detection is not yet integrated.
Edge deployment is not finalized.
Recommended Next Phases
Phase 12 — Per-camera analytics
Phase 13 — Multi-camera support
Phase 14 — Real weapon/PPE model integration
Phase 15 — Login/auth
Phase 16 — Recording/playback
Phase 17 — Telegram/email alert integration
Phase 18 — Docker deployment
Phase 19 — Edge deployment
Stable Checkpoint

Current stable checkpoint:

Working realtime AI surveillance dashboard with:
camera stream + detection + tracking + behavior rules + backend + WebSocket + database +
