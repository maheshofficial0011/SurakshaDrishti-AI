# 🟢 CHANGED: Strong performance tracking pipeline
# REASON: Reduce dashboard lag by throttling detection, stream upload, and video recording

import os
import sys
import cv2
import requests
import imageio.v2 as imageio

from datetime import datetime
from pathlib import Path
from collections import deque
from threading import Thread

os.environ["OPENCV_VIDEOIO_PRIORITY_MSMF"] = "0"

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(PROJECT_ROOT)

from backend.app.services.tracking_service import TrackingService
from event_engine.engine import EventEngine
from ai_engine.inference.detector import Detector

BACKEND_EVENTS_URL = "http://127.0.0.1:8000/events"
BACKEND_FRAME_URL = "http://127.0.0.1:8000/frame"


# 🟢 CHANGED: Camera metadata
# REASON: Events and reports need camera identity/location

CAMERA_ID = "CAM-01"
CAMERA_NAME = "Main Gate Camera"
CAMERA_LOCATION = "Main Gate"


# 🟢 CHANGED: Recording directories
# REASON: Store snapshots and optional video clips as alert evidence

RECORDINGS_DIR = Path("recordings")

SNAPSHOTS_DIR = RECORDINGS_DIR / "snapshots"
SNAPSHOTS_DIR.mkdir(parents=True, exist_ok=True)

CLIPS_DIR = RECORDINGS_DIR / "clips"
CLIPS_DIR.mkdir(parents=True, exist_ok=True)


# 🟢 CHANGED: Strong performance mode
# REASON: Reduce CPU load and dashboard delay on laptop

CLIP_FPS = 5
CLIP_SECONDS = 2
FRAME_BUFFER_SIZE = CLIP_FPS * CLIP_SECONDS

DETECTION_EVERY_N_FRAMES = 6
STREAM_EVERY_N_FRAMES = 3
RECORDING_COOLDOWN_SECONDS = 15

# 🟢 CHANGED: Video clips disabled by default for smooth live demo
# REASON: MP4 writing is CPU-heavy; snapshots remain enabled

ENABLE_VIDEO_CLIPS = False

# 🟢 CHANGED: Toggle drawing non-person objects
# REASON: Drawing many object boxes can add overhead

DRAW_NON_PERSON_OBJECTS = True


def enrich_event_metadata(event):
    # 🟢 CHANGED: Add camera/timestamp metadata
    # REASON: Reports and analytics need source camera information

    event["camera_id"] = CAMERA_ID
    event["camera_name"] = CAMERA_NAME
    event["camera_location"] = CAMERA_LOCATION
    event["timestamp"] = datetime.now().isoformat()

    return event


def send_event_to_backend(event):
    # 🟢 CHANGED: Reduced backend logging
    # REASON: Excessive terminal printing slows realtime pipeline

    try:
        response = requests.post(BACKEND_EVENTS_URL, json=event, timeout=1)

        if response.status_code >= 400:
            print("⚠ Backend response:", response.status_code)

    except Exception as e:
        print("⚠ Backend API error:", e)


def save_event_snapshot(frame, event):
    # 🟢 CHANGED: Save event snapshot image
    # REASON: Alerts should include lightweight visual evidence for dashboard review

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


def save_event_clip(frame_buffer_snapshot, event):
    # 🟢 CHANGED: Save browser-compatible alert video clip
    # REASON: imageio/libx264 creates browser-playable MP4 clips

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

    except Exception as e:
        print("⚠ Clip save error:", e)
        return event


def save_event_clip_background(frame_buffer_snapshot, event):
    # 🟢 CHANGED: Save clip in background thread
    # REASON: Prevent MP4 writing from blocking live camera loop

    try:
        save_event_clip(frame_buffer_snapshot, event)
    except Exception as e:
        print("⚠ Background clip save error:", e)


def send_frame_to_backend(frame):
    # 🟢 CHANGED: Send annotated frame to backend stream
    # REASON: Dashboard displays live AI feed through backend

    try:
        _, buffer = cv2.imencode(
            ".jpg",
            frame,
            [int(cv2.IMWRITE_JPEG_QUALITY), 70],
        )

        requests.post(
            BACKEND_FRAME_URL,
            data=buffer.tobytes(),
            headers={"Content-Type": "image/jpeg"},
            timeout=0.35,
        )

    except Exception as e:
        print("⚠ Frame stream error:", e)


