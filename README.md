# SurakshaNet AI

SurakshaNet AI is a local real-time AI surveillance MVP built for public-safety monitoring using computer vision, event rules, a FastAPI backend, SQLite storage, WebSocket alerts, and a professional React dashboard.

The system runs locally on Windows and uses a webcam as the live video source.

---

## Project Status

Current status:

```text
Final MVP Stabilization
```

This project is focused on a stable, working surveillance MVP rather than a large enterprise surveillance platform.

---

## Core Features

- Live webcam surveillance
- YOLOv8n person/general object detection
- Stable person tracking
- Intrusion detection
- Loitering detection
- Crowd detection
- Event Engine V2 without PPE
- FastAPI backend
- SQLite event database
- WebSocket realtime alerts
- Professional React dashboard
- Login authentication
- Event analytics
- JSON / CSV report export
- Daily summary export
- Alert snapshot evidence
- Smooth CPU performance mode
- Dashboard settings panel
- Reviewed / unreviewed alert status in dashboard

---

## MVP Scope

Included in MVP:

```text
Live Camera → Detection → Tracking → Event Rules → Backend → Database → WebSocket → Dashboard → Reports
```

Excluded from current MVP:

- PPE detection
- Multi-camera support
- Face recognition
- Cloud deployment
- YOLO-World live weapon detection
- Mobile app
- Advanced AI reasoning layer
- Production-grade authentication

These are intentionally excluded to keep the MVP stable, fast, and demo-ready.

---

## Tech Stack

### AI / Computer Vision

- Python
- OpenCV
- Ultralytics YOLOv8n
- Lightweight tracking logic
- Rule-based Event Engine V2

### Backend

- FastAPI
- Uvicorn
- SQLite
- WebSocket
- Static file serving for alert snapshots

### Frontend

- React
- Vite
- JavaScript
- Professional dark dashboard UI

---

## Project Structure

```text
SurakshaNet-AI/
│
├── ai_engine/
│   └── inference/
│       └── detector.py
│
├── alert_system/
│   └── dispatcher.py
│
├── backend/
│   └── app/
│       ├── api/
│       │   ├── router.py
│       │   └── routes/
│       │       ├── analytics.py
│       │       ├── auth.py
│       │       ├── events.py
│       │       └── reports.py
│       ├── database.py
│       ├── main.py
│       ├── services/
│       │   └── tracking_service.py
│       └── websocket_manager.py
│
├── event_engine/
│   └── engine.py
│
├── frontend/
│   └── dashboard/
│       └── src/
│           └── App.jsx
│
├── pipelines/
│   └── tracking_pipeline.py
│
├── tracking/
│   └── bytetrack/
│       └── tracker.py
│
├── docs/
│   ├── demo_guide.md
│   └── screenshots/
│
├── scripts/
│   └── run_demo_windows.md
│
├── recordings/
│   └── snapshots/
│
└── README.md
```

---

## Setup Instructions

### 1. Clone or open project

```powershell
cd E:\Copycat2
```

### 2. Create and activate Python virtual environment

```powershell
python -m venv venv
venv\Scripts\activate
```

### 3. Install Python dependencies

```powershell
pip install -r requirements.txt
```

If `requirements.txt` is not fully updated, install core dependencies manually:

```powershell
pip install fastapi uvicorn opencv-python ultralytics requests python-multipart imageio imageio-ffmpeg
```

### 4. Install frontend dependencies

```powershell
cd frontend\dashboard
npm install
```

---

## Environment Variables

Create a `.env` file in project root:

```env
DASHBOARD_USERNAME=admin
DASHBOARD_PASSWORD=admin123
DASHBOARD_TOKEN=surakshanet-demo-token
```

Demo login:

```text
Username: admin
Password: admin123
```

---

## Run Project

Open three terminals.

---

### Terminal 1 — Backend

```powershell
cd E:\Copycat2
venv\Scripts\activate
uvicorn backend.app.main:app --reload
```

Backend runs at:

```text
http://127.0.0.1:8000
```

Health check:

```text
http://127.0.0.1:8000/health
```

---

### Terminal 2 — AI Pipeline

```powershell
cd E:\Copycat2
venv\Scripts\activate
python pipelines/tracking_pipeline.py
```

This starts:

- webcam capture
- YOLO detection
- tracking
- event engine
- backend event sending
- snapshot evidence saving
- dashboard frame streaming

Press `q` in the camera window to stop.

---

### Terminal 3 — Dashboard

```powershell
cd E:\Copycat2\frontend\dashboard
npm run dev
```

Open manually in Chrome:

```text
http://localhost:5173
```

Do not Ctrl+Click from VS Code if it opens inside VS Code Simple Browser.

---

## Main API Endpoints

### Health

```text
GET /health
```

### Events

```text
GET /events
POST /events
POST /events/test
DELETE /events
```

### WebSocket

```text
WS /ws/events
```

### Live Video

```text
POST /frame
GET /video_feed
```

### Analytics

```text
GET /analytics/summary
GET /analytics/by-type
GET /analytics/risk-zones
```

### Reports

```text
GET /reports/events/json
GET /reports/events/csv
GET /reports/daily-summary/json
```

### Auth

```text
POST /auth/login
GET /auth/verify
```

---

## Dashboard Features

The dashboard includes:

- Secure login screen
- Live camera feed
- WebSocket/API status indicators
- Operator status row
- Demo mode banner
- Event filters
- Test alert button
- Analytics cards
- Incident summary panel
- Camera/system health panel
- Alert feed
- Snapshot preview
- Mark reviewed / unreviewed
- JSON and CSV export buttons
- Daily summary export
- Settings panel
- Dark/light mode switch

---

## Event Logic

### Intrusion

Detects when a tracked person remains inside a restricted zone for a configured duration.

### Loitering

Detects when the same tracked person remains near the same location for a configured time.

### Crowd Alert

Detects when multiple tracked people stay inside a zone for a configured duration.

### Weapon Detection

Weapon AI is disabled in the final MVP because open-vocabulary YOLO-World was too slow on CPU and a proper custom weapon model is not included.

---

## Performance Mode

The project is optimized for CPU-only laptop demo.

Recommended pipeline settings:

```python
DETECTION_EVERY_N_FRAMES = 6
STREAM_EVERY_N_FRAMES = 3
ENABLE_VIDEO_CLIPS = False
DRAW_NON_PERSON_OBJECTS = False
```

Snapshots are enabled.

Video clips are disabled by default for smooth live performance.

---

## Demo Guide

Detailed demo instructions are available here:

```text
docs/demo_guide.md
```

Quick demo flow:

```text
Login → Show live feed → Trigger test alert → Trigger real intrusion → Show snapshot → Show analytics → Export report
```

---

## Known Limitations

- Single webcam only
- CPU-only performance
- No real PPE detection
- No production-grade weapon detection
- No cloud deployment
- SQLite is used for local prototype storage
- Authentication is demo-level only
- Dashboard reviewed/unreviewed state is frontend-local only

---

## Final MVP Goal

SurakshaNet AI is designed as a polished, stable, local AI surveillance MVP.

The goal is not to be an enterprise-grade CCTV platform yet. The goal is to demonstrate a complete working pipeline:

```text
AI Detection → Tracking → Event Intelligence → Backend → Realtime Dashboard → Reports
```

---

## License

For educational and demonstration use.
