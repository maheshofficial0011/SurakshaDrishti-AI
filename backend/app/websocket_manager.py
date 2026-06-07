"""
SurakshaDrishti AI - WebSocket Manager

Purpose:
- Manage dashboard WebSocket clients.
- Broadcast real-time events to connected frontend clients.
- Keep terminal logs Windows-safe by avoiding emoji output.
"""

from typing import List

from fastapi import WebSocket


active_connections: List[WebSocket] = []


async def connect_websocket(websocket: WebSocket) -> None:
    """
    Accept and register a new WebSocket client.
    """
    await websocket.accept()
    active_connections.append(websocket)

    # ASCII-only log avoids Windows UnicodeEncodeError.
    print("[WS] WebSocket client connected")


def disconnect_websocket(websocket: WebSocket) -> None:
    """
    Remove a WebSocket client from active connections.
    """
    if websocket in active_connections:
        active_connections.remove(websocket)

    # ASCII-only log avoids Windows UnicodeEncodeError.
    print("[WS] WebSocket client disconnected")


async def broadcast_event(event: dict) -> None:
    """
    Broadcast an event to all connected WebSocket clients.

    Failed/dead clients are removed safely.
    """
    disconnected_clients = []

    for connection in active_connections:
        try:
            await connection.send_json(event)
        except Exception:
            disconnected_clients.append(connection)

    for connection in disconnected_clients:
        disconnect_websocket(connection)


async def broadcast_message(message: dict) -> None:
    """
    Generic broadcast helper for non-event messages.
    """
    await broadcast_event(message)