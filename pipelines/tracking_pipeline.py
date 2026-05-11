# 🟢 CHANGED: Clean Phase 6.2 tracking pipeline
# REASON: Sends events to FastAPI backend and tracks only persons

import os
import sys
import cv2
import requests

# 🟢 CHANGED: Added browser-compatible video writer
# REASON: OpenCV mp4v clips may not play in browser video tag

import imageio.v2 as imageio
from datetime import datetime
from pathlib import Path
from collections import deque

os.environ["OPENCV_VIDEOIO_PRIORITY_MSMF"] = "0"

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(PROJECT_ROOT)

from backend.app.services.tracking_service import TrackingService
from event_engine.engine import EventEngine
from ai_engine.inference.detector import Detector

BACKEND_EVENTS_URL = "http://127.0.0.1:8000/events"
BACKEND_FRAME_URL = "http://127.0.0.1:8000/frame"

# 🟢 CHANGED: Added alert recording directories
# REASON: Store both image snapshots and short video clips as evidence

RECORDINGS_DIR = Path("recordings")

SNAPSHOTS_DIR = RECORDINGS_DIR / "snapshots"
SNAPSHOTS_DIR.mkdir(parents=True, exist_ok=True)

CLIPS_DIR = RECORDINGS_DIR / "clips"
CLIPS_DIR.mkdir(parents=True, exist_ok=True)

# 🟢 CHANGED: Added rolling video buffer settings
# REASON: Save recent frames around alert events

CLIP_FPS = 10
CLIP_SECONDS = 5
FRAME_BUFFER_SIZE = CLIP_FPS * CLIP_SECONDS
# 🟢 CHANGED: Added camera metadata
# REASON: Events and reports need camera identity/location

CAMERA_ID = "CAM-01"
CAMERA_NAME = "Main Gate Camera"
CAMERA_LOCATION = "Main Gate"


# 🟢 CHANGED: Add camera/timestamp metadata to each event
# REASON: Reports and analytics need source camera information


def enrich_event_metadata(event):
    event["camera_id"] = CAMERA_ID
    event["camera_name"] = CAMERA_NAME
    event["camera_location"] = CAMERA_LOCATION
    event["timestamp"] = datetime.now().isoformat()

    return event


# 🟢 CHANGED: Added backend debug logging
# REASON: Verify events are successfully reaching FastAPI backend
def send_event_to_backend(event):

    print("📡 Sending event to backend:", event)

    try:

        response = requests.post(BACKEND_EVENTS_URL, json=event, timeout=1)

        print("✅ Backend response:", response.status_code)

    except Exception as e:

        print("⚠ Backend API error:", e)


# 🟢 CHANGED: Save event snapshot image
# REASON: Alerts should include visual evidence for dashboard playback/review


def save_event_snapshot(frame, event):
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

    except Exception as e:
        print("⚠ Snapshot save error:", e)
        return event


# 🟢 CHANGED: Send annotated frame to backend
# REASON: Enable live dashboard camera stream

# 🟢 CHANGED: Save short alert video clip
# REASON: Alerts should include playable video evidence, not only snapshot image


# 🟢 CHANGED: Save browser-compatible alert video clip
# REASON: OpenCV mp4v MP4 files may show in dashboard but not play in browser


def save_event_clip(frame_buffer, event):
    try:
        if not frame_buffer:
            return event

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        event_type = event.get("type", "EVENT")
        camera_id = event.get("camera_id", "CAM")

        filename = f"{camera_id}_{event_type}_{timestamp}.mp4"
        file_path = CLIPS_DIR / filename

        # 🟢 CHANGED: Convert OpenCV BGR frames to RGB for imageio
        # REASON: imageio expects RGB frames for correct browser playback

        rgb_frames = []

        for buffered_frame in frame_buffer:
            rgb_frame = cv2.cvtColor(buffered_frame, cv2.COLOR_BGR2RGB)
            rgb_frames.append(rgb_frame)

        # 🟢 CHANGED: Use imageio ffmpeg writer
        # REASON: Produces browser-playable MP4 more reliably than cv2.VideoWriter

        imageio.mimsave(
            str(file_path),
            rgb_frames,
            fps=CLIP_FPS,
            codec="libx264",
            quality=7,
            macro_block_size=16,
        )

        event["clip_file"] = filename
        event["clip_url"] = f"http://127.0.0.1:8000/recordings/clips/{filename}"

        return event

    except Exception as e:
        print("⚠ Clip save error:", e)
        return event


