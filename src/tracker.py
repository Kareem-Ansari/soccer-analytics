# ByteTrack wrapper for persistent player tracking

import supervision as sv


class SoccerTracker:
    """
    Wraps supervision ByteTrack.
    Maintains state across frames for one video clip.
    Reset between clips by creating a new instance.
    """

    def __init__(self, track_thresh=0.35, min_hits=3, max_age=30):
        self.tracker = sv.ByteTrack(
            track_thresh=track_thresh,
            track_buffer=min_hits,
        )

    def update(self, detections):
        """
        Update tracker with new detections.

        Args:
            detections: supervision Detections from detector.py

        Returns:
            supervision Detections with tracker_id field populated
        """
        return self.tracker.update_with_detections(detections)

    def reset(self):
        """Reset tracker state. Call between clips."""
        self.tracker.reset()