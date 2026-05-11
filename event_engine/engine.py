from alert_system.dispatcher import AlertDispatcher
import time


class EventEngine:
    """
    Central intelligence brain of SurakshaNet AI

    Handles:
    - Intrusion detection
    - Loitering detection
    - Crowd alert
    - Weapon detection hook
    - PPE violation hook
    - Alert cooldown
    """

    def __init__(self):
        self.zones = []
        self.alert = AlertDispatcher()

        # 🟢 CHANGED: Cooldown memory
        # REASON: Prevent repeated same alerts every frame
        self.cooldown_seconds = 5
        self.last_alert_time = {}

        # 🟢 CHANGED: Loitering memory
        # REASON: Track how long a person stays in nearly same area
        self.loiter_start_time = {}
        self.last_positions = {}

        # 🟢 CHANGED: Behavior thresholds
        # REASON: Centralized tuning values
        self.loiter_seconds = 10
        self.loiter_movement_threshold = 60
        self.crowd_threshold = 3

    def set_zones(self, zones):
        self.zones = zones

    def can_emit(self, key):
        now = time.time()
        last_time = self.last_alert_time.get(key, 0)

        if now - last_time >= self.cooldown_seconds:
            self.last_alert_time[key] = now
            return True

        return False

    def get_center(self, bbox):
        x1, y1, x2, y2 = bbox

        cx = (x1 + x2) // 2
        cy = (y1 + y2) // 2

        return cx, cy

    def distance(self, p1, p2):
        x1, y1 = p1
        x2, y2 = p2

        return ((x1 - x2) ** 2 + (y1 - y2) ** 2) ** 0.5

    def process(self, tracked_objects, detections=None):
        events = []

        current_time = time.time()

        # -----------------------------
        # 1. CROWD ALERT
        # -----------------------------

        person_count = len(tracked_objects)

        if person_count >= self.crowd_threshold:
            key = "CROWD_ALERT"

            if self.can_emit(key):
                events.append(
                    {
                        "type": "CROWD_ALERT",
                        "severity": "MEDIUM",
                        "person_count": person_count,
                        "message": f"{person_count} persons detected in camera view",
                    }
                )

        # -----------------------------
        # 2. PERSON BEHAVIOR RULES
        # -----------------------------

        for obj in tracked_objects:

            if not obj or "bbox" not in obj or "id" not in obj:
                continue

            x1, y1, x2, y2 = obj["bbox"]
            obj_id = obj["id"]
            bbox = [x1, y1, x2, y2]

            cx, cy = self.get_center(bbox)
            current_position = (cx, cy)

            # -----------------------------
            # 2A. INTRUSION DETECTION
            # -----------------------------

            for zone in self.zones:
                zx1, zy1, zx2, zy2 = zone["box"]

                if zx1 < cx < zx2 and zy1 < cy < zy2:
                    key = f"INTRUSION:{obj_id}:{zone['name']}"

                    if self.can_emit(key):
                        events.append(
                            {
                                "type": "INTRUSION",
                                "severity": "HIGH",
                                "object_id": obj_id,
                                "zone": zone["name"],
                                "bbox": bbox,
                                "message": f"Person {obj_id} entered restricted zone: {zone['name']}",
                            }
                        )

            # -----------------------------
            # 2B. LOITERING DETECTION
            # -----------------------------

            if obj_id not in self.last_positions:
                self.last_positions[obj_id] = current_position
                self.loiter_start_time[obj_id] = current_time

            else:
                last_position = self.last_positions[obj_id]
                move_distance = self.distance(last_position, current_position)

                # If person moved far, reset loitering timer
                if move_distance > self.loiter_movement_threshold:
                    self.last_positions[obj_id] = current_position
                    self.loiter_start_time[obj_id] = current_time

                else:
                    duration = current_time - self.loiter_start_time[obj_id]

                    if duration >= self.loiter_seconds:
                        key = f"LOITERING:{obj_id}"

                        if self.can_emit(key):
                            events.append(
                                {
                                    "type": "LOITERING",
                                    "severity": "MEDIUM",
                                    "object_id": obj_id,
                                    "duration_seconds": int(duration),
                                    "bbox": bbox,
                                    "message": f"Person {obj_id} is loitering for {int(duration)} seconds",
                                }
                            )

        # -----------------------------
        # 3. WEAPON DETECTION HOOK
        # -----------------------------

        if detections:
            for det in detections:
                cls = det.get("class", "").lower()

                if cls in ["knife", "gun", "weapon"]:
                    key = f"WEAPON:{cls}"

                    if self.can_emit(key):
                        events.append(
                            {
                                "type": "WEAPON_DETECTED",
                                "severity": "CRITICAL",
                                "confidence": det.get("conf", 0),
                                "class": cls,
                                "bbox": det.get("bbox", []),
                                "message": f"Potential weapon detected: {cls}",
                            }
                        )

        # -----------------------------
        # 4. PPE VIOLATION HOOK
        # -----------------------------

        if detections:
            for det in detections:
                cls = det.get("class", "").lower()

                if cls in ["no_helmet", "no_vest"]:
                    key = f"PPE:{cls}"

                    if self.can_emit(key):
                        events.append(
                            {
                                "type": "PPE_VIOLATION",
                                "severity": "MEDIUM",
                                "class": cls,
                                "bbox": det.get("bbox", []),
                                "message": f"PPE violation detected: {cls}",
                            }
                        )

        # -----------------------------
        # 5. ALERT DISPATCH
        # -----------------------------

        for event in events:
            self.alert.send(event)

        return events
