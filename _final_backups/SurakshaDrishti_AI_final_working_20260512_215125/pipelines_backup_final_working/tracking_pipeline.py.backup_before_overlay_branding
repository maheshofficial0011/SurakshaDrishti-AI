"""
SurakshaNet AI — Final MVP Tracking Pipeline

Purpose:
- Read frames from webcam
- Run YOLOv8n detection with throttling
- Track persons with stable IDs
- Run Event Engine V3.1 logic
- Save snapshot evidence
- Send events to FastAPI backend
- Send annotated frames to dashboard live feed
- Keep terminal output clean and professional

Final MVP mode:
- CPU-friendly
- YOLOv8n only
- PPE excluded
- Weapon AI disabled/hook only
- Snapshots enabled
- Video clips disabled by default
"""

import os
import sys
import cv2
import time
import requests
import imageio.v2 as imageio

from datetime import datetime
from pathlib import Path
from collections import deque
from threading import Thread

# ---------------------------------------------------------------------
# Windows/OpenCV camera stability
# ---------------------------------------------------------------------
# Disables MSMF priority to avoid some webcam issues on Windows.

# ---------------------------------------------------------------------
# Windows/OpenCV camera stability + quieter terminal
# ---------------------------------------------------------------------
# Reduce OpenCV backend warning noise and allow fallback camera backends.

os.environ["OPENCV_VIDEOIO_PRIORITY_MSMF"] = "0"

try:
    cv2.setLogLevel(0)
except Exception:
    pass


# ---------------------------------------------------------------------
# Project path setup
# ---------------------------------------------------------------------

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(PROJECT_ROOT)


# ---------------------------------------------------------------------
# Local imports
# ---------------------------------------------------------------------

from backend.app.services.tracking_service import TrackingService
from event_engine.engine import EventEngine
from ai_engine.inference.detector import Detector

from utils.terminal import (
    print_banner,
    print_ok,
    print_info,
    print_warn,
    print_error,
    print_running,
    print_frame_status,
    print_alert,
    print_shutdown,
)

# ---------------------------------------------------------------------
# Backend endpoints
# ---------------------------------------------------------------------

BACKEND_EVENTS_URL = "http://127.0.0.1:8000/events"
BACKEND_FRAME_URL = "http://127.0.0.1:8000/frame"


# ---------------------------------------------------------------------
# Camera metadata
# ---------------------------------------------------------------------
# This metadata is attached to every generated event so reports and
# dashboard cards can identify the source camera.

CAMERA_ID = "CAM-01"
CAMERA_NAME = "Main Gate Camera"
CAMERA_LOCATION = "Main Gate"


# ---------------------------------------------------------------------
# Evidence directories
# ---------------------------------------------------------------------

RECORDINGS_DIR = Path("recordings")

SNAPSHOTS_DIR = RECORDINGS_DIR / "snapshots"
SNAPSHOTS_DIR.mkdir(parents=True, exist_ok=True)

CLIPS_DIR = RECORDINGS_DIR / "clips"
CLIPS_DIR.mkdir(parents=True, exist_ok=True)


# ---------------------------------------------------------------------
# Performance settings
# ---------------------------------------------------------------------
# These values are chosen for smooth local CPU demo performance.

CLIP_FPS = 5
CLIP_SECONDS = 2
FRAME_BUFFER_SIZE = CLIP_FPS * CLIP_SECONDS

DETECTION_EVERY_N_FRAMES = 6
STREAM_EVERY_N_FRAMES = 3
RECORDING_COOLDOWN_SECONDS = 15

# Video clips are disabled for final MVP smooth mode.
# Snapshots remain enabled and are much cheaper than MP4 encoding.
ENABLE_VIDEO_CLIPS = False

# Drawing non-person detections can add visual clutter and small overhead.
# Keep False for clean demo mode.
DRAW_NON_PERSON_OBJECTS = False

# Terminal status should not print every frame.
FRAME_STATUS_EVERY_N_FRAMES = 30


# ---------------------------------------------------------------------
# Event helpers
# ---------------------------------------------------------------------


