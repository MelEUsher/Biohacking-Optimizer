# API Module

## Directory Structure

```text
api/
├── __init__.py
├── main.py
├── models/
│   └── __init__.py
├── README.md
└── routers/
    ├── __init__.py
    └── health.py
```

## Run Locally

Install dependencies (from the project root):

```bash
pip install -r requirements.txt
```

Start the FastAPI app with Uvicorn:

```bash
uvicorn api.main:app --reload
```

The API will be available at `http://127.0.0.1:8000`.

## Endpoints

### `GET /health`

Health check endpoint used for service monitoring and test verification.

Response:

```json
{
  "status": "healthy",
  "version": "0.1.0"
}
```

### `POST /predict`

Run model inference against the regenerated Phase 2 preprocessing pipeline and
trained regression model to predict `stress_level`.

- Method: `POST`
- URL: `/predict`

Request body schema (`application/json`):

- `sleep_hours` (`float`, required): `0.0` to `12.0`
- `workout_intensity` (`float`, required): `1.0` to `10.0`
- `supplement_intake` (`float`, required): `0.0` to `10.0`
- `screen_time` (`float`, required): `0.0` to `16.0`

Example request:

```json
{
  "sleep_hours": 7.5,
  "workout_intensity": 5.0,
  "supplement_intake": 3.0,
  "screen_time": 4.0
}
```

Example response:

```json
{
  "prediction": 3.42,
  "recommendation": "Moderate predicted stress. Prioritize sleep consistency and reduce screen time where possible.",
  "input_received": {
    "sleep_hours": 7.5,
    "workout_intensity": 5.0,
    "supplement_intake": 3.0,
    "screen_time": 4.0
  }
}
```

## Validation Rules

The API uses Pydantic request schemas for input validation. Invalid requests return
`422 Unprocessable Entity` with a `detail` field describing validation errors.

### `PredictRequest` (`POST /predict`)

- `sleep_hours` (`float`, required): accepted range `0.0` to `12.0`
  - Example error: `sleep_hours must be between 0 and 12 hours.`
- `workout_intensity` (`float`, required): accepted range `1.0` to `10.0`
  - Example error: `workout_intensity must be between 1 and 10.`
- `supplement_intake` (`float`, required): accepted range `0.0` to `10.0`
  - Example error: `supplement_intake must be between 0 and 10.`
- `screen_time` (`float`, required): accepted range `0.0` to `16.0`
  - Example error: `screen_time must be between 0 and 16 hours.`
- `stress_level` (`int`, optional): accepted range `1` to `10` when provided
  - Example error: `stress_level must be between 1 and 10.`

### `EntryCreate` / Daily Entry Request (`POST /entries`, `PUT /entries/{id}`)

- `sleep_hours` (`float`, required): accepted range `0.0` to `24.0`
  - Example error: `sleep_hours must be between 0 and 24 hours.`
- `screen_time` (`float`, required): accepted range `0.0` to `24.0`
  - Example error: `screen_time must be between 0 and 24 hours.`
- `stress_level` (`int`, required): accepted range `1` to `10`
  - Example error: `stress_level must be between 1 and 10.`
- `workout_intensity` (`str`, required): non-empty string (whitespace-only rejected)
  - Example error: `workout_intensity must not be empty.`
- `supplement_intake` (`str | null`, optional): if provided, must be non-empty
  - Example error: `supplement_intake must not be empty when provided.`
- `date` (`YYYY-MM-DD`, required): ISO date format
  - Example error (FastAPI/Pydantic): invalid date format in `detail`

## Entries to Model Service Orchestration

When a client submits `POST /entries`, the API orchestrates a follow-up prediction request:

1. The API validates/authenticates the request and writes the new row to `daily_entries`.
2. The API calls the Model Service `POST /predict` endpoint.
3. On success, the API stores the returned prediction result in the `predictions` table.

### Sequence

`POST /entries` -> Model Service `POST /predict` -> `predictions` table insert

### Environment Variables

- `MODEL_SERVICE_URL` (required): Base URL for the external Model Service. The API appends `/predict` when making orchestration calls.

### Error Handling

- If the Model Service times out, cannot be reached, or returns a non-200 response, the API returns `503 Service Unavailable` with detail `"Model Service unavailable"`.
- The daily entry creation happens before the model call, so the `daily_entries` row remains persisted even when the Model Service request fails.
