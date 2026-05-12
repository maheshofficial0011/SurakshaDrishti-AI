\# SurakshaDrishti AI — Demo Script



\*\*Team:\*\* TriNetra  

\*\*Mode:\*\* Final MVP



\---



\## Opening Line



Good morning/afternoon. We are Team TriNetra, and our project is SurakshaDrishti AI.



SurakshaDrishti AI is a real-time AI surveillance and emergency response prototype. It uses live camera input, object detection, person tracking, alerts, SOS emergency reporting, heatmap analytics, and an authority response workflow.



\---



\## Start the System



Run these in three separate PowerShell terminals.



\### Terminal 1 — Backend



```powershell

cd E:\\Copycat2

.\\start\_backend.ps1







Terminal 2 — Frontend

cd E:\\Copycat2

.\\start\_frontend.ps1

Terminal 3 — AI Pipeline

cd E:\\Copycat2

.\\start\_pipeline.ps1



Open dashboard:



http://localhost:5173/

Demo Step 1 — Dashboard Overview



Say:



This is the SurakshaDrishti AI command dashboard. It gives a complete overview of the surveillance system, including live feed, alerts, SOS, authority response, heatmap, analytics, and assistant support.



Demo Step 2 — Live Feed



Open the Live Feed section.



Say:



This is the real-time camera feed processed by our local AI pipeline. The system detects objects and tracks persons with stable IDs.



Show:



Yellow boxes for object detection

Green boxes for person tracking

Live camera overlay

Clean feed without duplicate badges

Demo Step 3 — Object Detection and Tracking



Say:



The system uses YOLO-based object detection and a lightweight stable person tracker. Object detection identifies visible items, while person tracking gives stable IDs for security events like loitering, intrusion, and crowd analysis.



Demo Step 4 — SOS Control



Open SOS Control.



Say:



This section simulates a realistic emergency report. The operator can enter reporter name, phone, incident location, incident type, help needed, and incident details.



Click Trigger SOS.



Expected result:



SOS alert appears

SOS alert is pinned at the top

Active emergency banner appears

Authority response record is created

Demo Step 5 — Alerts Section



Open Alerts.



Say:



The alert feed prioritizes critical emergency alerts. SOS alerts remain pinned until the linked authority response is resolved.



Demo Step 6 — Authority Response Center



Open Authority.



Say:



This section converts alerts into an actionable response workflow. Operators can assign a unit, mark it as running, and resolve it after response completion.



Perform:



Assign unit

Mark Running

Resolve incident



Expected result:



Pending count decreases

Running status updates

Resolved count increases

Emergency banner disappears after resolution

Demo Step 7 — Heatmap



Open Heatmap.



Say:



The heatmap section visualizes incident risk and helps operators understand safety conditions around the monitored area.



Demo Step 8 — AI Assistant



Open the assistant and ask:



system health

show pending incidents

what should I do next?



Say:



The assistant helps the operator understand dashboard state, navigate sections, and follow emergency response actions.



Closing Line



SurakshaDrishti AI is a complete local MVP showing how AI surveillance, emergency alerting, SOS reporting, analytics, and authority response can work together in one command-center system.



Thank you.

