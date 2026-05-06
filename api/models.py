# Pydantic response models for all API endpoints
# Defines the shape of every JSON response the API returns

from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class HealthResponse(BaseModel):
    status: str
    database: str
    version: str


class TrackingRun(BaseModel):
    run_id: int
    sequence_name: str
    started_at: datetime
    total_frames: Optional[int]
    model_name: Optional[str]
    confidence_thresh: Optional[float]
    notes: Optional[str]


class RunsResponse(BaseModel):
    total: int
    runs: list[TrackingRun]


class Detection(BaseModel):
    id: int
    frame_id: int
    track_id: Optional[int]
    class_name: Optional[str]
    confidence: Optional[float]
    x1: Optional[float]
    y1: Optional[float]
    x2: Optional[float]
    y2: Optional[float]
    bbox_width: Optional[float]
    bbox_height: Optional[float]
    bbox_center_x: Optional[float]
    bbox_center_y: Optional[float]


class DetectionsResponse(BaseModel):
    run_id: int
    sequence_name: str
    total_detections: int
    detections: list[Detection]


class FrameStat(BaseModel):
    frame_id: int
    player_count: int
    avg_confidence: Optional[float]


class RunStatsResponse(BaseModel):
    run_id: int
    sequence_name: str
    total_frames: int
    total_detections: int
    avg_players_per_frame: Optional[float]
    max_players_in_frame: Optional[int]
    min_players_in_frame: Optional[int]
    avg_confidence: Optional[float]
    unique_track_ids: int
    per_frame: list[FrameStat]


class SequenceSummary(BaseModel):
    sequence_name: str
    total_detections: int
    unique_track_ids: int
    avg_confidence: Optional[float]


class SequencesResponse(BaseModel):
    total: int
    sequences: list[SequenceSummary]


class SequenceDetailResponse(BaseModel):
    sequence_name: str
    total_detections: int
    unique_track_ids: int
    avg_confidence: Optional[float]
    avg_players_per_frame: Optional[float]
    max_players_in_frame: Optional[int]
    min_players_in_frame: Optional[int]
    per_frame: list[FrameStat]