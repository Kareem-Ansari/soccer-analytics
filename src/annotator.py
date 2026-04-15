# Frame annotation: boxes, trails, labels, stats overlay

import cv2
import numpy as np
from collections import Counter
import supervision as sv


class SoccerAnnotator:
    """
    Draws bounding boxes, labels, movement trails,
    and a stats overlay panel on frames.
    """

    def __init__(self, trace_length=50):
        self.box_annotator = sv.BoxAnnotator(thickness=2)

        self.label_annotator = sv.LabelAnnotator(
            text_scale=0.4,
            text_thickness=1,
            text_padding=3
        )

        self.trail_annotator = sv.TraceAnnotator(
            thickness=2,
            trace_length=trace_length,
            position=sv.Position.BOTTOM_CENTER
        )

    def build_labels(self, detections, class_names):
        """Build label strings for each detection."""
        if detections.tracker_id is None or len(detections) == 0:
            return []
        return [
            f"{class_names[c]} #{tid}"
            for c, tid in zip(
                detections.class_id,
                detections.tracker_id
            )
        ]

    def draw_stats_panel(self, frame, detections, class_names,
                         frame_id=None, total_frames=None):
        """Draw semi-transparent stats panel in top-left corner."""
        if detections.tracker_id is None or len(detections) == 0:
            return frame

        counts  = Counter(class_names[c] for c in detections.class_id)
        n_rows  = len(counts) + (1 if frame_id is not None else 0)
        panel_h = 44 + (n_rows * 22)

        overlay = frame.copy()
        cv2.rectangle(overlay, (8, 8), (230, panel_h), (0, 0, 0), -1)
        cv2.addWeighted(overlay, 0.55, frame, 0.45, 0, frame)

        cv2.putText(
            frame, "SoccerNet Tracking",
            (14, 30), cv2.FONT_HERSHEY_SIMPLEX,
            0.55, (255, 255, 255), 2
        )

        y = 50
        if frame_id is not None and total_frames is not None:
            progress = frame_id / total_frames if total_frames > 0 else 0
            cv2.putText(
                frame,
                f"Frame {frame_id}/{total_frames} ({progress:.0%})",
                (14, y), cv2.FONT_HERSHEY_SIMPLEX,
                0.38, (180, 180, 180), 1
            )
            y += 22

        for name, count in sorted(counts.items()):
            cv2.putText(
                frame, f"{name}: {count}",
                (14, y), cv2.FONT_HERSHEY_SIMPLEX,
                0.45, (200, 200, 200), 1
            )
            y += 22

        return frame

    def annotate(self, frame, detections, class_names,
                 frame_id=None, total_frames=None):
        """
        Full annotation pipeline on a single frame.

        Args:
            frame        : BGR numpy array
            detections   : supervision Detections with tracker_id
            class_names  : dict of {class_id: name}
            frame_id     : optional int for progress display
            total_frames : optional int for progress display

        Returns:
            Annotated BGR numpy array
        """
        labels    = self.build_labels(detections, class_names)
        annotated = frame.copy()
        annotated = self.trail_annotator.annotate(annotated, detections)
        annotated = self.box_annotator.annotate(annotated, detections)
        annotated = self.label_annotator.annotate(
                        annotated, detections, labels)
        annotated = self.draw_stats_panel(
                        annotated, detections, class_names,
                        frame_id, total_frames)
        return annotated