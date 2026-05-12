from pathlib import Path

p = Path("pipelines/tracking_pipeline.py")
text = p.read_text(encoding="utf-8")

backup = p.with_name("tracking_pipeline.py.backup_before_object_detection_visibility_fix")
backup.write_text(text, encoding="utf-8")

# Show non-person detections also.
text = text.replace(
    "DRAW_NON_PERSON_OBJECTS = False",
    "DRAW_NON_PERSON_OBJECTS = True",
)

# Make detection refresh faster for visible demo.
text = text.replace(
    "DETECTION_EVERY_N_FRAMES = 6",
    "DETECTION_EVERY_N_FRAMES = 3",
)

# Improve non-person label drawing.
old = '''        cv2.putText(
            frame,
            f"{cls_name} {conf:.2f}",
            (x1, max(y1 - 10, 20)),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (255, 200, 0),
            2,
        )'''

new = '''        label = f"{cls_name.upper()} {conf:.2f}"

        # Label background for readability.
        (label_w, label_h), _ = cv2.getTextSize(
            label,
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            2,
        )

        label_y = max(y1 - 10, 24)

        cv2.rectangle(
            frame,
            (x1, label_y - label_h - 8),
            (x1 + label_w + 8, label_y + 4),
            (0, 0, 0),
            -1,
        )

        cv2.putText(
            frame,
            label,
            (x1 + 4, label_y),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (255, 200, 0),
            2,
            cv2.LINE_AA,
        )'''

if old in text:
    text = text.replace(old, new, 1)

p.write_text(text, encoding="utf-8")

print("object detection visibility fix applied")
print(f"backup: {backup}")