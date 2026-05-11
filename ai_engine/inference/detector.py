from ultralytics import YOLO

class Detector:
    def __init__(self):
        # Load all models (you can swap paths later)
        # 🟢 CHANGED: Using pretrained YOLOv8 default model
        # REASON: Fix corrupted .pt files and stabilize Phase 5 pipeline

         self.person_model = YOLO("yolov8n.pt")
         self.weapon_model = YOLO("yolov8n.pt")
         self.ppe_model = YOLO("yolov8n.pt")

    def detect(self, frame):
        results = []

        # PERSON / GENERAL OBJECTS
        person_res = self.person_model(frame)[0]

        # WEAPON DETECTION
        weapon_res = self.weapon_model(frame)[0]

        # PPE DETECTION
        ppe_res = self.ppe_model(frame)[0]

        # Convert outputs into unified format
        def parse(res, label_source):
            detections = []
            for box in res.boxes:
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                conf = float(box.conf[0])
                cls_id = int(box.cls[0])
                cls_name = res.names[cls_id]

                detections.append({
                    "bbox": [x1, y1, x2, y2],
                    "conf": conf,
                    "class": cls_name,
                    "source": label_source
                })
            return detections

        results += parse(person_res, "person")
        results += parse(weapon_res, "weapon")
        results += parse(ppe_res, "ppe")

        return results