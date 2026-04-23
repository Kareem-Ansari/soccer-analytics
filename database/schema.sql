-- soccer_analytics database schema
-- PostgreSQL + TimescaleDB

-- Tracks metadata for each inference run
CREATE TABLE IF NOT EXISTS tracking_runs (
    run_id            SERIAL PRIMARY KEY,
    sequence_name     TEXT NOT NULL,
    started_at        TIMESTAMPTZ DEFAULT NOW(),
    total_frames      INTEGER,
    model_name        TEXT,
    confidence_thresh FLOAT,
    notes             TEXT
);

-- Stores every detection per frame
-- TimescaleDB hypertable for fast time-range queries
CREATE TABLE IF NOT EXISTS detections (
    time            TIMESTAMPTZ NOT NULL,
    run_id          INTEGER REFERENCES tracking_runs(run_id),
    sequence_name   TEXT NOT NULL,
    frame_id        INTEGER NOT NULL,
    track_id        INTEGER,
    class_name      TEXT,
    confidence      FLOAT,
    x1              FLOAT,
    y1              FLOAT,
    x2              FLOAT,
    y2              FLOAT,
    bbox_width      FLOAT,
    bbox_height     FLOAT,
    bbox_center_x   FLOAT,
    bbox_center_y   FLOAT
);

-- Convert to hypertable (TimescaleDB)
SELECT create_hypertable('detections', 'time',
    if_not_exists => TRUE);

-- Indexes for common query patterns
CREATE INDEX IF NOT EXISTS idx_detections_sequence
    ON detections (sequence_name, frame_id);

CREATE INDEX IF NOT EXISTS idx_detections_track
    ON detections (track_id, sequence_name);
