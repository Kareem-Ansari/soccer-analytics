# Database connection and all query functions
# All SQL lives here - never in main.py
# Connection uses environment variables only - no hardcoded credentials

import os
import psycopg2
import psycopg2.extras
from typing import Optional


def get_connection():
    """
    Return a psycopg2 connection using environment variables.
    Called fresh for each request.
    """
    return psycopg2.connect(
        host=os.environ.get("DB_HOST", "localhost"),
        port=int(os.environ.get("DB_PORT", 5432)),
        database=os.environ.get("DB_NAME", "soccer_analytics"),
        user=os.environ.get("DB_USER", "postgres"),
        password=os.environ.get("DB_PASSWORD", ""),
        cursor_factory=psycopg2.extras.RealDictCursor
    )


def check_database_connection():
    """Returns True if database is reachable, False otherwise."""
    try:
        conn = get_connection()
        cur  = conn.cursor()
        cur.execute("SELECT 1")
        cur.close()
        conn.close()
        return True
    except Exception:
        return False


def get_all_runs():
    """Return all tracking runs ordered by most recent first."""
    conn = get_connection()
    cur  = conn.cursor()
    cur.execute("""
        SELECT run_id, sequence_name, started_at,
               total_frames, model_name,
               confidence_thresh, notes
        FROM tracking_runs
        ORDER BY started_at DESC;
    """)
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows


def get_detections_for_run(run_id: int,
                            limit: int = 1000,
                            offset: int = 0):
    """Return detections for a specific run with pagination."""
    conn = get_connection()
    cur  = conn.cursor()

    # Get run metadata
    cur.execute("""
        SELECT sequence_name FROM tracking_runs
        WHERE run_id = %s;
    """, (run_id,))
    run = cur.fetchone()

    if not run:
        cur.close()
        conn.close()
        return None

    # Get detections with pagination
    cur.execute("""
        SELECT id, frame_id, track_id, class_name,
               confidence, x1, y1, x2, y2,
               bbox_width, bbox_height,
               bbox_center_x, bbox_center_y
        FROM detections
        WHERE run_id = %s
        ORDER BY frame_id, track_id
        LIMIT %s OFFSET %s;
    """, (run_id, limit, offset))
    detections = cur.fetchall()

    # Get total count
    cur.execute("""
        SELECT COUNT(*) as total FROM detections
        WHERE run_id = %s;
    """, (run_id,))
    total = cur.fetchone()["total"]

    cur.close()
    conn.close()

    return {
        "sequence_name"    : run["sequence_name"],
        "total_detections" : total,
        "detections"       : detections,
    }


def get_run_stats(run_id: int):
    """Return aggregated stats for a tracking run."""
    conn = get_connection()
    cur  = conn.cursor()

    # Get run metadata
    cur.execute("""
        SELECT sequence_name, total_frames
        FROM tracking_runs WHERE run_id = %s;
    """, (run_id,))
    run = cur.fetchone()

    if not run:
        cur.close()
        conn.close()
        return None

    # Overall stats
    cur.execute("""
        SELECT
            COUNT(*)                          as total_detections,
            ROUND(AVG(confidence)::numeric,4) as avg_confidence,
            COUNT(DISTINCT track_id)          as unique_track_ids
        FROM detections WHERE run_id = %s;
    """, (run_id,))
    overall = cur.fetchone()

    # Per frame stats
    cur.execute("""
        SELECT
            frame_id,
            COUNT(*)                          as player_count,
            ROUND(AVG(confidence)::numeric,4) as avg_confidence
        FROM detections WHERE run_id = %s
        GROUP BY frame_id
        ORDER BY frame_id;
    """, (run_id,))
    per_frame = cur.fetchall()

    # Max and min players per frame
    cur.execute("""
        SELECT
            MAX(player_count) as max_players,
            MIN(player_count) as min_players,
            ROUND(AVG(player_count)::numeric,2) as avg_players
        FROM (
            SELECT frame_id, COUNT(*) as player_count
            FROM detections WHERE run_id = %s
            GROUP BY frame_id
        ) fc;
    """, (run_id,))
    frame_agg = cur.fetchone()

    cur.close()
    conn.close()

    return {
        "sequence_name"       : run["sequence_name"],
        "total_frames"        : run["total_frames"] or len(per_frame),
        "total_detections"    : overall["total_detections"],
        "avg_players_per_frame": frame_agg["avg_players"],
        "max_players_in_frame": frame_agg["max_players"],
        "min_players_in_frame": frame_agg["min_players"],
        "avg_confidence"      : overall["avg_confidence"],
        "unique_track_ids"    : overall["unique_track_ids"],
        "per_frame"           : per_frame,
    }


def get_all_sequences():
    """Return summary of all sequences in the database."""
    conn = get_connection()
    cur  = conn.cursor()
    cur.execute("""
        SELECT
            sequence_name,
            COUNT(*)                          as total_detections,
            COUNT(DISTINCT track_id)          as unique_track_ids,
            ROUND(AVG(confidence)::numeric,4) as avg_confidence
        FROM detections
        GROUP BY sequence_name
        ORDER BY sequence_name;
    """)
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows


def get_sequence_detail(sequence_name: str):
    """Return detailed stats for one sequence."""
    conn = get_connection()
    cur  = conn.cursor()

    # Overall stats
    cur.execute("""
        SELECT
            COUNT(*)                          as total_detections,
            COUNT(DISTINCT track_id)          as unique_track_ids,
            ROUND(AVG(confidence)::numeric,4) as avg_confidence
        FROM detections
        WHERE sequence_name = %s;
    """, (sequence_name,))
    overall = cur.fetchone()

    if not overall or overall["total_detections"] == 0:
        cur.close()
        conn.close()
        return None

    # Per frame
    cur.execute("""
        SELECT
            frame_id,
            COUNT(*)                          as player_count,
            ROUND(AVG(confidence)::numeric,4) as avg_confidence
        FROM detections
        WHERE sequence_name = %s
        GROUP BY frame_id
        ORDER BY frame_id;
    """, (sequence_name,))
    per_frame = cur.fetchall()

    # Aggregates
    cur.execute("""
        SELECT
            MAX(player_count) as max_players,
            MIN(player_count) as min_players,
            ROUND(AVG(player_count)::numeric,2) as avg_players
        FROM (
            SELECT frame_id, COUNT(*) as player_count
            FROM detections
            WHERE sequence_name = %s
            GROUP BY frame_id
        ) fc;
    """, (sequence_name,))
    agg = cur.fetchone()

    cur.close()
    conn.close()

    return {
        "total_detections"    : overall["total_detections"],
        "unique_track_ids"    : overall["unique_track_ids"],
        "avg_confidence"      : overall["avg_confidence"],
        "avg_players_per_frame": agg["avg_players"],
        "max_players_in_frame": agg["max_players"],
        "min_players_in_frame": agg["min_players"],
        "per_frame"           : per_frame,
    }