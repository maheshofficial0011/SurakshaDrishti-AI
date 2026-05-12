import cv2
import os
import sys

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.append(PROJECT_ROOT)

from ai_engine.inference.detector import Detector

detector = Detector()

cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("camera not opened")
    raise SystemExit

for i in range(20):
    ret, frame = cap.read()

    if not ret or frame is None:
        print("no frame")
        continue

    frame = cv2.resize(frame, (640, 480))
    detections = detector.detect(frame)

    print(f"frame={i} detections={len(detections)}")

    for det in detections[:10]:
        print(det)

cap.release()