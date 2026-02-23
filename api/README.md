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
