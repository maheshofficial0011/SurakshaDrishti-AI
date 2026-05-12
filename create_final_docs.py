from pathlib import Path

ROOT = Path(".")

files = {
"README.md": r"""# SurakshaDrishti AI

**Team:** TriNetra  
**Mode:** Final MVP  
**Platform:** Local Windows Real-Time AI Surveillance Prototype

---

## Project Overview

SurakshaDrishti AI is a local real-time public safety surveillance prototype built to demonstrate AI-assisted monitoring, alert generation, SOS handling, and authority response workflow.

The system uses a webcam as the live camera source and processes video locally using computer vision. It detects objects, tracks persons, generates safety alerts, shows live alerts on a dashboard, supports SOS emergency triggering, and allows authority workflow actions such as Assign, Running, and Resolved.

---

## Core Features

- Live webcam surveillance feed
- YOLO-based object detection
- Person tracking with stable IDs
- Event engine for safety alerts
- Real-time dashboard
- Alerts feed with pinned SOS emergency alerts
- SOS emergency form
- Authority Response Center
- Dispatch workflow: Pending, Assigned, Running, Resolved
- Heatmap and analytics sections
- Snapshot evidence support
- Local dashboard assistant
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
- WebSocket / API polling

### Frontend
- React
- Vite
- JavaScript

### AI / Computer Vision
- YOLOv8n
- OpenCV
- Custom lightweight tracking service
- Rule-based event engine

---

## Folder Structure

```txt
E:\Copycat2
│
├── backend/
├── frontend/
│   └── dashboard/
├── pipelines/
├── tracking/
├── event_engine/
├── ai_engine/
├── recordings/
├── start_backend.ps1
├── start_frontend.ps1
├── start_pipeline.ps1
├── START_FULL_SYSTEM.txt
└── README.md