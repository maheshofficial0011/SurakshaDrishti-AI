# 🟢 CHANGED: Stable tracking service
# REASON: Use Tracking Stability V2 tracker with cleaner person filtering

from tracking.bytetrack.tracker import Tracker


class TrackingService:
    def __init__(self):
        self.tracker = Tracker(
            iou_threshold=0.35,
            center_distance_threshold=120,
            max_missed=10,
            min_hits=3,
        )

    def process(self, detections):
        """
        Expected detection format:
        [
            {
                "bbox": [x1, y1, x2, y2],
                "conf": 0.82,
                "class": "person"
            }
        ]
        """

        detections = detections or []

        # Track ONLY persons
        person_detections = []

        for det in detections:
            cls = det.get("class", "").lower()

            if cls != "person":
                continue

            bbox = det.get("bbox")

            if not bbox or len(bbox) != 4:
                continue

            person_detections.append(
                {
                    "bbox": [int(v) for v in bbox],
                    "conf": float(det.get("conf", 0.0)),
                }
            )

        tracked_objects = self.tracker.update(person_detections)

        return tracked_objects
