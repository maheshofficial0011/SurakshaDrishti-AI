\# SurakshaDrishti AI — Troubleshooting Guide



\*\*Team:\*\* TriNetra  

\*\*Mode:\*\* Final MVP



\---



\## 1. Dashboard Not Opening



Run:



```powershell

cd E:\\Copycat2\\frontend\\dashboard

npm run dev







Open:



http://localhost:5173/



If there is an error, run:



npm run build



Read the error shown in the terminal.



2\. Backend Connection Refused



Start backend:



cd E:\\Copycat2

.\\start\_backend.ps1



Test backend:



Invoke-RestMethod -Uri "http://127.0.0.1:8000/health"



Expected result: backend returns a health/status response.



3\. Live Feed Not Showing



Make sure all three parts are running:



1\. Backend

2\. Frontend

3\. AI camera pipeline



Start pipeline:



cd E:\\Copycat2

.\\start\_pipeline.ps1



Also check:



Webcam is connected

Camera permission is allowed

No other app is using the webcam

4\. Camera Not Opening



Possible causes:



Camera is already used by another app

Windows camera permission is blocked

Webcam driver issue

Wrong camera index



Fix:



Close Camera, Zoom, Google Meet, Teams, OBS, or other camera apps.

Restart the AI pipeline.

Restart the laptop if the camera stays locked.

5\. Object Detection Not Showing



Yellow boxes represent object detections.



If no object boxes appear:



Make sure AI pipeline is running

Place visible objects/persons in front of camera

Restart the pipeline

Check detector/model loading in terminal

6\. Person Tracking Not Showing



Green boxes represent tracked persons.



Tracking works mainly for person detections.



Check the overlay:



Det: total detections

Person: person detections

Tracked: tracked persons



Meaning:



Person = 0

→ detector is not seeing a person



Person > 0 and Tracked = 0

→ tracker issue



Tracked > 0

→ tracking is working

7\. SOS Not Working



Test backend SOS directly:



Invoke-RestMethod -Method Post `

&#x20; -Uri "http://127.0.0.1:8000/sos" `

&#x20; -ContentType "application/json" `

&#x20; -Body '{"user\_name":"Demo User","phone":"demo","incident\_location":"Demo Laptop Location","incident\_type":"Medical Emergency","help\_needed":\["POLICE","AMBULANCE"],"details":"SOS test"}'



If this works, backend SOS is fine and the issue is likely frontend.



8\. SOS Alert Not Pinned



Expected behavior:



SOS alert appears immediately at top

Active emergency banner appears

Alert remains until linked dispatches are resolved



Check:



Alerts section

Authority section

Dispatch status

Browser console errors

9\. Authority Workflow Not Updating



Check dispatch summary:



Invoke-RestMethod -Uri "http://127.0.0.1:8000/dispatches/summary"



Status mapping:



PENDING    → Pending

ASSIGNED   → Assigned

DISPATCHED → Running

RESOLVED   → Resolved

10\. Vite Build Error



Run:



cd E:\\Copycat2\\frontend\\dashboard

npm run build



Common causes:



Invalid JSX

Missing bracket

Missing comma

Raw CSS pasted inside App.jsx

Broken string



Use your latest backup if needed.



11\. Stop Full System



Press:



CTRL + C



in each terminal:



Backend terminal

Frontend terminal

AI pipeline terminal

