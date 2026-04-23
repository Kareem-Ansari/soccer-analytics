-- Sample analytical queries for soccer_analytics database

-- Average players detected per frame in a sequence
SELECT
    ROUND(AVG(player_count)::numeric, 2) as avg_players
FROM (
    SELECT frame_id, COUNT(*) as player_count
    FROM detections
    WHERE sequence_name = 'SNMOT-116'
    GROUP BY frame_id
) frame_counts;

-- Player detection count over time
SELECT
    frame_id,
    COUNT(*) as player_count,
    ROUND(AVG(confidence)::numeric, 4) as avg_confidence
FROM detections
WHERE sequence_name = 'SNMOT-116'
GROUP BY frame_id
ORDER BY frame_id;

-- Unique players tracked per sequence
SELECT
    sequence_name,
    COUNT(DISTINCT track_id) as unique_players,
    COUNT(*) as total_detections
FROM detections
GROUP BY sequence_name;

-- High confidence detections only
SELECT frame_id, track_id, confidence, bbox_center_x, bbox_center_y
FROM detections
WHERE confidence > 0.8
ORDER BY frame_id, track_id;