def enrich_event_metadata(event):
    """
    Add camera identity and wall-clock timestamp to an event.

    The Event Engine produces behavior events.
    This pipeline enriches them with source camera metadata before sending
    them to the backend.
    """

    event["camera_id"] = CAMERA_ID
    event["camera_name"] = CAMERA_NAME
    event["camera_location"] = CAMERA_LOCATION
    event["timestamp"] = datetime.now().isoformat()

    return event


def send_event_to_backend(event):
    """
    Send one event to the FastAPI backend.

    Terminal output is intentionally minimal.
    Detailed event display is handled through print_alert().
    """

    try:
        response = requests.post(
            BACKEND_EVENTS_URL,
            json=event,
            timeout=1,
        )

        if response.status_code >= 400:
            print_warn(f"Backend event response: {response.status_code}")

    except Exception as exc:
        print_warn(f"Backend event API unavailable: {exc}")


def save_event_snapshot(frame, event):
    """
    Save a JPEG snapshot for an alert event.

    Snapshot evidence is lightweight and useful for dashboard review.
    """

    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        event_type = event.get("type", "EVENT")
        camera_id = event.get("camera_id", "CAM")

        filename = f"{camera_id}_{event_type}_{timestamp}.jpg"
        file_path = SNAPSHOTS_DIR / filename

        cv2.imwrite(str(file_path), frame)

        event["snapshot_file"] = filename
        event["snapshot_url"] = f"http://127.0.0.1:8000/recordings/snapshots/{filename}"

        return event

    except Exception as exc:
        print_warn(f"Snapshot save error: {exc}")
        return event


def save_event_clip(frame_buffer_snapshot, event):
    """
    Save a browser-compatible MP4 clip.

    This is optional and disabled by default because MP4 encoding is CPU-heavy.
    """

    try:
        if not frame_buffer_snapshot:
            return event

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        event_type = event.get("type", "EVENT")
        camera_id = event.get("camera_id", "CAM")

        filename = f"{camera_id}_{event_type}_{timestamp}.mp4"
        file_path = CLIPS_DIR / filename

        rgb_frames = []

        for buffered_frame in frame_buffer_snapshot:
            rgb_frame = cv2.cvtColor(buffered_frame, cv2.COLOR_BGR2RGB)
            rgb_frames.append(rgb_frame)

        imageio.mimsave(
            str(file_path),
            rgb_frames,
            fps=CLIP_FPS,
            codec="libx264",
            quality=6,
            macro_block_size=16,
        )

        event["clip_file"] = filename
        event["clip_url"] = f"http://127.0.0.1:8000/recordings/clips/{filename}"

        return event

    except Exception as exc:
        print_warn(f"Clip save error: {exc}")
        return event


def save_event_clip_background(frame_buffer_snapshot, event):
    """
    Save video clip in a background thread.

    This prevents clip encoding from blocking the live camera loop.
    """

    try:
        save_event_clip(frame_buffer_snapshot, event)
    except Exception as exc:
        print_warn(f"Background clip save error: {exc}")


def should_record_event(event, last_recording_time):
    """
    Decide whether snapshot/video evidence should be saved.

    A cooldown prevents repeated events from generating too many files.
    """

    event_key = (
        f"{event.get('type')}_"
        f"{event.get('object_id', 'none')}_"
        f"{event.get('zone', 'none')}"
    )

    now_ts = datetime.now().timestamp()
    last_ts = last_recording_time.get(event_key, 0)

    if (now_ts - last_ts) >= RECORDING_COOLDOWN_SECONDS:
        last_recording_time[event_key] = now_ts
        return True

    return False


def should_save_video_clip(event):
    """
    Decide whether to save video clip evidence.

    Final MVP keeps this disabled by default for performance.
    """

    if not ENABLE_VIDEO_CLIPS:
        return False

    return (
        event.get("severity") in ["HIGH", "CRITICAL"]
        or event.get("type") == "INTRUSION"
    )


# ---------------------------------------------------------------------
# Backend frame streaming
# ---------------------------------------------------------------------


def send_frame_to_backend(frame):
    """
    Send annotated frame to backend for MJPEG dashboard stream.

    This is throttled by STREAM_EVERY_N_FRAMES to reduce dashboard lag.
    """

    try:
        success, buffer = cv2.imencode(
            ".jpg",
            frame,
            [int(cv2.IMWRITE_JPEG_QUALITY), 70],
        )

        if not success:
            print_warn("Could not encode frame for dashboard stream")
            return

        requests.post(
            BACKEND_FRAME_URL,
            data=buffer.tobytes(),
            headers={"Content-Type": "image/jpeg"},
            timeout=0.35,
        )

    except Exception:
        # Avoid noisy terminal spam if backend is temporarily unavailable.
        pass


