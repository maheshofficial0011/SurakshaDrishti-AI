# 🟢 CHANGED: Fast CPU-stable detector
# REASON: YOLO-World is too slow on CPU, so weapon model is optional/off by default

import torch
from ultralytics import YOLO, YOLOWorld


class Detector:
    """
    Unified detector for SurakshaNet AI.

    Current fast mode:
    - YOLOv8n handles person/general object detection.
    - YOLO-World weapon detection is disabled by default for CPU performance.
    - PPE logic is excluded.
    """

    def __init__(self):
        self.device = "cuda:0" if torch.cuda.is_available() else "cpu"
        self.use_half = self.device.startswith("cuda")

        print(f"🚀 Detector running on: {self.device}")

        self.general_model_path = "yolov8n.pt"
        self.general_conf = 0.35

        self.general_model = YOLO(self.general_model_path)
        self.general_model.to(self.device)

        self.weapon_classes = [
            "gun",
            "handgun",
            "pistol",
            "rifle",
            "knife",
            "weapon",
        ]

        self.weapon_conf = 0.25

        # Keep False for smooth CPU demo.
        # Set True only if CUDA GPU is working or you want to test weapon scan.
        self.weapon_enabled = False
        self.weapon_model = None

        if self.weapon_enabled:
            try:
                self.weapon_model = YOLOWorld("yolov8s-world.pt")
                self.weapon_model.to(self.device)
                self.weapon_model.set_classes(self.weapon_classes)

                print("🔫 YOLO-World weapon prompts active:", self.weapon_classes)

            except Exception as e:
                self.weapon_enabled = False
                self.weapon_model = None
                print("⚠ YOLO-World weapon model disabled:", e)
        else:
            print("⚡ Weapon detection disabled for smooth CPU performance")

    def _predict(self, model, frame, conf):
        return model.predict(
            frame,
            device=self.device,
            verbose=False,
            half=self.use_half,
            conf=conf,
            iou=0.45,
            imgsz=640,
        )[0]

    def _parse(self, result, label_source):
        detections = []

        for box in result.boxes:
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            conf = float(box.conf[0])
            cls_id = int(box.cls[0])
            cls_name = result.names[cls_id]

            detections.append(
                {
                    "bbox": [x1, y1, x2, y2],
                    "conf": conf,
                    "class": cls_name,
                    "source": label_source,
                }
            )

        return detections

    def detect(self, frame):
        detections = []

        general_result = self._predict(
            self.general_model,
            frame,
            conf=self.general_conf,
        )

        detections += self._parse(general_result, "general")

        if self.weapon_enabled and self.weapon_model is not None:
            weapon_result = self._predict(
                self.weapon_model,
                frame,
                conf=self.weapon_conf,
            )

            weapon_detections = self._parse(weapon_result, "weapon_world")

            for det in weapon_detections:
                cls = det.get("class", "").lower()
                conf = float(det.get("conf", 0) or 0)

                if cls in self.weapon_classes and conf >= self.weapon_conf:
                    detections.append(det)

        return detections
