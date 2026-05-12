# SurakshaDrishti AI

**Team:** TriNetra  
**Mode:** Final MVP  
**Platform:** Local Windows Real-Time AI Surveillance Prototype

---

## Project Overview

SurakshaDrishti AI is a local real-time public safety surveillance prototype.

It uses a live webcam, AI object detection, person tracking, alerts, SOS emergency reporting, heatmap analytics, and authority response workflow.

The system is designed as a command-center style dashboard where operators can monitor live video, review alerts, trigger SOS, assign response units, and resolve incidents.

---

## Main Features

- Live webcam feed
- AI object detection using YOLOv8
- Person tracking with stable IDs
- Real-time dashboard
- Alert feed
- Pinned SOS emergency alerts
- SOS emergency form
- Authority Response Center
- Dispatch workflow:
  - Pending
  - Assigned
  - Running
  - Resolved
- Heatmap section
- Analytics section
- Local AI assistant
- Snapshot evidence support
- Professional command-center UI
- CPU-friendly final MVP mode

---

## Tech Stack

### Backend

- Python
- FastAPI
- SQLite
- OpenCV
- Ultralytics YOLOv8
- REST APIs

### Frontend

- React
- Vite
- JavaScript
- CSS styling inside App.jsx

### AI / Computer Vision

- YOLOv8n
- OpenCV
- Custom lightweight person tracker
- Rule-based event engine

---

## Folder Structure

```txt
E:\Copycat2
│
├── backend/
│   └── app/
│       ├── api/
│       ├── services/
│       ├── database/
│       └── main.py
│
├── frontend/
│   └── dashboard/
│       ├── src/
│       │   └── App.jsx
│       ├── package.json
│       └── vite.config.js
│
├── pipelines/
│   └── tracking_pipeline.py
│
├── tracking/
│   └── bytetrack/
│       └── tracker.py
│
├── event_engine/
│   └── engine.py
│
├── ai_engine/
│   └── inference/
│       └── detector.py
│
├── recordings/
│   ├── snapshots/
│   └── clips/
│
├── start_backend.ps1
├── start_frontend.ps1
├── start_pipeline.ps1
├── START_FULL_SYSTEM.txt
└── README.md


How to Run the Project
Run the project in three separate PowerShell terminals.

Terminal 1 — Start Backend
cd E:\Copycat2.\start_backend.ps1
Backend runs at:
http://127.0.0.1:8000
API docs:
http://127.0.0.1:8000/docs

Terminal 2 — Start Frontend Dashboard
cd E:\Copycat2.\start_frontend.ps1
Open dashboard:
http://localhost:5173/

Terminal 3 — Start AI Camera Pipeline
cd E:\Copycat2.\start_pipeline.ps1
This starts:


Webcam capture


YOLO object detection


Person tracking


Event engine


Snapshot evidence


Live camera stream to dashboard



Health Check Commands
Backend Health
Invoke-RestMethod -Uri "http://127.0.0.1:8000/health"

Dispatch Summary
Invoke-RestMethod -Uri "http://127.0.0.1:8000/dispatches/summary"

Trigger SOS Manually
Invoke-RestMethod -Method Post `  -Uri "http://127.0.0.1:8000/sos" `  -ContentType "application/json" `  -Body '{"user_name":"Demo User","phone":"demo","incident_location":"Demo Laptop Location","incident_type":"Medical Emergency","help_needed":["POLICE","AMBULANCE"],"details":"Manual SOS test"}'

Frontend Build Check
cd E:\Copycat2\frontend\dashboardnpm run build

Demo Flow


Start backend.


Start frontend.


Start AI pipeline.


Open dashboard.


Open Live Feed.


Show object detection.


Show person tracking.


Open SOS Control.


Trigger SOS alert.


Confirm SOS alert is pinned at top.


Open Authority Response Center.


Assign unit.


Mark Running.


Resolve incident.


Confirm emergency banner disappears.


Ask AI Assistant:


system health


show pending incidents


what should I do next?


how to demo?





Current Final MVP Status
Backend API: WorkingFrontend Dashboard: WorkingLive Feed: WorkingObject Detection: WorkingPerson Tracking: WorkingSOS Alert: WorkingPinned SOS Alert: WorkingAuthority Workflow: WorkingHeatmap: WorkingAssistant: WorkingFinal Backup: CreatedRun Scripts: Created

Known Limitations
This is a local MVP prototype, not a production deployment.
Current limitations:


Runs locally on laptop.


CPU-only performance depends on hardware.


YOLOv8n is used for lightweight detection.


PPE detection is excluded in final MVP.


Weapon detection is not enabled as a heavy real-time CPU model.


Video clips are disabled by default for performance.


Tracking is optimized mainly for persons.


SOS and authority workflow are demo-realistic, not connected to actual emergency services.



Future Scope


Multi-camera support


Real IP camera / CCTV integration


Mobile app integration


Real notification system


Role-based authentication


Cloud deployment


GPU acceleration


Advanced pose/action detection


Real weapon detection model


Audio distress detection


Production-grade incident management


Real GIS map integration


Authority mobile dashboard



Team
Project: SurakshaDrishti AI
Team: TriNetra

Final Note
SurakshaDrishti AI demonstrates how AI, computer vision, dashboards, SOS workflows, and authority response management can be combined into a local public-safety command-center prototype.
