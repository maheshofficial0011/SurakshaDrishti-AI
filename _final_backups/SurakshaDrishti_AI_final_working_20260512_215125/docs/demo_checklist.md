# SurakshaNet AI — Final Demo Checklist

Use this checklist before recording or presenting the final MVP demo.

---

## 1. Pre-Demo Setup

Check project folder:

```powershell
cd E:\Copycat2
git status
```

Expected:

nothing to commit, working tree clean

Make sure you are on the final branch:

git branch

Recommended branch:

final-mvp-stabilization 2. Start Backend

Open Terminal 1:

cd E:\Copycat2
venv\Scripts\activate
uvicorn backend.app.main:app --reload

Check:

Uvicorn running on http://127.0.0.1:8000

Open in browser:

http://127.0.0.1:8000/health

Expected:

{
"status": "running"
}

or similar backend health response.

3. Start AI Pipeline

Open Terminal 2:

cd E:\Copycat2
venv\Scripts\activate
python pipelines/tracking_pipeline.py

Check:

Camera opened
Detector running
Tracking pipeline active

A camera window should open.

4. Start Dashboard

Open Terminal 3:

cd E:\Copycat2\frontend\dashboard
npm run dev

Open manually in Chrome:

http://localhost:5173

Do not open in VS Code Simple Browser for final demo.

5. Login

Use:

Username: admin
Password: admin123

Expected:

Dashboard opens successfully 6. Dashboard Health Check

Confirm:

WS: CONNECTED
API: ONLINE
Camera: CAM-01 Main Gate
System Health: Operational
Demo Mode Banner visible
Live feed visible 7. Test Alert

Click:

Test Alert

Confirm:

Alert appears in Live Alert Feed
Toast appears
Analytics update
Unreviewed count updates 8. Real Camera Alert

Trigger a simple real intrusion test:

Move into the configured restricted zone area in camera view.
Stay for a few seconds.

Confirm:

INTRUSION alert appears
Object ID appears
Zone appears
Snapshot appears if recording is enabled 9. Review Alert

On an alert card, click:

Mark Reviewed

Confirm:

Alert status changes from UNREVIEWED to REVIEWED
Unreviewed count decreases 10. Reports

Click:

Export JSON
Export CSV
Daily

Confirm:

Report opens/downloads
Events are included
Snapshot URL is included when available 11. Settings Panel

Open:

Settings

Confirm:

App version visible
MVP mode visible
Detection mode visible
Theme switch visible
Runtime status visible

Test:

Switch Light/Dark mode
Return to Dashboard 12. Stop Demo

Stop frontend:

CTRL + C

Stop backend:

CTRL + C

Stop pipeline:

press q in camera window
then CTRL + C if needed 13. Final Demo Talking Flow

Use this order while presenting:

1. Problem statement
2. Solution overview
3. System architecture
4. Live dashboard login
5. Live camera feed
6. AI detection + tracking explanation
7. Intrusion / loitering / crowd logic
8. Test alert
9. Snapshot evidence
10. Analytics and reports
11. Settings / MVP scope
12. Limitations
13. Future improvements
14. Known Demo Notes

Mention clearly:

PPE is excluded from final MVP.
Weapon AI is disabled for smooth CPU performance.
Video clips are disabled by default.
System runs locally on one webcam.
Authentication is demo-level. 15. Final Pass Criteria

The demo is ready when:

✔ Backend starts
✔ Pipeline starts
✔ Dashboard starts
✔ Login works
✔ Live feed visible
✔ Test alert works
✔ Real event appears
✔ Snapshot evidence works
✔ Analytics work
✔ Reports export
✔ Settings panel works
✔ No crashes during 5–10 minute demo

## Step 2 — Commit it

Run:

```powershell
cd E:\Copycat2
git add docs/demo_checklist.md
git commit -m "Add final MVP demo checklist"
git status
```