def send_frame_to_backend(frame):
    try:
        _, buffer = cv2.imencode(".jpg", frame)

        requests.post(
            BACKEND_FRAME_URL,
            data=buffer.tobytes(),
            headers={"Content-Type": "image/jpeg"},
            timeout=0.5,
        )

    except Exception as e:
        print("⚠ Frame stream error:", e)


# 🟢 CHANGED: Add camera/timestamp metadata to each event
# REASON: Reports and analytics need source camera information


def enrich_event_metadata(event):
    event["camera_id"] = CAMERA_ID
    event["camera_name"] = CAMERA_NAME
    event["camera_location"] = CAMERA_LOCATION
    event["timestamp"] = datetime.now().isoformat()

    return event


def open_camera(max_index=5):
    for i in range(max_index):
        cap = cv2.VideoCapture(i, cv2.CAP_DSHOW)

        if cap.isOpened():
            print("Camera opened at index:", i)
            return cap

        cap.release()

    return None


def main():
    detector = Detector()
    tracker_service = TrackingService()
    engine = EventEngine()

    engine.set_zones(
        [
            {"name": "Main Gate", "box": (100, 100, 400, 400)},
            {"name": "Server Room", "box": (500, 200, 800, 500)},
        ]
    )

    cap = open_camera()

    if cap is None:
        print("❌ Camera not opening")
        return

    window_name = "SurakshaNet AI - Phase 6.2 Tracking"

    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(window_name, 800, 600)

    print("SurakshaNet AI - Phase 6.2 Live Backend Integration Active")
    # 🟢 CHANGED: Rolling frame buffer for alert video clips
    # REASON: Keep recent frames so alerts can save short evidence video

    frame_buffer = deque(maxlen=FRAME_BUFFER_SIZE)

    while True:
        ret, frame = cap.read()

        if not ret or frame is None:
            print("❌ Frame not received")
            continue

        frame = cv2.resize(frame, (640, 480))
        # 🟢 CHANGED: Store frame in rolling buffer
        # REASON: Recent frames are used to generate alert video clips

        frame_buffer.append(frame.copy())

        # 🟢 CHANGED: Use unified detector
        # REASON: Detection source for person tracking + weapon/PPE checks
        detections = detector.detect(frame)

        # 🟢 CHANGED: Track only person objects
        # REASON: Chairs, bottles, mobiles should not receive tracking IDs
        person_detections = [
            det for det in detections if det.get("class", "").lower() == "person"
        ]

        tracked_objects = tracker_service.process(person_detections)

        # Keep all detections for weapon/PPE event checks
        events = engine.process(tracked_objects, detections)

        # 🟢 CHANGED: Draw all detected objects
        # REASON: Show chair, bottle, mobile, etc. visually

        for det in detections:

            cls_name = det.get("class", "unknown")

            conf = det.get("conf", 0)

            x1, y1, x2, y2 = det["bbox"]

            # Skip person here because person is drawn separately with tracking ID
            if cls_name.lower() == "person":
                continue

            cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 200, 0), 2)

            cv2.putText(
                frame,
                f"{cls_name} {conf:.2f}",
                (x1, y1 - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (255, 200, 0),
                2,
            )

        # 🟢 CHANGED: Draw tracked persons with IDs
        # REASON: Only persons should receive tracking IDs

        for obj in tracked_objects:

            x1, y1, x2, y2 = obj["bbox"]

            obj_id = obj["id"]

            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

            cv2.putText(
                frame,
                f"PERSON ID {obj_id}",
                (x1, y1 - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (0, 255, 0),
                2,
            )

        # Send events to backend
        for event in events:

            # 🟢 CHANGED: Attach camera + timestamp metadata
            # REASON: Backend, dashboard, and reports need event source info

            event = enrich_event_metadata(event)

            # 🟢 CHANGED: Save snapshot for each event
            # REASON: Dashboard playback needs visual evidence

            event = save_event_snapshot(frame, event)

            # 🟢 CHANGED: Save alert video clip for each event
            # REASON: Alerts should include playable video evidence, not only snapshot image

            event = save_event_clip(frame_buffer, event)

            print("🚨 EVENT:", event)

            send_event_to_backend(event)

        # 🟢 CHANGED: Send annotated camera frame to backend stream
        # REASON: Dashboard can display live AI feed
        send_frame_to_backend(frame)
        cv2.imshow(window_name, frame)

        key = cv2.waitKey(1)

        if key == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
