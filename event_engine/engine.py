from alert_system.dispatcher import AlertDispatcher
import time


class EventEngine:
    """
    SurakshaNet AI Event Engine V2

    Handles:
    - Intrusion detection with duration confirmation
    - Loitering detection with movement analysis
    - Zone-based crowd detection with duration confirmation
    - Weapon detection with confidence filtering
    - Alert cooldown / deduplication

    PPE logic intentionally excluded for now.
    """

    def __init__(self):
        self.zones = []
        self.alert = AlertDispatcher()

        # -----------------------------
        # Alert cooldown settings
        # -----------------------------

        self.cooldown_seconds = 10
        self.last_alert_time = {}

        # -----------------------------
        # Intrusion state
        # -----------------------------
        # Tracks how long each object stays inside each restricted zone.

        self.intrusion_start_time = {}
        self.intrusion_confirm_seconds = 1.5

        # -----------------------------
        # Loitering state
        # -----------------------------

        self.loiter_start_time = {}
        self.loiter_anchor_position = {}
        self.loiter_seconds = 15
        self.loiter_movement_threshold = 70

        # -----------------------------
        # Crowd state
        # -----------------------------

        self.crowd_threshold = 3
        self.crowd_confirm_seconds = 2.5
        self.crowd_start_time = {}

        # -----------------------------
        # Weapon filtering
        # -----------------------------

        self.weapon_classes = {"knife", "gun", "weapon", "pistol", "rifle"}
        self.weapon_confidence_threshold = 0.55
        self.weapon_seen_count = {}
        self.weapon_required_hits = 2

        # -----------------------------
        # Track cleanup
        # -----------------------------

        self.last_seen_time = {}
        self.track_stale_seconds = 20

    def set_zones(self, zones):
        """
        zones format:
        [
            {"name": "Main Gate", "box": (100, 100, 400, 400)},
            {"name": "Server Room", "box": (500, 200, 800, 500)}
        ]
        """

        self.zones = zones or []

    # -----------------------------
    # Utility helpers
    # -----------------------------

    def can_emit(self, key):
        now = time.time()
        last_time = self.last_alert_time.get(key, 0)

        if now - last_time >= self.cooldown_seconds:
            self.last_alert_time[key] = now
            return True

        return False

    def get_center(self, bbox):
        x1, y1, x2, y2 = bbox

        cx = int((x1 + x2) / 2)
        cy = int((y1 + y2) / 2)

        return cx, cy

    def distance(self, p1, p2):
        x1, y1 = p1
        x2, y2 = p2

        return ((x1 - x2) ** 2 + (y1 - y2) ** 2) ** 0.5

    def is_point_inside_zone(self, point, zone):
        cx, cy = point
        zx1, zy1, zx2, zy2 = zone["box"]

        return zx1 <= cx <= zx2 and zy1 <= cy <= zy2

    def get_zone_for_point(self, point):
        for zone in self.zones:
            if self.is_point_inside_zone(point, zone):
                return zone

        return None

    def normalize_bbox(self, bbox):
        if not bbox or len(bbox) != 4:
            return []

        return [int(v) for v in bbox]

    def make_event(
        self,
        event_type,
        severity,
        message,
        object_id=None,
        zone=None,
        bbox=None,
        extra=None,
    ):
        event = {
            "type": event_type,
            "severity": severity,
            "message": message,
            "timestamp": time.time(),
        }

        if object_id is not None:
            event["object_id"] = object_id

        if zone is not None:
            event["zone"] = zone

        if bbox is not None:
            event["bbox"] = self.normalize_bbox(bbox)

        if extra:
            event.update(extra)

        return event

    def cleanup_stale_tracks(self, active_ids, current_time):
        """
        Remove old track memory so stale object IDs do not remain forever.
        """

        stale_ids = []

        for obj_id, last_seen in self.last_seen_time.items():
            if (
                obj_id not in active_ids
                and current_time - last_seen > self.track_stale_seconds
            ):
                stale_ids.append(obj_id)

        for obj_id in stale_ids:
            self.last_seen_time.pop(obj_id, None)
            self.loiter_start_time.pop(obj_id, None)
            self.loiter_anchor_position.pop(obj_id, None)

            for key in list(self.intrusion_start_time.keys()):
                if key.startswith(f"{obj_id}:"):
                    self.intrusion_start_time.pop(key, None)

    # -----------------------------
    # Main processing
    # -----------------------------

    def process(self, tracked_objects, detections=None):
        events = []
        detections = detections or []
        tracked_objects = tracked_objects or []

        current_time = time.time()
        active_ids = set()

        zone_people_count = {}
        zone_people_ids = {}

        # -----------------------------
        # 1. Person-based logic
        # -----------------------------

        for obj in tracked_objects:
            if not obj or "bbox" not in obj or "id" not in obj:
                continue

            obj_id = obj["id"]
            bbox = self.normalize_bbox(obj["bbox"])

            if not bbox:
                continue

            active_ids.add(obj_id)
            self.last_seen_time[obj_id] = current_time

            center = self.get_center(bbox)
            current_zone = self.get_zone_for_point(center)

            if current_zone:
                zone_name = current_zone["name"]

                zone_people_count[zone_name] = zone_people_count.get(zone_name, 0) + 1
                zone_people_ids.setdefault(zone_name, []).append(obj_id)

                # -----------------------------
                # 1A. Intrusion V2
                # -----------------------------
                # Alert only after the same person remains inside zone
                # for intrusion_confirm_seconds.

                intrusion_key = f"{obj_id}:{zone_name}"

                if intrusion_key not in self.intrusion_start_time:
                    self.intrusion_start_time[intrusion_key] = current_time

                intrusion_duration = (
                    current_time - self.intrusion_start_time[intrusion_key]
                )

                if intrusion_duration >= self.intrusion_confirm_seconds:
                    alert_key = f"INTRUSION:{obj_id}:{zone_name}"

                    if self.can_emit(alert_key):
                        events.append(
                            self.make_event(
                                event_type="INTRUSION",
                                severity="HIGH",
                                object_id=obj_id,
                                zone=zone_name,
                                bbox=bbox,
                                message=(
                                    f"Person {obj_id} stayed inside restricted zone "
                                    f"{zone_name} for {intrusion_duration:.1f} seconds"
                                ),
                                extra={
                                    "duration_seconds": round(intrusion_duration, 1),
                                    "rule": "intrusion_duration_v2",
                                },
                            )
                        )
            else:
                # Person is not inside any restricted zone.
                # Remove old intrusion timers for this object.

                for key in list(self.intrusion_start_time.keys()):
                    if key.startswith(f"{obj_id}:"):
                        self.intrusion_start_time.pop(key, None)

            # -----------------------------
            # 1B. Loitering V2
            # -----------------------------
            # Person must stay near the same anchor point for loiter_seconds.

            if obj_id not in self.loiter_anchor_position:
                self.loiter_anchor_position[obj_id] = center
                self.loiter_start_time[obj_id] = current_time
            else:
                anchor = self.loiter_anchor_position[obj_id]
                move_distance = self.distance(anchor, center)

                if move_distance > self.loiter_movement_threshold:
                    self.loiter_anchor_position[obj_id] = center
                    self.loiter_start_time[obj_id] = current_time
                else:
                    loiter_duration = current_time - self.loiter_start_time[obj_id]

                    if loiter_duration >= self.loiter_seconds:
                        zone_name = (
                            current_zone["name"] if current_zone else "Camera View"
                        )
                        alert_key = f"LOITERING:{obj_id}:{zone_name}"

                        if self.can_emit(alert_key):
                            events.append(
                                self.make_event(
                                    event_type="LOITERING",
                                    severity="MEDIUM",
                                    object_id=obj_id,
                                    zone=zone_name,
                                    bbox=bbox,
                                    message=(
                                        f"Person {obj_id} remained in the same area "
                                        f"for {int(loiter_duration)} seconds"
                                    ),
                                    extra={
                                        "duration_seconds": int(loiter_duration),
                                        "movement_distance": round(move_distance, 2),
                                        "rule": "loitering_stationary_v2",
                                    },
                                )
                            )

        # -----------------------------
        # 2. Crowd Detection V2
        # -----------------------------
        # Crowd is now zone-based and duration-confirmed.
        # If no zones are configured, fallback to whole camera view.

        if self.zones:
            for zone in self.zones:
                zone_name = zone["name"]
                count = zone_people_count.get(zone_name, 0)

                if count >= self.crowd_threshold:
                    if zone_name not in self.crowd_start_time:
                        self.crowd_start_time[zone_name] = current_time

                    crowd_duration = current_time - self.crowd_start_time[zone_name]

                    if crowd_duration >= self.crowd_confirm_seconds:
                        alert_key = f"CROWD_ALERT:{zone_name}"

                        if self.can_emit(alert_key):
                            events.append(
                                self.make_event(
                                    event_type="CROWD_ALERT",
                                    severity="HIGH",
                                    zone=zone_name,
                                    message=(
                                        f"{count} people detected inside zone {zone_name} "
                                        f"for {crowd_duration:.1f} seconds"
                                    ),
                                    extra={
                                        "person_count": count,
                                        "object_ids": zone_people_ids.get(
                                            zone_name, []
                                        ),
                                        "duration_seconds": round(crowd_duration, 1),
                                        "rule": "zone_crowd_duration_v2",
                                    },
                                )
                            )
                else:
                    self.crowd_start_time.pop(zone_name, None)
        else:
            total_count = len(tracked_objects)

            if total_count >= self.crowd_threshold:
                zone_name = "Camera View"

                if zone_name not in self.crowd_start_time:
                    self.crowd_start_time[zone_name] = current_time

                crowd_duration = current_time - self.crowd_start_time[zone_name]

                if crowd_duration >= self.crowd_confirm_seconds:
                    alert_key = "CROWD_ALERT:CAMERA_VIEW"

                    if self.can_emit(alert_key):
                        events.append(
                            self.make_event(
                                event_type="CROWD_ALERT",
                                severity="HIGH",
                                zone=zone_name,
                                message=(
                                    f"{total_count} people detected in camera view "
                                    f"for {crowd_duration:.1f} seconds"
                                ),
                                extra={
                                    "person_count": total_count,
                                    "duration_seconds": round(crowd_duration, 1),
                                    "rule": "camera_crowd_duration_v2",
                                },
                            )
                        )
            else:
                self.crowd_start_time.pop("Camera View", None)

        # -----------------------------
        # 3. Weapon Detection V2
        # -----------------------------
        # Filters by class, confidence, and repeated hits.
        # Note: Real weapon detection requires custom weapon model.
        # Generic YOLOv8n COCO may not detect weapons reliably.

        for det in detections:
            cls = det.get("class", "").lower()
            conf = float(det.get("conf", 0) or 0)

            if cls not in self.weapon_classes:
                continue

            if conf < self.weapon_confidence_threshold:
                continue

            bbox = self.normalize_bbox(det.get("bbox", []))
            weapon_key = f"{cls}:{bbox}"

            self.weapon_seen_count[weapon_key] = (
                self.weapon_seen_count.get(weapon_key, 0) + 1
            )

            if self.weapon_seen_count[weapon_key] >= self.weapon_required_hits:
                alert_key = f"WEAPON_DETECTED:{cls}"

                if self.can_emit(alert_key):
                    events.append(
                        self.make_event(
                            event_type="WEAPON_DETECTED",
                            severity="CRITICAL",
                            bbox=bbox,
                            message=f"Potential weapon detected: {cls} ({conf:.2f})",
                            extra={
                                "class": cls,
                                "confidence": conf,
                                "rule": "weapon_confidence_multiframe_v2",
                            },
                        )
                    )
        # Decay old weapon memory to avoid unlimited growth
        if len(self.weapon_seen_count) > 100:
            self.weapon_seen_count.clear()

        # -----------------------------
        # 4. Cleanup stale track memory
        # -----------------------------

        self.cleanup_stale_tracks(active_ids, current_time)

        # -----------------------------
        # 5. Alert Dispatch
        # -----------------------------

        for event in events:
            self.alert.send(event)

        return events
