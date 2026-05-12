"""
SurakshaDrishti AI — Tracking Stability V3

Purpose:
- Provide stable person IDs for the real-time surveillance pipeline.
- Reduce flicker when YOLO detections temporarily disappear.
- Show tracks immediately instead of waiting too long.
- Preserve existing output contract used by downstream modules.

Input:
[
    {
        "bbox": [x1, y1, x2, y2],
        "conf": 0.82
    }
]

Output:
[
    {
        "id": 1,
        "bbox": [x1, y1, x2, y2],
        "conf": 0.82
    }
]
"""

import math


def clamp_bbox(bbox):
    """
    Convert bbox values to safe integer coordinates.
    """

    if not bbox or len(bbox) != 4:
        return None

    x1, y1, x2, y2 = [int(v) for v in bbox]

    if x2 <= x1 or y2 <= y1:
        return None

    return [x1, y1, x2, y2]


def compute_iou(box_a, box_b):
    """
    Compute Intersection over Union between two bounding boxes.
    """

    ax1, ay1, ax2, ay2 = box_a
    bx1, by1, bx2, by2 = box_b

    inter_x1 = max(ax1, bx1)
    inter_y1 = max(ay1, by1)
    inter_x2 = min(ax2, bx2)
    inter_y2 = min(ay2, by2)

    inter_w = max(0, inter_x2 - inter_x1)
    inter_h = max(0, inter_y2 - inter_y1)
    inter_area = inter_w * inter_h

    area_a = max(0, ax2 - ax1) * max(0, ay2 - ay1)
    area_b = max(0, bx2 - bx1) * max(0, by2 - by1)

    union = area_a + area_b - inter_area

    if union <= 0:
        return 0.0

    return inter_area / union


def center_of(bbox):
    """
    Return center x/y of bbox.
    """

    x1, y1, x2, y2 = bbox
    return (x1 + x2) / 2.0, (y1 + y2) / 2.0


def center_distance(box_a, box_b):
    """
    Compute Euclidean center distance between two boxes.
    """

    acx, acy = center_of(box_a)
    bcx, bcy = center_of(box_b)

    return math.sqrt((acx - bcx) ** 2 + (acy - bcy) ** 2)


def box_area(bbox):
    x1, y1, x2, y2 = bbox
    return max(1, x2 - x1) * max(1, y2 - y1)


class StableTrack:
    """
    One tracked person.

    A track is kept alive for a few missed frames so the ID does not
    disappear instantly when detection flickers.
    """

    def __init__(self, track_id, bbox, conf):
        self.id = track_id
        self.bbox = bbox
        self.conf = float(conf or 0.0)

        self.age = 1
        self.hits = 1
        self.missed = 0

        # Immediately visible for demo stability.
        self.confirmed = True

    def update(self, bbox, conf):
        """
        Update track with a new detection.

        Uses bbox smoothing to reduce jitter.
        """

        bbox = clamp_bbox(bbox)

        if bbox is None:
            return

        old_box = self.bbox

        # Lower value = faster response, higher value = smoother but laggier.
        smooth = 0.55

        self.bbox = [
            int(old_box[i] * smooth + bbox[i] * (1.0 - smooth)) for i in range(4)
        ]

        self.conf = (self.conf * 0.65) + (float(conf or 0.0) * 0.35)

        self.age += 1
        self.hits += 1
        self.missed = 0
        self.confirmed = True

    def mark_missed(self):
        """
        Keep old bbox during short detection misses.
        """

        self.age += 1
        self.missed += 1

        # Slowly decay confidence while missed.
        self.conf *= 0.92

    def is_alive(self, max_missed):
        return self.missed <= max_missed

    def to_output(self):
        return {
            "id": self.id,
            "bbox": [int(v) for v in self.bbox],
            "conf": round(float(self.conf), 3),
        }


