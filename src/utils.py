# Shared utility functions used across all modules

import os
import yaml
import cv2
import numpy as np


def load_config(config_path="configs/config.yaml"):
    """Load config.yaml and return as dict."""
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Config not found: {config_path}")
    with open(config_path, "r") as f:
        return yaml.safe_load(f)


def get_video_metadata(video_path):
    """Return dict of video properties."""
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise IOError(f"Cannot open video: {video_path}")
    meta = {
        "width"    : int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
        "height"   : int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)),
        "fps"      : cap.get(cv2.CAP_PROP_FPS),
        "frames"   : int(cap.get(cv2.CAP_PROP_FRAME_COUNT)),
        "duration" : (int(cap.get(cv2.CAP_PROP_FRAME_COUNT)) /
                      cap.get(cv2.CAP_PROP_FPS)),
    }
    cap.release()
    return meta


def make_video_writer(output_path, fps, width, height):
    """Create and return a cv2 VideoWriter."""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    return cv2.VideoWriter(output_path, fourcc, fps, (width, height))


def clamp(value, min_val=0.0, max_val=1.0):
    """Clamp a float to [min_val, max_val]."""
    return max(min_val, min(max_val, value))


def mot_row_to_yolo(row, img_w, img_h):
    """
    Convert one MOT CSV row to YOLO normalized format.

    MOT row: frame_id, track_id, x_tl, y_tl, w, h, conf, -1, -1, -1
    YOLO   : class_id cx cy nw nh  (all normalized 0-1)
    """
    x  = float(row[2])
    y  = float(row[3])
    w  = float(row[4])
    h  = float(row[5])
    cx = clamp((x + w / 2) / img_w)
    cy = clamp((y + h / 2) / img_h)
    nw = clamp(w / img_w)
    nh = clamp(h / img_h)
    return cx, cy, nw, nh


def compute_iou(box_a, box_b):
    """
    Compute IoU between two boxes in xyxy format.
    Both boxes: [x1, y1, x2, y2]
    """
    xa1 = max(box_a[0], box_b[0])
    ya1 = max(box_a[1], box_b[1])
    xa2 = min(box_a[2], box_b[2])
    ya2 = min(box_a[3], box_b[3])

    inter_w = max(0.0, xa2 - xa1)
    inter_h = max(0.0, ya2 - ya1)
    inter   = inter_w * inter_h

    area_a = (box_a[2] - box_a[0]) * (box_a[3] - box_a[1])
    area_b = (box_b[2] - box_b[0]) * (box_b[3] - box_b[1])
    union  = area_a + area_b - inter

    return inter / union if union > 0 else 0.0