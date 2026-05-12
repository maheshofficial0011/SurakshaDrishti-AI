"""
SurakshaDrishti AI — Tracking Service

Purpose:
- Adapter between detection pipeline and tracker.
- Keeps the existing service contract unchanged.
- Tracks only persons for Event Engine logic.

Input:
[
    {
        "bbox": [x1, y1, x2, y2],
        "conf": 0.82,
        "class": "person"
    }
]

Output:
[
    {
        "id": track_id,
        "bbox": [x1, y1, x2, y2],
        "conf": conf
    }
]
"""

from tracking.bytetrack.tracker import Tracker


class TrackingService:
    def __init__(self):
        # Stable CPU-friendly tracking settings.
        # min_hits=1 makes IDs visible immediately in the live demo.
        self.tracker = Tracker(
            iou_threshold=0.25,
            center_distance_threshold=160,
            max_missed=15,
            min_hits=1,
        )

    def process(self, detections):
        """
        Process detections and return tracked person objects.

        Notes:
        - Only person detections are tracked.
        - Non-person objects are still shown by the pipeline as detections,
          but they do not get stable IDs in this MVP.
        """

        detections = detections or []

        person_detections = []

        for det in detections:
            cls_name = str(det.get("class", "")).lower().strip()

            if cls_name != "person":
                continue

            bbox = det.get("bbox")

            if not bbox or len(bbox) != 4:
                continue

            try:
                clean_bbox = [int(v) for v in bbox]
                conf = float(det.get("conf", 0.0) or 0.0)
            except Exception:
                continue

            person_detections.append(
                {
                    "bbox": clean_bbox,
                    "conf": conf,
                }
            )

        return self.tracker.update(person_detections)
