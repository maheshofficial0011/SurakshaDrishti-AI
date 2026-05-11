# 🟢 CHANGED: Tracking Stability V2
# REASON: Improve ID stability, reduce flicker, preserve tracks through short misses

import math


def compute_iou(box_a, box_b):
    ax1, ay1, ax2, ay2 = box_a
    bx1, by1, bx2, by2 = box_b

    inter_x1 = max(ax1, bx1)
    inter_y1 = max(ay1, by1)
    inter_x2 = min(ax2, bx2)
    inter_y2 = min(ay2, by2)

    inter_w = max(0, inter_x2 - inter_x1)
    inter_h = max(0, inter_y2 - inter_y1)

    inter_area = inter_w * inter_h

    area_a = (ax2 - ax1) * (ay2 - ay1)
    area_b = (bx2 - bx1) * (by2 - by1)

    union = area_a + area_b - inter_area

    if union <= 0:
        return 0.0

    return inter_area / union


def center_distance(box_a, box_b):
    ax1, ay1, ax2, ay2 = box_a
    bx1, by1, bx2, by2 = box_b

    acx = (ax1 + ax2) / 2
    acy = (ay1 + ay2) / 2

    bcx = (bx1 + bx2) / 2
    bcy = (by1 + by2) / 2

    return math.sqrt((acx - bcx) ** 2 + (acy - bcy) ** 2)


class StableTrack:
    def __init__(self, track_id, bbox, conf):
        self.id = track_id

        self.bbox = bbox
        self.conf = conf

        self.age = 1
        self.hits = 1
        self.missed = 0

        self.confirmed = False

    def update(self, bbox, conf):
        # Smooth bbox slightly
        old_box = self.bbox

        smooth = 0.7

        self.bbox = [
            int(old_box[i] * smooth + bbox[i] * (1 - smooth)) for i in range(4)
        ]

        # Smooth confidence
        self.conf = (self.conf * 0.7) + (conf * 0.3)

        self.age += 1
        self.hits += 1
        self.missed = 0

    def mark_missed(self):
        self.missed += 1
        self.age += 1

    def to_output(self):
        return {
            "id": self.id,
            "bbox": self.bbox,
            "conf": round(float(self.conf), 3),
        }


class Tracker:
    """
    Stable lightweight tracker for SurakshaNet AI.

    Features:
    - IoU matching
    - Center distance fallback
    - Track confirmation
    - Miss tolerance
    - Confidence smoothing
    - Stale cleanup
    """

    def __init__(
        self,
        iou_threshold=0.35,
        center_distance_threshold=120,
        max_missed=10,
        min_hits=3,
    ):
        self.iou_threshold = iou_threshold
        self.center_distance_threshold = center_distance_threshold

        self.max_missed = max_missed
        self.min_hits = min_hits

        self.tracks = []
        self.next_id = 1

    def update(self, detections):
        """
        detections format:
        [
            {
                "bbox": [x1, y1, x2, y2],
                "conf": 0.82
            }
        ]
        """

        detections = detections or []

        matched_tracks = set()
        matched_detections = set()

        # -----------------------------
        # 1. IoU matching
        # -----------------------------

        for track_index, track in enumerate(self.tracks):
            best_det_index = -1
            best_iou = 0

            for det_index, det in enumerate(detections):
                if det_index in matched_detections:
                    continue

                iou = compute_iou(track.bbox, det["bbox"])

                if iou > best_iou:
                    best_iou = iou
                    best_det_index = det_index

            if best_det_index >= 0 and best_iou >= self.iou_threshold:
                det = detections[best_det_index]

                track.update(det["bbox"], det.get("conf", 0.0))

                matched_tracks.add(track_index)
                matched_detections.add(best_det_index)

        # -----------------------------
        # 2. Center-distance fallback
        # -----------------------------

        for track_index, track in enumerate(self.tracks):
            if track_index in matched_tracks:
                continue

            best_det_index = -1
            best_distance = 999999

            for det_index, det in enumerate(detections):
                if det_index in matched_detections:
                    continue

                dist = center_distance(track.bbox, det["bbox"])

                if dist < best_distance:
                    best_distance = dist
                    best_det_index = det_index

            if best_det_index >= 0 and best_distance <= self.center_distance_threshold:
                det = detections[best_det_index]

                track.update(det["bbox"], det.get("conf", 0.0))

                matched_tracks.add(track_index)
                matched_detections.add(best_det_index)

        # -----------------------------
        # 3. Mark unmatched tracks missed
        # -----------------------------

        for track_index, track in enumerate(self.tracks):
            if track_index not in matched_tracks:
                track.mark_missed()

        # -----------------------------
        # 4. Create new tracks
        # -----------------------------

        for det_index, det in enumerate(detections):
            if det_index in matched_detections:
                continue

            new_track = StableTrack(
                track_id=self.next_id,
                bbox=det["bbox"],
                conf=det.get("conf", 0.0),
            )

            self.next_id += 1

            self.tracks.append(new_track)

        # -----------------------------
        # 5. Remove stale tracks
        # -----------------------------

        self.tracks = [t for t in self.tracks if t.missed <= self.max_missed]

        # -----------------------------
        # 6. Confirm stable tracks
        # -----------------------------

        confirmed_outputs = []

        for track in self.tracks:
            if not track.confirmed:
                if track.hits >= self.min_hits:
                    track.confirmed = True

            if track.confirmed:
                confirmed_outputs.append(track.to_output())

        return confirmed_outputs
