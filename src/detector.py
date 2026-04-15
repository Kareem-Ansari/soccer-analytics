# YOLO11 detection wrapper

import os
import cv2
import numpy as np
from ultralytics import YOLO


class SoccerDetector:
    """
    Wraps YOLO11 for soccer player detection.
    Loads model once, exposes a detect() method per frame.
    """

    def __init__(self, weights_path, confidence=0.35, input_size=1280):
        if not os.path.exists(weights_path):
            raise FileNotFoundError(
                f"Weights not found: {weights_path}"
            )
        self.model      = YOLO(weights_path)
        self.confidence = confidence
        self.input_size = input_size
        self.class_names = self.model.names

    def detect(self, frame):
        """
        Run detection on a single BGR frame.

        Returns:
            supervision Detections object (empty if nothing found)
        """
        import supervision as sv

        results    = self.model(
            frame,
            verbose=False,
            conf=self.confidence,
            imgsz=self.input_size,
        )[0]
        detections = sv.Detections.from_ultralytics(results)
        return detections

    def detect_batch(self, frames):
        """
        Run detection on a list of frames.
        Returns list of supervision Detections objects.
        """
        import supervision as sv

        results_list = self.model(
            frames,
            verbose=False,
            conf=self.confidence,
            imgsz=self.input_size,
        )
        return [sv.Detections.from_ultralytics(r) for r in results_list]