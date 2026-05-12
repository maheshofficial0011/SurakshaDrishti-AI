# Run SurakshaNet AI Demo on Windows

Open 3 terminals.

---

## Terminal 1 — Backend

```powershell
cd E:\Copycat2
venv\Scripts\activate
uvicorn backend.app.main:app --reload
```

---

## Terminal 2 — AI Pipeline

```powershell
cd E:\Copycat2
venv\Scripts\activate
python pipelines/tracking_pipeline.py
```

---

## Terminal 3 — Dashboard

```powershell
cd E:\Copycat2\frontend\dashboard
npm run dev
```

Open:

```text
http://localhost:5173
```

---

## Stop Demo

Backend terminal:

```text
CTRL + C
```

Pipeline:

```text
press q in camera window
then CTRL + C if needed
```

Frontend terminal:

```text
CTRL + C
```
