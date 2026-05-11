# 🟢 CHANGED: Added FastAPI backend server
# REASON: Enable dashboard + API integration

import cv2
import numpy as np
from fastapi import Request
from fastapi.responses import StreamingResponse
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi import WebSocket
from typing import List

# 🟢 CHANGED: Added database initialization
# REASON: Ensure SQLite event database is created on backend startup

from backend.app.database import init_db

app = FastAPI(title="SurakshaNet AI Backend", version="1.0.0")
# 🟢 CHANGED: Initialize database at startup
# REASON: Create event table automatically

init_db()

# 🟢 CHANGED: Added CORS middleware
# REASON: Enable cross-origin requests from the frontend

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 🟢 CHANGED: Added API router registration
# REASON: Enable modular backend endpoints

from backend.app.api.router import api_router

app.include_router(api_router)

# 🟢 CHANGED: Use centralized websocket manager
# REASON: Prevent circular imports

from backend.app.websocket_manager import connect_websocket, disconnect_websocket


@app.websocket("/ws/events")
async def websocket_events(websocket: WebSocket):

    await connect_websocket(websocket)

    try:

        while True:
            await websocket.receive_text()

    except:

        disconnect_websocket(websocket)


# -----------------------------
# HEALTH CHECK
# -----------------------------
@app.get("/health")
def health():

    return {"status": "running", "system": "SurakshaNet AI"}


# -----------------------------
# ROOT ROUTE
# -----------------------------
@app.get("/")
def root():

    return {"message": "SurakshaNet AI Backend Active"}


# 🟢 CHANGED: In-memory latest frame buffer
# REASON: Dashboard needs live camera stream

latest_frame = None

# 🟢 CHANGED: WebSocket client storage
# REASON: Enable real-time dashboard event push
active_websockets: List[WebSocket] = []


@app.post("/frame")
async def receive_frame(request: Request):
    global latest_frame

    body = await request.body()
    np_arr = np.frombuffer(body, np.uint8)
    latest_frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

    return {"status": "frame received"}


def generate_video_stream():
    global latest_frame

    while True:
        if latest_frame is None:
            continue

        ret, buffer = cv2.imencode(".jpg", latest_frame)

        if not ret:
            continue

        frame_bytes = buffer.tobytes()

        yield (
            b"--frame\r\n" b"Content-Type: image/jpeg\r\n\r\n" + frame_bytes + b"\r\n"
        )


@app.get("/video_feed")
def video_feed():
    return StreamingResponse(
        generate_video_stream(), media_type="multipart/x-mixed-replace; boundary=frame"
    )