class Tracker:
    """
    Lightweight stable tracker.

    Matching strategy:
    1. Try IoU matching first.
    2. Use center-distance fallback for fast motion or small box changes.
    3. Keep missed tracks alive briefly to prevent flicker.
    4. Return tracks immediately so dashboard shows IDs without delay.
    """

    def __init__(
        self,
        iou_threshold=0.25,
        center_distance_threshold=160,
        max_missed=15,
        min_hits=1,
    ):
        self.iou_threshold = iou_threshold
        self.center_distance_threshold = center_distance_threshold
        self.max_missed = max_missed
        self.min_hits = min_hits

        self.tracks = []
        self.next_id = 1

    def _normalize_detections(self, detections):
        """
        Validate and normalize detection list.
        """

        clean = []

        for det in detections or []:
            bbox = clamp_bbox(det.get("bbox"))

            if bbox is None:
                continue

            conf = float(det.get("conf", 0.0) or 0.0)

            clean.append(
                {
                    "bbox": bbox,
                    "conf": conf,
                }
            )

        return clean

    def _match_score(self, track, det):
        """
        Compute matching score.

        Higher is better.
        A strong IoU match wins.
        Center distance allows matching when IoU is weak due to motion.
        """

        iou = compute_iou(track.bbox, det["bbox"])
        dist = center_distance(track.bbox, det["bbox"])

        # Normalize distance into 0..1 score.
        distance_score = max(
            0.0,
            1.0 - (dist / max(1.0, self.center_distance_threshold)),
        )

        # Area similarity helps avoid switching IDs between very different boxes.
        area_a = box_area(track.bbox)
        area_b = box_area(det["bbox"])
        area_ratio = min(area_a, area_b) / max(area_a, area_b)

        score = (iou * 0.60) + (distance_score * 0.30) + (area_ratio * 0.10)

        return score, iou, dist

    def update(self, detections):
        """
        Update tracker with current frame detections.
        """

        detections = self._normalize_detections(detections)

        matched_track_indexes = set()
        matched_detection_indexes = set()

        # ------------------------------------------------------------
        # Greedy global matching
        # ------------------------------------------------------------
        candidates = []

        for track_index, track in enumerate(self.tracks):
            for det_index, det in enumerate(detections):
                score, iou, dist = self._match_score(track, det)

                valid_iou_match = iou >= self.iou_threshold
                valid_distance_match = dist <= self.center_distance_threshold

                if valid_iou_match or valid_distance_match:
                    candidates.append(
                        {
                            "track_index": track_index,
                            "det_index": det_index,
                            "score": score,
                            "iou": iou,
                            "dist": dist,
                        }
                    )

        candidates.sort(key=lambda item: item["score"], reverse=True)

        for item in candidates:
            track_index = item["track_index"]
            det_index = item["det_index"]

            if track_index in matched_track_indexes:
                continue

            if det_index in matched_detection_indexes:
                continue

            track = self.tracks[track_index]
            det = detections[det_index]

            track.update(det["bbox"], det.get("conf", 0.0))

            matched_track_indexes.add(track_index)
            matched_detection_indexes.add(det_index)

        # ------------------------------------------------------------
        # Mark unmatched tracks as missed
        # ------------------------------------------------------------

        for track_index, track in enumerate(self.tracks):
            if track_index not in matched_track_indexes:
                track.mark_missed()

        # ------------------------------------------------------------
        # Create new tracks for unmatched detections
        # ------------------------------------------------------------

        for det_index, det in enumerate(detections):
            if det_index in matched_detection_indexes:
                continue

            new_track = StableTrack(
                track_id=self.next_id,
                bbox=det["bbox"],
                conf=det.get("conf", 0.0),
            )

            self.next_id += 1
            self.tracks.append(new_track)

        # ------------------------------------------------------------
        # Remove stale tracks
        # ------------------------------------------------------------

        self.tracks = [
            track for track in self.tracks if track.is_alive(self.max_missed)
        ]

        # ------------------------------------------------------------
        # Return visible tracks
        # ------------------------------------------------------------
        # For MVP dashboard, return confirmed tracks immediately.
        # Tracks with short misses are still returned so boxes do not flicker.

        outputs = []

        for track in self.tracks:
            if track.hits >= self.min_hits or track.confirmed:
                outputs.append(track.to_output())

        return outputs