# ---------------------------------------------------------------------
# Camera helpers
# ---------------------------------------------------------------------


def open_camera(max_index=5):
    """
    Open webcam using multiple backend fallbacks.

    Why:
    - Some Windows systems fail with CAP_DSHOW.
    - Some work better with CAP_MSMF.
    - Some work only with default OpenCV backend.

    This avoids messy camera startup failures and improves compatibility.
    """

    camera_backends = [
        ("DSHOW", cv2.CAP_DSHOW),
        ("MSMF", cv2.CAP_MSMF),
        ("DEFAULT", None),
    ]

    for backend_name, backend_value in camera_backends:
        for index in range(max_index):
            try:
                if backend_value is None:
                    cap = cv2.VideoCapture(index)
                else:
                    cap = cv2.VideoCapture(index, backend_value)

                if cap.isOpened():
                    ret, test_frame = cap.read()

                    if ret and test_frame is not None:
                        cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

                        print_ok(
                            f"Webcam opened successfully | index={index} | backend={backend_name}"
                        )

                        return cap

                cap.release()

            except Exception:
                continue

    return None


# ---------------------------------------------------------------------
# Drawing helpers
# ---------------------------------------------------------------------


def draw_detections(frame, detections):
    """
    Draw non-person detections if enabled.

    Person boxes are drawn through tracked objects to show stable IDs.
    """

    if not DRAW_NON_PERSON_OBJECTS:
        return

    for det in detections:
        cls_name = det.get("class", "unknown")
        conf = float(det.get("conf", 0) or 0)

        if cls_name.lower() == "person":
            continue

        bbox = det.get("bbox")

        if not bbox or len(bbox) != 4:
            continue

        x1, y1, x2, y2 = [int(v) for v in bbox]

        cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 200, 0), 2)

        cv2.putText(
            frame,
            f"{cls_name} {conf:.2f}",
            (x1, max(y1 - 10, 20)),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (255, 200, 0),
            2,
        )


def draw_tracked_objects(frame, tracked_objects):
    """
    Draw tracked persons with stable IDs.
    """

    for obj in tracked_objects:
        bbox = obj.get("bbox")
        obj_id = obj.get("id")

        if not bbox or len(bbox) != 4 or obj_id is None:
            continue

        x1, y1, x2, y2 = [int(v) for v in bbox]

        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

        cv2.putText(
            frame,
            f"PERSON ID {obj_id}",
            (x1, max(y1 - 10, 20)),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (0, 255, 0),
            2,
        )


def draw_runtime_overlay(frame, frame_count, tracked_count):
    """
    Draw a small clean overlay on the camera preview window.
    """

    cv2.rectangle(frame, (8, 8), (310, 80), (0, 0, 0), -1)

    cv2.putText(
        frame,
        "SurakshaNet AI | Final MVP",
        (18, 32),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.6,
        (255, 255, 255),
        2,
    )

    cv2.putText(
        frame,
        f"Camera: {CAMERA_ID} | Tracked: {tracked_count} | Frame: {frame_count}",
        (18, 62),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.45,
        (180, 220, 255),
        1,
    )


# ---------------------------------------------------------------------
# Main pipeline
# ---------------------------------------------------------------------


