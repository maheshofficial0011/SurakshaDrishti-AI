# 🟢 CHANGED: Fixed ByteTrackCore class structure
# REASON: update() method indentation was broken outside class


import numpy as np


class ByteTrackCore:
    """
    Lightweight ByteTrack-style tracker
    """

    def __init__(self, iou_threshold=0.3):

        self.iou_threshold = iou_threshold

        self.next_id = 0

        self.tracks = {}

    def iou(self, box1, box2):

        x1, y1, x2, y2 = box1

        x1_p, y1_p, x2_p, y2_p = box2

        xi1 = max(x1, x1_p)
        yi1 = max(y1, y1_p)
        xi2 = min(x2, x2_p)
        yi2 = min(y2, y2_p)

        inter_area = max(0, xi2 - xi1) * max(0, yi2 - yi1)

        box1_area = (x2 - x1) * (y2 - y1)

        box2_area = (x2_p - x1_p) * (y2_p - y1_p)

        union = box1_area + box2_area - inter_area

        if union == 0:
            return 0

        return inter_area / union

    # 🟢 CHANGED: Proper update method inside class
    # REASON: Previous indentation broke class method registration

    def update(self, detections):

        updated_tracks = {}

        for det in detections:

            # Structured detection format
            x1, y1, x2, y2 = det["bbox"]

            conf = det["conf"]

            cls_name = det.get("class", "unknown")

            matched_id = None

            # Match with existing tracks
            for track_id, track in self.tracks.items():

                if self.iou(track["bbox"], (x1, y1, x2, y2)) > self.iou_threshold:

                    matched_id = track_id

                    break

            # Create new track
            if matched_id is None:

                matched_id = self.next_id

                self.next_id += 1

            updated_tracks[matched_id] = {
                "bbox": (x1, y1, x2, y2),
                "conf": conf,
                "class": cls_name,
            }

        self.tracks = updated_tracks

        return self.tracks
