# 🟢 CHANGED: Centralized websocket manager
# REASON: Prevent circular imports and support scalable realtime architecture

from fastapi import WebSocket
from typing import List

active_websockets: List[WebSocket] = []


async def connect_websocket(websocket: WebSocket):

    await websocket.accept()

    active_websockets.append(websocket)

    print("🟢 WebSocket client connected")


def disconnect_websocket(websocket: WebSocket):

    if websocket in active_websockets:

        active_websockets.remove(websocket)

    print("🔴 WebSocket disconnected")


async def broadcast_event(event):

    disconnected = []

    for ws in active_websockets:

        try:
            await ws.send_json(event)

        except:
            disconnected.append(ws)

    for ws in disconnected:

        if ws in active_websockets:
            active_websockets.remove(ws)