def open_camera(max_index=5):
    for i in range(max_index):
        cap = cv2.VideoCapture(i, cv2.CAP_DSHOW)

        if cap.isOpened():
            print("Camera opened at index:", i)

            # 🟢 CHANGED: Reduce camera buffer
            # REASON: Helps reduce live feed latency on some webcams

            cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

            return cap

        cap.release()

    return None


def draw_detections(frame, detections):
    # 🟢 CHANGED: Draw non-person detections only when enabled
    # REASON: Allows performance mode without losing person tracking

    if not DRAW_NON_PERSON_OBJECTS:
        return

    for det in detections:
        cls_name = det.get("class", "unknown")
        conf = det.get("conf", 0)

        if cls_name.lower() == "person":
            continue

        x1, y1, x2, y2 = det["bbox"]

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


def draw_tracked_objects(frame, tracked_objects):
    # 🟢 CHANGED: Draw tracked persons with IDs
    # REASON: Only persons should receive persistent tracking IDs

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


def should_record_event(event, last_recording_time):
    # 🟢 CHANGED: Recording cooldown check
    # REASON: Prevent snapshot/video spam for same repeated event

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
    # 🟢 CHANGED: Save video only when enabled and for important alerts
    # REASON: Video encoding is heavy and should not run for every event

    if not ENABLE_VIDEO_CLIPS:
        return False

    return (
        event.get("severity") in ["HIGH", "CRITICAL"]
        or event.get("type") == "INTRUSION"
    )


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

    window_name = "SurakshaNet AI - Strong Performance Mode"

    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(window_name, 800, 600)

    print("SurakshaNet AI - Strong Performance Pipeline Active")
    print(f"Detection every {DETECTION_EVERY_N_FRAMES} frames")
    print(f"Stream every {STREAM_EVERY_N_FRAMES} frames")
    print(f"Video clips enabled: {ENABLE_VIDEO_CLIPS}")

    # 🟢 CHANGED: Rolling frame buffer for optional alert video clips
    # REASON: Keep recent frames so clips can be saved if enabled

    frame_buffer = deque(maxlen=FRAME_BUFFER_SIZE)

    # 🟢 CHANGED: Runtime performance state
    # REASON: Throttle expensive operations to keep dashboard responsive

    frame_count = 0
    last_recording_time = {}
    last_detections = []
    last_tracked_objects = []

    while True:
        ret, frame = cap.read()

        if not ret or frame is None:
            print("❌ Frame not received")
            continue

        frame_count += 1

        frame = cv2.resize(frame, (640, 480))

        # 🟢 CHANGED: Store recent frame only if clips are enabled
        # REASON: Avoid unnecessary memory copy overhead when video is off

        if ENABLE_VIDEO_CLIPS:
            frame_buffer.append(frame.copy())

        # 🟢 CHANGED: Run detection every N frames
        # REASON: YOLO is expensive; reusing recent detections reduces lag

        if frame_count % DETECTION_EVERY_N_FRAMES == 0:
            detections = detector.detect(frame)

            person_detections = [
                det for det in detections if det.get("class", "").lower() == "person"
            ]

            tracked_objects = tracker_service.process(person_detections)

            last_detections = detections
            last_tracked_objects = tracked_objects
        else:
            detections = last_detections
            tracked_objects = last_tracked_objects

        # Keep all detections for weapon/PPE event checks
        events = engine.process(tracked_objects, detections)

        draw_detections(frame, detections)
        draw_tracked_objects(frame, tracked_objects)

        for event in events:
            event = enrich_event_metadata(event)

            if should_record_event(event, last_recording_time):
                # 🟢 CHANGED: Always save snapshot after cooldown
                # REASON: Snapshot is lightweight evidence and useful for dashboard

                event = save_event_snapshot(frame, event)

                if should_save_video_clip(event):
                    # 🟢 CHANGED: Save video in background
                    # REASON: Avoid blocking live camera and dashboard stream

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
                # 🟢 CHANGED: Mark repeated event as lightweight
                # REASON: Repeated alerts should not overload recording system

                event["recording_skipped"] = True

            print("🚨 EVENT:", event)

            send_event_to_backend(event)

        # 🟢 CHANGED: Throttle live stream frame upload
        # REASON: Sending every frame overloads backend and causes dashboard lag

        if frame_count % STREAM_EVERY_N_FRAMES == 0:
            send_frame_to_backend(frame)

        cv2.imshow(window_name, frame)

        key = cv2.waitKey(1)

        if key == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
