# SurakshaDrishti AI

<p align="center">
  <strong>AI/ML-Based Railway Crowd and Crime Monitoring System</strong><br/>
  <em>Turning Railway CCTV into Real-Time AI Safety Intelligence</em>
</p>

<p align="center">
  <img alt="Project" src="https://img.shields.io/badge/Project-SurakshaDrishti%20AI-0ea5e9?style=for-the-badge"/>
  <img alt="Team" src="https://img.shields.io/badge/Team-TriNetra-2563eb?style=for-the-badge"/>
  <img alt="Domain" src="https://img.shields.io/badge/Domain-Smart%20Automation-10b981?style=for-the-badge"/>
</p>

---

## Project Pitch

**SurakshaDrishti AI** transforms normal CCTV/webcam input into an intelligent railway safety workflow. It detects persons, monitors risky activities, generates real-time alerts, stores incident evidence and supports faster authority response through a live command dashboard.

This project is aligned with **SIH1349 - Ministry of Railways**, focusing on using existing CCTV networks for **crowd management, crime prevention and work monitoring using AI/ML**.

---

## Why This Project Matters

Railway stations are crowded, dynamic and high-risk public spaces. Traditional CCTV systems record incidents, but they do not automatically detect unusual behavior, prioritize alerts or guide fast response.

SurakshaDrishti AI demonstrates how existing surveillance infrastructure can be upgraded into a **real-time AI safety command system** without requiring a complete hardware replacement.

---

## What We Built

| Module | Status | Description |
|---|---:|---|
| Login/Auth | Implemented | Basic access flow for dashboard usage |
| Live Camera Feed | Operational | Displays live webcam/CCTV-style feed inside dashboard |
| Person Detection | Operational | YOLOv8/OpenCV pipeline detects persons from video frames |
| Alert System | Implemented | Intrusion, loitering, SOS and dispatch updates appear as alerts |
| Command Dashboard | Operational | Central view for system health, alerts, evidence and controls |
| SOS Form | Implemented | Simulates passenger/operator emergency reporting |
| Authority Workflow | Simulation-ready | Pending, assigned, running and resolved response states |
| Reports/Export | JSON/CSV ready | Converts events into reviewable summaries and reports |
| SQLite Database | Local storage | Stores event data, severity, time, camera and location details |

---

## System Workflow

```text
CCTV / Webcam Input
        ↓
OpenCV Frame Capture
        ↓
YOLOv8 Person/Object Detection
        ↓
Tracking + Event Engine
        ↓
FastAPI Backend + SQLite Storage
        ↓
React Dashboard + WebSocket Alerts
        ↓
SOS / Authority Workflow / Reports
```

---

## Technology Stack

| Layer | Technology |
|---|---|
| Frontend | React + Vite |
| Backend | FastAPI |
| AI/ML | Python, OpenCV, YOLOv8 |
| Database | SQLite |
| Realtime | WebSocket |
| Deployment Mode | Localhost demo + GitHub source |

---

## Run Commands

Run these PowerShell shortcuts from the project root:

```powershell
.\start_backend.ps1
.\start.frontend.ps1
.\start.pipeline.ps1
```

Recommended demo order:

1. Start backend.
2. Start frontend.
3. Start AI pipeline.
4. Open the local dashboard URL.
5. Show live camera feed and person detection.
6. Trigger or wait for intrusion/loitering alert.
7. Show SOS form and authority response workflow.
8. Export event report as JSON/CSV.

---

## Demo Highlights

- Live AI camera feed with person detection bounding box.
- Real-time alert banner and live alert feed.
- WebSocket-connected React dashboard.
- SOS emergency panel with incident preview.
- Authority response center with pending/assigned/running/resolved states.
- Predictive safety heatmap prototype.
- Event report and daily summary export.

---

## Honest Project Status

This is a **working MVP prototype**, not a final commercial railway product.

### Built and Working

- Login/auth
- Live camera feed
- Person detection
- Alerts
- Dashboard
- SOS form
- Dispatch simulation
- Reports/export
- SQLite database

### Prototype / Partial

- Object detection is present but unstable.
- Loitering detection works with simple logic.
- Intrusion detection works but zone logic needs improvement.
- Heatmap is simulated around the demo location.

### Future Scope

- Weapon detection.
- Stronger crowd detection and density estimation.
- Improved loitering, intrusion, fight/fall detection using pose and tracking.
- Multi-camera railway station integration.
- Privacy safeguards such as masking, role-based access and data retention policies.
- Docker/cloud deployment with scalable monitoring.

---

## Team TriNetra

| Member | Role |
|---|---|
| Mahesh Rana | Team Leader, System Architect, Full Stack Developer & Presenter |
| Laxman Chaudhary | AI/ML Module Developer |
| Pradip Singh | Backend & Database Developer |
| Ashutosh Mishra | Frontend Dashboard Developer |
| Gagan Bahadur Guru Dhami | UI/UX, Branding & Presentation Designer |
| Sandip Sha | Testing, Deployment & Demo Coordinator |
| Osama Idris Ali Mohamed | Research & Documentation Lead |

---

## Project Identity

| Detail | Value |
|---|---|
| Project Title | SurakshaDrishti AI - AI/ML-Based Railway Crowd and Crime Monitoring System |
| Team | TriNetra |
| College | Rathinam Technical Campus |
| Department | Department of Computer Science and Humanities |
| Academic Year | 2025-2026 |
| Event | YUDHISTRA Project Demo Day 2K26 |
| Problem Reference | SIH1349, Ministry of Railways |
| Domain | Smart Automation |
| Type | Software |

---

## Reviewer Summary

SurakshaDrishti AI demonstrates an end-to-end railway safety prototype: live camera input is processed by AI detection, converted into events by a rule engine, stored through a backend API, synchronized to a dashboard and connected to SOS, authority dispatch and reports. The current version proves the feasibility of upgrading CCTV monitoring into a real-time AI-assisted command-center workflow.
