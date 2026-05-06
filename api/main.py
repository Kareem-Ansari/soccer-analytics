# FastAPI application
# All routes defined here, all DB calls go through database.py
# Run via: uvicorn api.main:app --host 0.0.0.0 --port 8000

from fastapi import FastAPI, HTTPException, Query
from api.models import (
    HealthResponse,
    RunsResponse,
    DetectionsResponse,
    RunStatsResponse,
    SequencesResponse,
    SequenceDetailResponse,
)
from api import database

app = FastAPI(
    title="Soccer Analytics API",
    description=(
        "REST API for querying soccer player detection and "
        "tracking results from the SoccerNet tracking-2023 "
        "benchmark. Backed by PostgreSQL."
    ),
    version="1.0.0",
)


@app.get("/health", response_model=HealthResponse)
def health():
    """Check API and database connectivity."""
    db_ok = database.check_database_connection()
    return HealthResponse(
        status="ok",
        database="connected" if db_ok else "unreachable",
        version="1.0.0",
    )


@app.get("/runs", response_model=RunsResponse)
def list_runs():
    """List all tracking runs in the database."""
    rows = database.get_all_runs()
    return RunsResponse(
        total=len(rows),
        runs=rows,
    )


@app.get("/runs/{run_id}/detections",
         response_model=DetectionsResponse)
def get_detections(
    run_id: int,
    limit: int  = Query(default=1000, ge=1, le=5000),
    offset: int = Query(default=0, ge=0),
):
    """
    Return detections for a specific tracking run.
    Supports pagination via limit and offset query params.
    """
    result = database.get_detections_for_run(run_id, limit, offset)

    if result is None:
        raise HTTPException(
            status_code=404,
            detail=f"Run {run_id} not found"
        )

    return DetectionsResponse(
        run_id=run_id,
        sequence_name=result["sequence_name"],
        total_detections=result["total_detections"],
        detections=result["detections"],
    )


@app.get("/runs/{run_id}/stats",
         response_model=RunStatsResponse)
def get_run_stats(run_id: int):
    """
    Return aggregated statistics for a tracking run.
    Includes per-frame player counts and confidence scores.
    """
    result = database.get_run_stats(run_id)

    if result is None:
        raise HTTPException(
            status_code=404,
            detail=f"Run {run_id} not found"
        )

    return RunStatsResponse(
        run_id=run_id,
        sequence_name=result["sequence_name"],
        total_frames=result["total_frames"],
        total_detections=result["total_detections"],
        avg_players_per_frame=result["avg_players_per_frame"],
        max_players_in_frame=result["max_players_in_frame"],
        min_players_in_frame=result["min_players_in_frame"],
        avg_confidence=result["avg_confidence"],
        unique_track_ids=result["unique_track_ids"],
        per_frame=result["per_frame"],
    )


@app.get("/sequences", response_model=SequencesResponse)
def list_sequences():
    """List all sequences stored in the database with summary stats."""
    rows = database.get_all_sequences()
    return SequencesResponse(
        total=len(rows),
        sequences=rows,
    )


@app.get("/sequences/{sequence_name}",
         response_model=SequenceDetailResponse)
def get_sequence(sequence_name: str):
    """
    Return detailed stats for one sequence.
    Includes per-frame player counts and confidence breakdown.
    """
    result = database.get_sequence_detail(sequence_name)

    if result is None:
        raise HTTPException(
            status_code=404,
            detail=f"Sequence {sequence_name} not found"
        )

    return SequenceDetailResponse(
        sequence_name=sequence_name,
        total_detections=result["total_detections"],
        unique_track_ids=result["unique_track_ids"],
        avg_confidence=result["avg_confidence"],
        avg_players_per_frame=result["avg_players_per_frame"],
        max_players_in_frame=result["max_players_in_frame"],
        min_players_in_frame=result["min_players_in_frame"],
        per_frame=result["per_frame"],
    )