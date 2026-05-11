# 🟢 CHANGED: GPU-aware optimized detector
# REASON: Use CUDA when available and avoid running the same YOLO model 3 times unnecessarily

import torch
from ultralytics import YOLO


class Detector:
    """
    Unified detector for SurakshaNet AI.

    Current setup:
    - Uses YOLOv8n pretrained model for person/general object detection.
    - Weapon and PPE are kept as logical hooks for future custom models.
    - If weapon/PPE model paths are same as person model, inference runs only once.
    """

    def __init__(self):
        # 🟢 CHANGED: Select GPU if available
        # REASON: Move YOLO inference to GPU when CUDA PyTorch is installed

        self.device = "cuda:0" if torch.cuda.is_available() else "cpu"
        self.use_half = self.device.startswith("cuda")

        print(f"🚀 Detector running on: {self.device}")

        # 🟢 CHANGED: Centralized model paths
        # REASON: Easy future replacement with real weapon/PPE models

        self.person_model_path = "yolov8n.pt"
        self.weapon_model_path = "yolov8n.pt"
        self.ppe_model_path = "yolov8n.pt"

        # 🟢 CHANGED: Load main YOLO model once
        # REASON: Running yolov8n three times caused major lag

        self.person_model = YOLO(self.person_model_path)
        self.person_model.to(self.device)

        # 🟢 CHANGED: Avoid duplicate model loading if same weights are used
        # REASON: Weapon/PPE are currently hooks using same model, so reuse model

        if self.weapon_model_path == self.person_model_path:
            self.weapon_model = self.person_model
        else:
            self.weapon_model = YOLO(self.weapon_model_path)
            self.weapon_model.to(self.device)

        if self.ppe_model_path == self.person_model_path:
            self.ppe_model = self.person_model
        else:
            self.ppe_model = YOLO(self.ppe_model_path)
            self.ppe_model.to(self.device)

    def _predict(self, model, frame):
        # 🟢 CHANGED: Use explicit predict with device + half precision on CUDA
        # REASON: Ensures Ultralytics uses GPU when available

        return model.predict(
            frame,
            device=self.device,
            verbose=False,
            half=self.use_half,
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
        results = []

        # 🟢 CHANGED: Run main model once when all paths are same
        # REASON: Huge performance improvement for current demo setup

        if (
            self.person_model_path == self.weapon_model_path
            and self.person_model_path == self.ppe_model_path
        ):
            general_result = self._predict(self.person_model, frame)

            # Current pretrained YOLO gives real COCO classes such as:
            # person, car, chair, bottle, cell phone, etc.
            results += self._parse(general_result, "general")

            return results

        # PERSON / GENERAL OBJECTS
        person_res = self._predict(self.person_model, frame)
        results += self._parse(person_res, "person")

        # WEAPON DETECTION HOOK
        weapon_res = self._predict(self.weapon_model, frame)
        results += self._parse(weapon_res, "weapon")

        # PPE DETECTION HOOK
        ppe_res = self._predict(self.ppe_model, frame)
        results += self._parse(ppe_res, "ppe")

        return results
