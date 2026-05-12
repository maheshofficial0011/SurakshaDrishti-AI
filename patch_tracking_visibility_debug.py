from pathlib import Path

p = Path("pipelines/tracking_pipeline.py")
text = p.read_text(encoding="utf-8")

backup = p.with_name("tracking_pipeline.py.backup_before_tracking_visibility_debug")
backup.write_text(text, encoding="utf-8")

text = text.replace(
    "DRAW_NON_PERSON_OBJECTS = False",
    "DRAW_NON_PERSON_OBJECTS = True",
)

text = text.replace(
    "DETECTION_EVERY_N_FRAMES = 6",
    "DETECTION_EVERY_N_FRAMES = 3",
)

text = text.replace(
    "def draw_runtime_overlay(frame, frame_count, tracked_count):",
    "def draw_runtime_overlay(frame, frame_count, tracked_count, detection_count=0, person_count=0):",
)

text = text.replace(
    'stats_text = f"Camera: {CAMERA_ID} | Tracked: {tracked_count} | Frame: {frame_count}"',
    'stats_text = f"Camera: {CAMERA_ID} | Det: {detection_count} | Person: {person_count} | Tracked: {tracked_count} | Frame: {frame_count}"',
)

text = text.replace(
    "draw_runtime_overlay(frame, frame_count, len(tracked_objects))",
    """person_count = len([
                det
                for det in detections
                if det.get("class", "").lower() == "person"
            ])

            draw_runtime_overlay(
                frame,
                frame_count,
                len(tracked_objects),
                detection_count=len(detections),
                person_count=person_count,
            )""",
)

p.write_text(text, encoding="utf-8")
print("tracking visibility debug patch applied")
print(f"backup: {backup}")