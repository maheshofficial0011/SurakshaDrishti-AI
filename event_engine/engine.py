from alert_system.dispatcher import AlertDispatcher
import time


class EventEngine:
    """
    SurakshaNet AI — Event Engine V3.1

    Purpose:
    Convert stable tracked person objects into meaningful security events.

    Final MVP behavior:
    - Intrusion detection with duration confirmation
    - Loitering detection with stationary behavior analysis
    - Zone-based crowd detection with duration confirmation
    - Zone-specific severity
    - Dynamic confidence scoring
    - Severity escalation
    - Cooldown / deduplication
    - Stale track cleanup

    Final MVP exclusions:
    - PPE detection is excluded.
    - Weapon detection is disabled by default because the MVP does not include
      a reliable custom weapon model.
    """

    def __init__(self):
        self.zones = []
        self.alert = AlertDispatcher()

        # --------------------------------------------------
        # Final MVP tuning
        # --------------------------------------------------
        # These values are demo-friendly but still realistic enough to avoid
        # instant/fake-looking alerts.

        self.cooldown_seconds = 12

        self.intrusion_confirm_seconds = 1.2
        self.intrusion_critical_seconds = 8

        self.loiter_seconds = 8
        self.loiter_high_seconds = 20
        self.loiter_movement_threshold = 90
        self.loiter_jitter_threshold = 20

        self.crowd_threshold = 3
        self.crowd_critical_threshold = 5
        self.crowd_confirm_seconds = 2.0
        self.crowd_critical_seconds = 6.0

        # Ignore weak/unstable tracks.
        # YOLOv8n usually gives person confidence above this when detection is stable.
        self.min_track_confidence = 0.35

        # --------------------------------------------------
        # Runtime state
        # --------------------------------------------------

        self.last_alert_time = {}

        self.intrusion_start_time = {}

        self.loiter_start_time = {}
        self.loiter_anchor_position = {}
        self.loiter_last_position = {}

        self.crowd_start_time = {}
        self.crowd_last_count = {}

        self.last_seen_time = {}
        self.track_stale_seconds = 20

        # --------------------------------------------------
        # Zone-specific severity behavior
        # --------------------------------------------------
        # If your pipeline sets zones:
        # [
        #   {"name": "Main Gate", "box": (...)},
        #   {"name": "Server Room", "box": (...)}
        # ]
        #
        # Server Room is treated as more sensitive than Main Gate.

        self.zone_severity_overrides = {
            "Server Room": {
                "intrusion": "CRITICAL",
                "loitering": "HIGH",
                "crowd": "CRITICAL",
            },
            "Main Gate": {
                "intrusion": "HIGH",
                "loitering": "MEDIUM",
                "crowd": "HIGH",
            },
        }

        # --------------------------------------------------
        # Weapon hook
        # --------------------------------------------------
        # Disabled by default for final MVP.

        self.enable_weapon_detection = False
        self.weapon_classes = {"knife", "gun", "weapon", "pistol", "rifle"}
        self.weapon_confidence_threshold = 0.55
        self.weapon_seen_count = {}
        self.weapon_required_hits = 2

    # --------------------------------------------------
    # Public API
    # --------------------------------------------------

    def set_zones(self, zones):
        """
        Set restricted zones.

        Expected format:
        [
            {"name": "Main Gate", "box": (100, 100, 400, 400)},
            {"name": "Server Room", "box": (500, 200, 800, 500)}
        ]
        """

        self.zones = zones or []

    def process(self, tracked_objects, detections=None):
        """
        Main event processing function.

        tracked_objects input:
        [
            {"id": 1, "bbox": [x1, y1, x2, y2], "conf": 0.82}
        ]

        detections input:
        [
            {"bbox": [x1, y1, x2, y2], "conf": 0.82, "class": "person"}
        ]

        returns:
        [
            {
                "type": "INTRUSION",
                "severity": "HIGH",
                "message": "...",
                "object_id": 1,
                "zone": "Main Gate",
                "bbox": [...]
            }
        ]
        """

        events = []
        detections = detections or []
        tracked_objects = tracked_objects or []

        current_time = time.time()
        active_ids = set()

        zone_people_count = {}
        zone_people_ids = {}

        # --------------------------------------------------
        # 1. Person behavior logic
        # --------------------------------------------------

        for obj in tracked_objects:
            if not self.is_valid_track(obj):
                continue

            obj_id = obj["id"]
            bbox = self.normalize_bbox(obj["bbox"])
            track_conf = float(obj.get("conf", 0) or 0)

            active_ids.add(obj_id)
            self.last_seen_time[obj_id] = current_time

            center = self.get_center(bbox)
            current_zone = self.get_zone_for_point(center)

            if current_zone:
                zone_name = current_zone["name"]

                zone_people_count[zone_name] = zone_people_count.get(zone_name, 0) + 1
                zone_people_ids.setdefault(zone_name, []).append(obj_id)

                intrusion_event = self.check_intrusion(
                    obj_id=obj_id,
                    bbox=bbox,
                    zone_name=zone_name,
                    track_conf=track_conf,
                    current_time=current_time,
                )

                if intrusion_event:
                    events.append(intrusion_event)
            else:
                self.clear_intrusion_state_for_object(obj_id)

            loitering_event = self.check_loitering(
                obj_id=obj_id,
                bbox=bbox,
                center=center,
                current_zone=current_zone,
                track_conf=track_conf,
                current_time=current_time,
            )

            if loitering_event:
                events.append(loitering_event)

        # --------------------------------------------------
        # 2. Crowd logic
        # --------------------------------------------------

        crowd_events = self.check_crowd(
            tracked_objects=tracked_objects,
            zone_people_count=zone_people_count,
            zone_people_ids=zone_people_ids,
            current_time=current_time,
        )

        events.extend(crowd_events)

        # --------------------------------------------------
        # 3. Optional weapon hook
        # --------------------------------------------------

        if self.enable_weapon_detection:
            events.extend(self.check_weapon(detections))

        # --------------------------------------------------
        # 4. Cleanup
        # --------------------------------------------------

        self.cleanup_stale_tracks(active_ids, current_time)
        self.cleanup_old_alert_keys(current_time)

        # --------------------------------------------------
        # 5. Dispatch + return
        # --------------------------------------------------

        for event in events:
            self.alert.send(event)

        return events

    # --------------------------------------------------
    # Track validation
    # --------------------------------------------------

    def is_valid_track(self, obj):
        """
        Reject weak or malformed tracks before behavior logic.

        This reduces false behavior alerts caused by unstable detections.
        """

        if not obj or "bbox" not in obj or "id" not in obj:
            return False

        bbox = self.normalize_bbox(obj.get("bbox"))

        if not bbox:
            return False

        conf = float(obj.get("conf", 0) or 0)

        if conf < self.min_track_confidence:
            return False

        return True

    # --------------------------------------------------
    # Intrusion V3.1
    # --------------------------------------------------

    def check_intrusion(self, obj_id, bbox, zone_name, track_conf, current_time):
        """
        Intrusion rule:
        - Person center must remain inside a restricted zone.
        - Alert triggers only after intrusion_confirm_seconds.
        - Severity can escalate based on zone and duration.
        """

        intrusion_key = f"{obj_id}:{zone_name}"

        if intrusion_key not in self.intrusion_start_time:
            self.intrusion_start_time[intrusion_key] = current_time

        intrusion_duration = current_time - self.intrusion_start_time[intrusion_key]

        if intrusion_duration < self.intrusion_confirm_seconds:
            return None

        alert_key = f"INTRUSION:{obj_id}:{zone_name}"

        if not self.can_emit(alert_key):
            return None

        severity = self.get_zone_severity(zone_name, "intrusion", default="HIGH")

        if intrusion_duration >= self.intrusion_critical_seconds:
            severity = "CRITICAL"

        confidence = self.compute_behavior_confidence(
            duration=intrusion_duration,
            required_duration=self.intrusion_confirm_seconds,
            track_conf=track_conf,
        )

        return self.make_event(
            event_type="INTRUSION",
            severity=severity,
            object_id=obj_id,
            zone=zone_name,
            bbox=bbox,
            message=(
                f"Person {obj_id} remained inside restricted zone "
                f"{zone_name} for {intrusion_duration:.1f} seconds"
            ),
            extra={
                "duration_seconds": round(intrusion_duration, 1),
                "confidence": confidence,
                "track_confidence": round(track_conf, 3),
                "rule": "intrusion_duration_v3_1",
            },
        )

    # --------------------------------------------------
    # Loitering V3.1
    # --------------------------------------------------

    def check_loitering(
        self,
        obj_id,
        bbox,
        center,
        current_zone,
        track_conf,
        current_time,
    ):
        """
        Loitering rule:
        - Person must stay near the same anchor location.
        - Big movement resets the timer.
        - Small bbox jitter is tolerated.
        - Severity can escalate based on duration and zone.
        """

        if obj_id not in self.loiter_anchor_position:
            self.loiter_anchor_position[obj_id] = center
            self.loiter_last_position[obj_id] = center
            self.loiter_start_time[obj_id] = current_time
            return None

        anchor = self.loiter_anchor_position[obj_id]
        last_position = self.loiter_last_position.get(obj_id, center)

        distance_from_anchor = self.distance(anchor, center)
        frame_to_frame_distance = self.distance(last_position, center)

        self.loiter_last_position[obj_id] = center

        # Clear movement away from area resets loitering timer.
        if distance_from_anchor > self.loiter_movement_threshold:
            self.loiter_anchor_position[obj_id] = center
            self.loiter_start_time[obj_id] = current_time
            return None

        # Small movement is treated as normal camera/detection jitter.
        # No timer reset needed.
        if frame_to_frame_distance <= self.loiter_jitter_threshold:
            pass

        loiter_duration = current_time - self.loiter_start_time[obj_id]

        if loiter_duration < self.loiter_seconds:
            return None

        zone_name = current_zone["name"] if current_zone else "Camera View"
        alert_key = f"LOITERING:{obj_id}:{zone_name}"

        if not self.can_emit(alert_key):
            return None

        severity = self.get_zone_severity(zone_name, "loitering", default="MEDIUM")

        if loiter_duration >= self.loiter_high_seconds:
            severity = "HIGH"

        confidence = self.compute_behavior_confidence(
            duration=loiter_duration,
            required_duration=self.loiter_seconds,
            track_conf=track_conf,
        )

        return self.make_event(
            event_type="LOITERING",
            severity=severity,
            object_id=obj_id,
            zone=zone_name,
            bbox=bbox,
            message=(
                f"Person {obj_id} stayed near the same location for "
                f"{int(loiter_duration)} seconds"
            ),
            extra={
                "duration_seconds": int(loiter_duration),
                "movement_distance": round(distance_from_anchor, 2),
                "confidence": confidence,
                "track_confidence": round(track_conf, 3),
                "rule": "loitering_stationary_v3_1",
            },
        )

    # --------------------------------------------------
    # Crowd V3.1
    # --------------------------------------------------

    def check_crowd(
        self,
        tracked_objects,
        zone_people_count,
        zone_people_ids,
        current_time,
    ):
        """
        Crowd rule:
        - Crowd detection is zone-based if zones exist.
        - Otherwise it falls back to the full camera view.
        - Count must remain above threshold for crowd_confirm_seconds.
        - Severity escalates for higher count or longer crowd duration.
        """

        events = []

        if self.zones:
            for zone in self.zones:
                zone_name = zone["name"]
                count = zone_people_count.get(zone_name, 0)

                event = self.check_crowd_for_area(
                    area_name=zone_name,
                    count=count,
                    object_ids=zone_people_ids.get(zone_name, []),
                    current_time=current_time,
                )

                if event:
                    events.append(event)
        else:
            valid_tracks = [obj for obj in tracked_objects if self.is_valid_track(obj)]
            total_count = len(valid_tracks)

            event = self.check_crowd_for_area(
                area_name="Camera View",
                count=total_count,
                object_ids=[obj.get("id") for obj in valid_tracks if "id" in obj],
                current_time=current_time,
            )

            if event:
                events.append(event)

        return events

    def check_crowd_for_area(self, area_name, count, object_ids, current_time):
        """
        Crowd detection for a single area.
        """

        if count < self.crowd_threshold:
            self.crowd_start_time.pop(area_name, None)
            self.crowd_last_count.pop(area_name, None)
            return None

        if area_name not in self.crowd_start_time:
            self.crowd_start_time[area_name] = current_time

        self.crowd_last_count[area_name] = count

        crowd_duration = current_time - self.crowd_start_time[area_name]

        if crowd_duration < self.crowd_confirm_seconds:
            return None

        alert_key = f"CROWD_ALERT:{area_name}"

        if not self.can_emit(alert_key):
            return None

        severity = self.get_zone_severity(area_name, "crowd", default="HIGH")

        if (
            count >= self.crowd_critical_threshold
            or crowd_duration >= self.crowd_critical_seconds
        ):
            severity = "CRITICAL"

        confidence = self.compute_crowd_confidence(
            count=count,
            duration=crowd_duration,
        )

        return self.make_event(
            event_type="CROWD_ALERT",
            severity=severity,
            zone=area_name,
            message=(
                f"{count} people remained inside {area_name} "
                f"for {crowd_duration:.1f} seconds"
            ),
            extra={
                "person_count": count,
                "object_ids": object_ids,
                "duration_seconds": round(crowd_duration, 1),
                "confidence": confidence,
                "rule": "crowd_duration_v3_1",
            },
        )

    # --------------------------------------------------
    # Weapon hook — disabled by default
    # --------------------------------------------------

    def check_weapon(self, detections):
        """
        Optional weapon hook.

        Disabled by default in final MVP because YOLOv8n is not a reliable
        weapon detector. This function is kept only for future custom model use.
        """

        events = []

        for det in detections:
            cls = det.get("class", "").lower()
            conf = float(det.get("conf", 0) or 0)

            if cls not in self.weapon_classes:
                continue

            if conf < self.weapon_confidence_threshold:
                continue

            bbox = self.normalize_bbox(det.get("bbox", []))

            if not bbox:
                continue

            weapon_key = f"{cls}:{bbox}"

            self.weapon_seen_count[weapon_key] = (
                self.weapon_seen_count.get(weapon_key, 0) + 1
            )

            if self.weapon_seen_count[weapon_key] < self.weapon_required_hits:
                continue

            alert_key = f"WEAPON_DETECTED:{cls}"

            if not self.can_emit(alert_key):
                continue

            events.append(
                self.make_event(
                    event_type="WEAPON_DETECTED",
                    severity="CRITICAL",
                    bbox=bbox,
                    message=f"Potential weapon detected: {cls} ({conf:.2f})",
                    extra={
                        "class": cls,
                        "confidence": round(conf, 3),
                        "rule": "weapon_confidence_multiframe_hook_v3_1",
                    },
                )
            )

        if len(self.weapon_seen_count) > 100:
            self.weapon_seen_count.clear()

        return events

    # --------------------------------------------------
    # Severity / confidence helpers
    # --------------------------------------------------

    def get_zone_severity(self, zone_name, event_kind, default):
        """
        Return configured severity for a zone/event kind if available.
        """

        zone_rules = self.zone_severity_overrides.get(zone_name, {})

        return zone_rules.get(event_kind, default)

    def compute_behavior_confidence(self, duration, required_duration, track_conf):
        """
        Compute confidence based on:
        - how long the behavior continued
        - track confidence from detector/tracker

        Result is capped between 0.0 and 1.0.
        """

        if required_duration <= 0:
            duration_score = 1.0
        else:
            duration_score = min(1.0, duration / max(required_duration * 2, 0.01))

        combined = (duration_score * 0.6) + (track_conf * 0.4)

        return round(max(0.0, min(1.0, combined)), 3)

    def compute_crowd_confidence(self, count, duration):
        """
        Compute crowd confidence based on count and duration.
        """

        count_score = min(1.0, count / max(self.crowd_critical_threshold, 1))
        duration_score = min(1.0, duration / max(self.crowd_confirm_seconds * 2, 0.01))

        combined = (count_score * 0.55) + (duration_score * 0.45)

        return round(max(0.0, min(1.0, combined)), 3)

    # --------------------------------------------------
    # Core utility helpers
    # --------------------------------------------------

    def can_emit(self, key):
        """
        Cooldown check for repeated alerts.
        """

        now = time.time()
        last_time = self.last_alert_time.get(key, 0)

        if now - last_time >= self.cooldown_seconds:
            self.last_alert_time[key] = now
            return True

        return False

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
        """
        Create backend/dashboard-compatible event object.
        """

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

    def normalize_bbox(self, bbox):
        """
        Ensure bbox is a list of four integers.
        """

        if not bbox or len(bbox) != 4:
            return []

        return [int(v) for v in bbox]

    def get_center(self, bbox):
        """
        Return bbox center point.
        """

        x1, y1, x2, y2 = bbox

        cx = int((x1 + x2) / 2)
        cy = int((y1 + y2) / 2)

        return cx, cy

    def distance(self, p1, p2):
        """
        Euclidean distance between two points.
        """

        x1, y1 = p1
        x2, y2 = p2

        return ((x1 - x2) ** 2 + (y1 - y2) ** 2) ** 0.5

    def is_point_inside_zone(self, point, zone):
        """
        Check if point is inside a zone box.
        """

        cx, cy = point
        zx1, zy1, zx2, zy2 = zone["box"]

        return zx1 <= cx <= zx2 and zy1 <= cy <= zy2

    def get_zone_for_point(self, point):
        """
        Return the first zone containing the point.
        """

        for zone in self.zones:
            if self.is_point_inside_zone(point, zone):
                return zone

        return None

    def clear_intrusion_state_for_object(self, obj_id):
        """
        Clear intrusion timers for a person after leaving all zones.
        """

        for key in list(self.intrusion_start_time.keys()):
            if key.startswith(f"{obj_id}:"):
                self.intrusion_start_time.pop(key, None)

    def cleanup_stale_tracks(self, active_ids, current_time):
        """
        Remove old track memory for disappeared objects.
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
            self.loiter_last_position.pop(obj_id, None)

            self.clear_intrusion_state_for_object(obj_id)

    def cleanup_old_alert_keys(self, current_time):
        """
        Prevent cooldown dictionary from growing forever.
        """

        stale_keys = []

        for key, last_time in self.last_alert_time.items():
            if current_time - last_time > self.track_stale_seconds * 3:
                stale_keys.append(key)

        for key in stale_keys:
            self.last_alert_time.pop(key, None)
