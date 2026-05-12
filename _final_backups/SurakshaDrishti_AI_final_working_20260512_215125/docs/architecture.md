# SurakshaNet AI — System Architecture

This document explains the final MVP architecture of SurakshaNet AI.

---

## Architecture Goal

SurakshaNet AI is designed as a local real-time surveillance MVP.

The system converts a live webcam feed into intelligent safety events and displays them on a realtime dashboard.

Main pipeline:

```text
Webcam → Detection → Tracking → Event Engine → Backend → Database → WebSocket → Dashboard
```

---

## High-Level Flow

```text
1. Camera captures frames
2. YOLOv8n detects people/general objects
3. Tracking assigns stable person IDs
4. Event Engine checks rules
5. Alerts are sent to FastAPI backend
6. Backend saves events to SQLite
7. Backend broadcasts alerts through WebSocket
8. React dashboard displays alerts, analytics, snapshots, and reports
```

---

## Core Modules

### 1. Detection Module

File:

```text
ai_engine/inference/detector.py
```

Purpose:

```text
Runs YOLOv8n on webcam frames and returns detections.
```

Output format:

```json
{
  "bbox": [x1, y1, x2, y2],
  "conf": 0.82,
  "class": "person",
  "source": "general"
}
```

Current MVP mode:

```text
YOLOv8n only
CPU-stable mode
No YOLO-World live inference
No PPE detection
```

---

### 2. Tracking Module

Files:

```text
tracking/bytetrack/tracker.py
backend/app/services/tracking_service.py
```

Purpose:

```text
Tracks detected persons and assigns stable IDs.
```

Tracking Stability V2 includes:

```text
track age
missed frame tolerance
minimum hits before confirmation
IoU matching
center-distance fallback
stale track cleanup
confidence smoothing
```

Tracked output format:

```json
{
  "id": 1,
  "bbox": [x1, y1, x2, y2],
  "conf": 0.81
}
```

This output is used by the Event Engine.

---

### 3. Event Engine

File:

```text
event_engine/engine.py
```

Purpose:

```text
Converts tracked object behavior into safety events.
```

Current rules:

```text
Intrusion detection
Loitering detection
Crowd detection
Weapon hook only
```

PPE logic is excluded from final MVP.

---

## Event Logic

### Intrusion

A person must remain inside a restricted zone for a configured duration before an alert is created.

Example event:

```json
{
  "type": "INTRUSION",
  "severity": "HIGH",
  "object_id": 1,
  "zone": "Main Gate",
  "message": "Person 1 stayed inside restricted zone Main Gate"
}
```

---

### Loitering

A person must stay near the same location for a configured duration.

Example event:

```json
{
  "type": "LOITERING",
  "severity": "MEDIUM",
  "object_id": 1,
  "duration_seconds": 15
}
```

---

### Crowd Alert

A crowd alert is generated when multiple people stay inside a zone for a duration.

Example event:

```json
{
  "type": "CROWD_ALERT",
  "severity": "HIGH",
  "person_count": 3,
  "zone": "Main Gate"
}
```

---

## Backend Architecture

Backend framework:

```text
FastAPI
```

Important files:

```text
backend/app/main.py
backend/app/database.py
backend/app/websocket_manager.py
backend/app/api/router.py
```

Backend responsibilities:

```text
receive events
save events to SQLite
broadcast realtime alerts
serve live camera feed
serve alert snapshots
provide analytics APIs
provide report exports
handle dashboard login
```

---

## Database

Database:

```text
SQLite
```

Purpose:

```text
Stores event history locally.
```

Used for:

```text
dashboard event history
analytics summary
risk zones
JSON export
CSV export
daily summary
```

---

## WebSocket

Endpoint:

```text
/ws/events
```

Purpose:

```text
Pushes new alerts to the dashboard in realtime.
```

Flow:

```text
Pipeline sends alert → Backend saves alert → Backend broadcasts alert → Dashboard receives alert
```

---

## Live Video Feed

Endpoints:

```text
POST /frame
GET /video_feed
```

Flow:

```text
Pipeline sends latest annotated frame to backend.
Dashboard reads MJPEG stream from backend.
```

This allows the React dashboard to show the live AI camera feed.

---

## Snapshot Evidence

Folder:

```text
recordings/snapshots/
```

When a real camera alert occurs, the pipeline saves a snapshot and attaches:

```json
{
  "snapshot_file": "CAM-01_INTRUSION_....jpg",
  "snapshot_url": "http://127.0.0.1:8000/recordings/snapshots/..."
}
```

Snapshots are shown in the dashboard alert cards.

---

## Dashboard Architecture

Frontend:

```text
React + Vite
```

Main file:

```text
frontend/dashboard/src/App.jsx
```

Dashboard features:

```text
login screen
live camera feed
WebSocket/API status
demo mode banner
operator status row
analytics cards
incident summary
camera/system health
event filters
test alert button
report export buttons
alert feed
snapshot preview
reviewed/unreviewed local state
settings panel
dark/light mode
```

---

## Authentication

Auth endpoint:

```text
POST /auth/login
```

Environment variables:

```env
DASHBOARD_USERNAME=admin
DASHBOARD_PASSWORD=admin123
DASHBOARD_TOKEN=surakshanet-demo-token
```

Current auth is demo-level only.

Production auth would require:

```text
hashed passwords
JWT expiration
HTTPS
protected routes
role-based access
```

---

## Performance Strategy

The project is optimized for CPU-only local demo.

Recommended settings:

```python
DETECTION_EVERY_N_FRAMES = 6
STREAM_EVERY_N_FRAMES = 3
ENABLE_VIDEO_CLIPS = False
DRAW_NON_PERSON_OBJECTS = False
```

Why:

```text
YOLO inference is CPU-heavy.
Video clip encoding is CPU-heavy.
Sending every frame to backend causes dashboard lag.
```

Snapshots remain enabled because they are lightweight and useful for evidence.

---

## Final MVP Scope

Included:

```text
single webcam
YOLOv8n detection
stable tracking
intrusion detection
loitering detection
crowd detection
backend API
SQLite database
WebSocket alerts
professional dashboard
snapshots
analytics
reports
login
```

Excluded:

```text
PPE detection
multi-camera production system
face recognition
cloud deployment
YOLO-World live weapon detection
mobile app
advanced LLM reasoning
production security
```

---

## Why This Architecture Was Chosen

The final MVP prioritizes:

```text
stability
demo reliability
local execution
CPU performance
clear event logic
simple deployment
easy presentation
```

Instead of trying to build a huge surveillance platform, this MVP demonstrates a complete working end-to-end AI surveillance pipeline.
