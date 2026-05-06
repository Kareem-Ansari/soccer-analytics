# Soccer Analytics REST API

FastAPI REST API for querying soccer player detection
and tracking results from the SoccerNet tracking-2023 benchmark.

## Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | API and database status |
| GET | `/runs` | List all tracking runs |
| GET | `/runs/{run_id}/detections` | Detections for a run |
| GET | `/runs/{run_id}/stats` | Aggregated stats for a run |
| GET | `/sequences` | All sequences with summary stats |
| GET | `/sequences/{name}` | Detailed stats for one sequence |

## Running Locally

```bash
pip install -r requirements_api.txt
export DB_HOST=localhost
export DB_PORT=5432
export DB_NAME=soccer_analytics
export DB_USER=postgres
export DB_PASSWORD=your_password
uvicorn api.main:app --host 0.0.0.0 --port 8000
```

## Interactive Docs

FastAPI generates interactive docs automatically at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Example Responses

### GET /health
```json
{
  "status": "ok",
  "database": "connected",
  "version": "1.0.0"
}
```

### GET /runs/1/stats
```json
{
  "run_id": 1,
  "sequence_name": "SNMOT-116",
  "total_frames": 50,
  "total_detections": 423,
  "avg_players_per_frame": 8.46,
  "max_players_in_frame": 11,
  "min_players_in_frame": 6,
  "avg_confidence": 0.7823,
  "unique_track_ids": 14,
  "per_frame": [...]
}
```
