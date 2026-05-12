"""
SurakshaDrishti AI — Final MVP Detector

Purpose:
- Load YOLOv8n for person/general object detection.
- Run fast CPU-stable inference for the live surveillance pipeline.
- Keep optional YOLO-World weapon detection as a future hook only.
- Exclude PPE logic from the final MVP.

Final MVP decision:
- YOLOv8n is used for live detection.
- YOLO-World is disabled by default because it is too slow on CPU.
- Weapon detection is not treated as production-ready without a custom model.
- PPE detection is intentionally excluded.
"""

import torch
from ultralytics import YOLO

# YOLOWorld is optional. Import only when needed so normal CPU mode stays light.
try:
    from ultralytics import YOLOWorld
except Exception:
    YOLOWorld = None


# ---------------------------------------------------------------------
# Optional clean terminal helpers
# ---------------------------------------------------------------------
# The detector can run even if utils.terminal is unavailable.
# This keeps the file reusable and avoids import crashes.

try:
    from utils.terminal import print_ok, print_info, print_warn
except Exception:

    def print_ok(message):
        print(f"[OK] {message}")

    def print_info(message):
        print(f"[INFO] {message}")

    def print_warn(message):
        print(f"[WARN] {message}")


class Detector:
    """
    Unified detector for SurakshaDrishti AI.

    Current final MVP mode:
    - Uses YOLOv8n for person/general object detection.
    - Runs on CUDA if available, otherwise CPU.
    - Uses half precision only on CUDA.
    - Keeps YOLO-World weapon detection disabled by default.
    - Does not include PPE detection.

    Output format:
    [
        {
            "bbox": [x1, y1, x2, y2],
            "conf": 0.82,
            "class": "person",
            "source": "general"
        }
    ]
    """

    def __init__(self):
        # --------------------------------------------------
        # Device selection
        # --------------------------------------------------
        # If CUDA PyTorch is installed and available, YOLO inference uses GPU.
        # Otherwise it safely falls back to CPU.

        self.device = "cuda:0" if torch.cuda.is_available() else "cpu"
        self.use_half = self.device.startswith("cuda")

        # --------------------------------------------------
        # General detection model
        # --------------------------------------------------
        # YOLOv8n is small and suitable for CPU-friendly local demo.

        self.general_model_path = "yolov8n.pt"
        self.general_conf = 0.35
        self.general_iou = 0.45
        self.image_size = 640

        self.general_model = YOLO(self.general_model_path)
        self.general_model.to(self.device)

        print_ok(f"Detector initialized on {self.device}")
        print_info(f"General model: {self.general_model_path}")

        # --------------------------------------------------
        # Optional weapon detection hook
        # --------------------------------------------------
        # Disabled for final MVP.
        # Enable only if:
        # - CUDA is available, or
        # - you accept slower CPU performance, or
        # - you replace this with a small custom weapon model.

        self.weapon_enabled = False
        self.weapon_model = None
        self.weapon_conf = 0.25

        self.weapon_classes = [
            "gun",
            "handgun",
            "pistol",
            "rifle",
            "knife",
            "weapon",
        ]

        self._load_optional_weapon_model()

    # -----------------------------------------------------------------
    # Optional model loading
    # -----------------------------------------------------------------

    def _load_optional_weapon_model(self):
        """
        Load YOLO-World only if weapon detection is explicitly enabled.

        In final MVP mode this function keeps weapon detection disabled.
        This avoids slow CPU inference and prevents fake weapon detection.
        """

        if not self.weapon_enabled:
            print_info("Weapon detection disabled for smooth CPU performance")
            return

        if YOLOWorld is None:
            self.weapon_enabled = False
            self.weapon_model = None
            print_warn("YOLOWorld is not available. Weapon detection disabled.")
            return

        try:
            self.weapon_model = YOLOWorld("yolov8s-world.pt")
            self.weapon_model.to(self.device)
            self.weapon_model.set_classes(self.weapon_classes)

            print_ok("YOLO-World weapon prompts loaded")
            print_info(f"Weapon prompts: {self.weapon_classes}")

        except Exception as exc:
            self.weapon_enabled = False
            self.weapon_model = None
            print_warn(f"YOLO-World weapon model disabled: {exc}")

    # -----------------------------------------------------------------
    # Prediction helpers
    # -----------------------------------------------------------------

    def _predict(self, model, frame, conf):
        """
        Run model prediction with stable settings.

        Parameters:
            model: Ultralytics YOLO model
            frame: OpenCV BGR frame
            conf: confidence threshold

        Returns:
            Ultralytics prediction result for one frame.
        """

        return model.predict(
            frame,
            device=self.device,
            verbose=False,
            half=self.use_half,
            conf=conf,
            iou=self.general_iou,
            imgsz=self.image_size,
        )[0]

    def _parse(self, result, label_source):
        """
        Convert Ultralytics result into SurakshaNet detection format.

        Output format:
        {
            "bbox": [x1, y1, x2, y2],
            "conf": float,
            "class": class_name,
            "source": label_source
        }
        """

        detections = []

        if result is None or result.boxes is None:
            return detections

        for box in result.boxes:
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            conf = float(box.conf[0])
            cls_id = int(box.cls[0])
            cls_name = result.names.get(cls_id, str(cls_id))

            detections.append(
                {
                    "bbox": [x1, y1, x2, y2],
                    "conf": conf,
                    "class": cls_name,
                    "source": label_source,
                }
            )

        return detections

    # -----------------------------------------------------------------
    # Public detection API
    # -----------------------------------------------------------------

    def detect(self, frame):
        """
        Run detection on a single frame.

        Final MVP behavior:
        - Always runs YOLOv8n general detection.
        - Optionally runs YOLO-World weapon detection only if enabled.
        - Returns one unified list of detections.

        This method should not print every frame.
        The tracking pipeline handles clean runtime logging.
        """

        if frame is None:
            return []

        detections = []

        # --------------------------------------------------
        # 1. General/person detection
        # --------------------------------------------------

        general_result = self._predict(
            self.general_model,
            frame,
            conf=self.general_conf,
        )

        detections.extend(self._parse(general_result, "general"))

        # --------------------------------------------------
        # 2. Optional weapon detection hook
        # --------------------------------------------------
        # Disabled by default for smooth final MVP mode.

        if self.weapon_enabled and self.weapon_model is not None:
            weapon_result = self._predict(
                self.weapon_model,
                frame,
                conf=self.weapon_conf,
            )

            weapon_detections = self._parse(weapon_result, "weapon_world")

            for det in weapon_detections:
                cls_name = det.get("class", "").lower()
                conf = float(det.get("conf", 0) or 0)

                if cls_name in self.weapon_classes and conf >= self.weapon_conf:
                    detections.append(det)

        return detections
