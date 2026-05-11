# SurakshaNet AI — Demo Guide

This guide explains how to run and present the current working SurakshaNet AI prototype.

---

## Demo Goal

Show a complete AI surveillance workflow:

```text
Live Camera → AI Detection → Person Tracking → Behavior Rules → Alert → Backend → Database → Realtime Dashboard → Snapshot/Reports
```

---

## What To Show In Demo

Current working demo includes:

- Live camera feed
- Person detection
- Person tracking
- Intrusion detection
- Loitering / crowd behavior rules
- Alert cooldown
- Realtime WebSocket alert feed
- Professional React dashboard
- Backend API health status
- Manual test alert button
- SQLite event history
- Alert snapshot image
- Analytics cards
- Event filters
- JSON / CSV export
- Daily summary export

---

## Run Order

Open three terminals.

---

### Terminal 1 — Backend

```powershell
cd E:\Copycat2
venv\Scripts\activate
uvicorn backend.app.main:app --reload
```

Expected output:

```text
Uvicorn running on http://127.0.0.1:8000
```

Test in browser:

```text
http://127.0.0.1:8000/health
```

Expected:

```json
{
  "status": "running",
  "system": "SurakshaNet AI"
}
```

---

### Terminal 2 — AI Pipeline

```powershell
cd E:\Copycat2
venv\Scripts\activate
python pipelines/tracking_pipeline.py
```

Expected:

```text
Camera opened at index: 0
SurakshaNet AI ...
```

This starts:

- webcam
- detection
- tracking
- behavior rules
- alert sending
- snapshot recording
- frame streaming

Press `q` to stop the camera window.

---

### Terminal 3 — Dashboard

```powershell
cd E:\Copycat2\frontend\dashboard
npm run dev
```

Open:

```text
http://localhost:5173
```

Expected dashboard status:

```text
WS: CONNECTED | API: ONLINE
```

---

## Demo Flow

### Step 1 — Show Dashboard

Open dashboard and explain:

```text
This is the SurakshaNet AI command dashboard.
It receives realtime alerts from the AI pipeline through FastAPI and WebSocket.
```

Show:

- live camera feed
- stats cards
- analytics cards
- filtered alerts panel
- backend analytics sync

---

### Step 2 — Trigger Manual Test Alert

Click:

```text
🧪 Test Alert
```

Explain:

```text
This verifies the backend, database, WebSocket, dashboard alerts, and analytics without needing a physical event.
```

Expected:

- alert appears in right panel
- toast popup appears
- analytics update
- database event count increases

---

### Step 3 — Trigger Real Camera Alert

Stand or move in front of the camera inside the restricted zone.

Expected:

- intrusion alert appears
- object ID appears
- camera metadata appears
- snapshot image appears
- event is saved to database

Explain:

```text
The system detects a person, tracks them, checks restricted-zone rules, creates an alert, saves it, and displays it in realtime.
```

---

### Step 4 — Show Event Snapshot

In the alert card, show:

```text
Alert Snapshot
Open Snapshot
```

Explain:

```text
Every real camera alert can store visual evidence for review.
```

Snapshot folder:

```text
E:\Copycat2\recordings\snapshots
```

---

### Step 5 — Show Filters

Use filters:

```text
Event Type → INTRUSION
Severity → HIGH
Limit → 20
```

Explain:

```text
Operators can filter event history by type, severity, and limit.
```

---

### Step 6 — Show Exports

Click:

```text
⬇ JSON
⬇ CSV
📊 Daily
```

Explain:

```text
Reports can be exported for offline review, documentation, and incident analysis.
```

---

## Important API URLs

### Backend Health

```text
http://127.0.0.1:8000/health
```

### Events

```text
http://127.0.0.1:8000/events
```

### Analytics Summary

```text
http://127.0.0.1:8000/analytics/summary
```

### Reports

```text
http://127.0.0.1:8000/reports/events/json
http://127.0.0.1:8000/reports/events/csv
http://127.0.0.1:8000/reports/daily-summary
```

### Live Video Feed

```text
http://127.0.0.1:8000/video_feed
```

---

## Demo Talking Points

Use this short explanation:

```text
SurakshaNet AI is a smart public-safety surveillance prototype.
It uses computer vision to detect people, track movement, apply behavior rules like intrusion and loitering, and send realtime alerts to a professional dashboard.
The backend stores every event in SQLite, pushes alerts through WebSocket, provides analytics APIs, and exports reports.
Recent upgrades added alert snapshots, backend health monitoring, and a manual test-alert system for reliable demos.
```

---

## Current Limitations

Mention honestly:

- Current setup uses one webcam.
- Weapon/PPE detection are hooks unless proper trained models are added.
- SQLite is used for local prototype storage.
- Full production security/auth is not added yet.
- Audio detection is not integrated yet.
- Multi-camera support is future scope.

---

## Troubleshooting

### Dashboard says API OFFLINE

Make sure backend is running:

```powershell
uvicorn backend.app.main:app --reload
```

Open:

```text
http://127.0.0.1:8000/health
```

---

### Dashboard says WS DISCONNECTED

Make sure backend is running and `/ws/events` exists.

Restart dashboard:

```powershell
cd E:\Copycat2\frontend\dashboard
npm run dev
```

---

### Camera not opening

Try closing other apps using the webcam.

Run:

```powershell
python test_cam.py
```

Or change camera index in the pipeline if needed.

---

### Snapshot not showing

Check a real camera event, not a test alert.

Manual test alert does not have a frame snapshot.

Check folder:

```text
E:\Copycat2\recordings\snapshots
```

---

### No alerts appearing

Check:

```text
Backend running
Pipeline running
Dashboard running
Camera visible
Restricted zone coordinates active
```

---

## Final Demo Checklist

Before presenting:

```text
[ ] Backend starts
[ ] /health returns running
[ ] Pipeline starts
[ ] Camera feed opens
[ ] Dashboard opens
[ ] WS shows CONNECTED
[ ] API shows ONLINE
[ ] Test Alert works
[ ] Real camera alert works
[ ] Snapshot appears for real event
[ ] JSON export works
[ ] CSV export works
[ ] Daily export works
[ ] Git status is clean
```
