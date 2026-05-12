"""
SurakshaNet AI — Clean Terminal Utilities

Purpose:
- Keep runtime terminal output clean and professional.
- Avoid random print spam.
- Provide consistent startup, status, alert, error, and shutdown messages.

This file has no external dependencies.
"""

from datetime import datetime

LINE = "=" * 64


def now_time():
    return datetime.now().strftime("%H:%M:%S")


def print_banner():
    print()
    print(LINE)
    print("🛡️  SurakshaNet AI — Final MVP Runtime")
    print(LINE)
    print("Mode         : Smooth CPU Demo")
    print("Detector     : YOLOv8n")
    print("Tracking     : Tracking Stability V2")
    print("Event Engine : V3.1 without PPE")
    print("Evidence     : Snapshots enabled")
    print("Video Clips  : Disabled by default")
    print(LINE)
    print()


def print_ok(message):
    print(f"[{now_time()}] [OK] {message}")


def print_info(message):
    print(f"[{now_time()}] [INFO] {message}")


def print_warn(message):
    print(f"[{now_time()}] [WARN] {message}")


def print_error(message):
    print(f"[{now_time()}] [ERROR] {message}")


def print_running():
    print()
    print("[RUNNING] Press Q in camera window or CTRL+C to stop.")
    print()


def print_frame_status(frame_id, persons, tracked, events, fps=None):
    """
    Print occasional frame status.

    Do not call this every frame unless throttled.
    """

    fps_text = f" fps={fps:.1f}" if fps is not None else ""
    print(
        f"[{now_time()}] [FRAME {frame_id}] "
        f"persons={persons} tracked={tracked} events={events}{fps_text}"
    )


def print_alert(event):
    event_type = event.get("type", "UNKNOWN")
    severity = event.get("severity", "INFO")
    message = event.get("message", "No message")

    print(f"[{now_time()}] [ALERT] {event_type} | {severity} | {message}")


def print_shutdown():
    print()
    print(LINE)
    print("🛑 SurakshaNet AI shutting down...")
    print("✔ Camera released")
    print("✔ Pipeline stopped safely")
    print("✔ Final MVP demo session ended")
    print(LINE)
    print()
