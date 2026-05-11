# 🟢 CHANGED: Import actual tracker implementation
# REASON: tracker.py contains ByteTrackCore class

from tracking.bytetrack.tracker import ByteTrackCore


class TrackingService:
    """
    Converts detection → tracked objects for backend use
    """

    def __init__(self):

        # 🟢 CHANGED: Initialize real ByteTrackCore tracker
        # REASON: Align tracking service with actual tracker class

        self.tracker = ByteTrackCore()

    def process(self, detections):
        """
        detections from YOLO → tracking output
        """

        tracked = self.tracker.update(detections)

        result = []

        for track_id, data in tracked.items():

            x1, y1, x2, y2 = data["bbox"]

            result.append(
                {"id": track_id, "bbox": [x1, y1, x2, y2], "conf": data["conf"]}
            )

        return result
