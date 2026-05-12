\# SurakshaDrishti AI — Feature List



\*\*Team:\*\* TriNetra  

\*\*Mode:\*\* Final MVP



\---



\## 1. Live Camera Feed



\- Local webcam feed

\- OpenCV frame processing

\- Backend frame streaming

\- Dashboard live view

\- Clean camera overlay

\- LIVE and CAM-01 badges fixed



\---



\## 2. AI Object Detection



\- YOLOv8n-based object detection

\- Yellow boxes for detected objects

\- CPU-friendly detection interval

\- Visible non-person object detections

\- Real-time detection preview



\---



\## 3. Person Tracking



\- Stable person IDs

\- Green boxes for tracked persons

\- Lightweight custom tracker

\- Miss tolerance to reduce flicker

\- Tracking used by event engine logic



\---



\## 4. Event Engine



\- Receives detections and tracked persons

\- Generates safety events

\- Supports rule-based alert logic

\- Sends alerts to backend

\- Provides data for dashboard alerts and analytics



\---



\## 5. Alerts Feed



\- Real-time alert list

\- Severity labels

\- Critical alert highlighting

\- SOS alert pinning

\- Alerts visible in dashboard



\---



\## 6. SOS Emergency Panel



\- Reporter name field

\- Phone/contact field

\- Incident location field

\- Incident type selection

\- Help needed selection:

&#x20; - Police

&#x20; - Ambulance

&#x20; - Fire

&#x20; - Rescue

&#x20; - Security

\- Incident details field

\- Creates CRITICAL SOS alert

\- Sends alert to backend

\- Shows alert in dashboard



\---



\## 7. Active Emergency Banner



\- Shows unresolved SOS alerts

\- Stays visible until incident is resolved

\- Displays incident type

\- Displays location

\- Displays help needed

\- Displays authority status



\---



\## 8. Authority Response Center



\- Shows pending incidents

\- Shows assigned incidents

\- Shows running incidents

\- Shows resolved incidents

\- Supports Assign action

\- Supports Mark Running action

\- Supports Resolve action

\- Updates summary counters



\---



\## 9. Dispatch Workflow



Supported workflow:



```txt

PENDING → ASSIGNED → DISPATCHED/RUNNING → RESOLVED





Dashboard labels:



PENDING    → Pending

ASSIGNED   → Assigned

DISPATCHED → Running

RESOLVED   → Resolved

10\. Heatmap

Risk visualization

Event-driven analytics

Dashboard risk summary

Helps demonstrate command-center decision support

11\. Analytics

Event summary

Severity summary

Risk information

Dashboard status panels

12\. Local AI Assistant

Floating assistant button

Assistant section

Human-like replies

Auto-scroll to latest message

Dashboard-aware answers

Navigation support

Project and team context

Demo support commands



Example questions:



system health

show pending incidents

show latest alert

what should I do next?

how to demo?

13\. Evidence Support

Snapshot folder available

Snapshot evidence for alerts

Video clips disabled by default for performance

Recording folders prepared

14\. Run Scripts



Created scripts:



start\_backend.ps1

start\_frontend.ps1

start\_pipeline.ps1

START\_FULL\_SYSTEM.txt



Purpose:



Start backend quickly

Start frontend quickly

Start AI camera pipeline quickly

Guide full system startup

15\. Backup

Final working backup created

Timestamped backup stored

Rollback point available before final polish

Final MVP Summary

Backend: Working

Frontend: Working

Live Feed: Working

Object Detection: Working

Person Tracking: Working

SOS: Working

SOS Pinning: Working

Authority Workflow: Working

Heatmap: Working

Assistant: Working

Documentation: Completed