def main():
    """
    Main runtime loop.

    This function is intentionally linear and simple:
    camera → detection → tracking → event engine → backend/dashboard
    """

    print_banner()
    print_info("Starting SurakshaNet AI pipeline...")

    cap = None

    try:
        detector = Detector()

        tracker_service = TrackingService()
        print_ok("Tracking service initialized")

        engine = EventEngine()
        print_ok("Event engine V3.1 ready")

        engine.set_zones(
            [
                {"name": "Main Gate", "box": (100, 100, 400, 400)},
                {"name": "Server Room", "box": (500, 200, 800, 500)},
            ]
        )
        print_ok("Restricted zones loaded")

        cap = open_camera()

        if cap is None:
            print_error("No webcam could be opened. Check camera permissions/device.")
            return

        window_name = "SurakshaNet AI - Final MVP"

        cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
        cv2.resizeWindow(window_name, 800, 600)

        print_info(f"Detection interval: every {DETECTION_EVERY_N_FRAMES} frames")
        print_info(f"Stream interval   : every {STREAM_EVERY_N_FRAMES} frames")
        print_info(f"Snapshots         : enabled")
        print_info(
            f"Video clips       : {'enabled' if ENABLE_VIDEO_CLIPS else 'disabled'}"
        )
        print_running()

        frame_buffer = deque(maxlen=FRAME_BUFFER_SIZE)

        frame_count = 0
        last_recording_time = {}

        last_detections = []
        last_tracked_objects = []

        last_status_time = time.time()
        fps_frame_counter = 0
        current_fps = 0.0

        while True:
            ret, frame = cap.read()

            if not ret or frame is None:
                print_warn("Frame not received from webcam")
                continue

            frame_count += 1
            fps_frame_counter += 1

            frame = cv2.resize(frame, (640, 480))

            if ENABLE_VIDEO_CLIPS:
                frame_buffer.append(frame.copy())

            # --------------------------------------------------
            # Detection + tracking throttling
            # --------------------------------------------------

            if frame_count % DETECTION_EVERY_N_FRAMES == 0:
                detections = detector.detect(frame)

                person_detections = [
                    det
                    for det in detections
                    if det.get("class", "").lower() == "person"
                ]

                tracked_objects = tracker_service.process(person_detections)

                last_detections = detections
                last_tracked_objects = tracked_objects
            else:
                detections = last_detections
                tracked_objects = last_tracked_objects

            # --------------------------------------------------
            # Event Engine
            # --------------------------------------------------

            events = engine.process(tracked_objects, detections)

            # --------------------------------------------------
            # Draw camera preview
            # --------------------------------------------------

            draw_detections(frame, detections)
            draw_tracked_objects(frame, tracked_objects)
            draw_runtime_overlay(frame, frame_count, len(tracked_objects))

            # --------------------------------------------------
            # Process generated events
            # --------------------------------------------------

            for event in events:
                event = enrich_event_metadata(event)

                if should_record_event(event, last_recording_time):
                    event = save_event_snapshot(frame, event)

                    if should_save_video_clip(event):
                        frame_buffer_snapshot = list(frame_buffer)
                        event["clip_pending"] = True

                        Thread(
                            target=save_event_clip_background,
                            args=(frame_buffer_snapshot, event.copy()),
                            daemon=True,
                        ).start()
                    else:
                        event["clip_skipped"] = True
                else:
                    event["recording_skipped"] = True

                print_alert(event)
                send_event_to_backend(event)

            # --------------------------------------------------
            # Send live frame to backend stream
            # --------------------------------------------------

            if frame_count % STREAM_EVERY_N_FRAMES == 0:
                send_frame_to_backend(frame)

            # --------------------------------------------------
            # FPS calculation + clean terminal status
            # --------------------------------------------------

            now = time.time()
            elapsed = now - last_status_time

            if elapsed >= 1.0:
                current_fps = fps_frame_counter / elapsed
                fps_frame_counter = 0
                last_status_time = now

            if frame_count % FRAME_STATUS_EVERY_N_FRAMES == 0:
                person_count = len(
                    [
                        det
                        for det in detections
                        if det.get("class", "").lower() == "person"
                    ]
                )

                print_frame_status(
                    frame_id=frame_count,
                    persons=person_count,
                    tracked=len(tracked_objects),
                    events=len(events),
                    fps=current_fps,
                )

            # --------------------------------------------------
            # Camera window
            # --------------------------------------------------

            cv2.imshow(window_name, frame)

            key = cv2.waitKey(1) & 0xFF

            if key == ord("q"):
                print_info("Q pressed. Stopping pipeline...")
                break

    except KeyboardInterrupt:
        print_warn("Keyboard interrupt received. Stopping pipeline...")

    except Exception as exc:
        print_error(f"Pipeline crashed: {exc}")
        raise

    finally:
        if cap is not None:
            cap.release()

        cv2.destroyAllWindows()
        print_shutdown()


if __name__ == "__main__":
    main()
