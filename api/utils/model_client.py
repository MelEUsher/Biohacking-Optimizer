from __future__ import annotations

import os

import httpx


class ModelServiceError(Exception):
    """Base error for model service orchestration failures."""


class ModelServiceConfigError(ModelServiceError):
    """Raised when model service configuration is missing or invalid."""


class ModelServiceTimeoutError(ModelServiceError):
    """Raised when the model service request times out."""


class ModelServiceConnectionError(ModelServiceError):
    """Raised when the model service cannot be reached."""


class ModelServiceResponseError(ModelServiceError):
    """Raised when the model service returns an invalid response."""


def get_model_service_url() -> str:
    base_url = os.getenv("MODEL_SERVICE_URL")
    if not base_url:
        raise ModelServiceConfigError(
            "MODEL_SERVICE_URL environment variable is required."
        )
    return base_url.rstrip("/")


async def call_model_service(entry_data: dict) -> dict:
    url = f"{get_model_service_url()}/predict"

    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.post(url, json=entry_data)
    except httpx.TimeoutException as exc:
        raise ModelServiceTimeoutError("Model Service request timed out.") from exc
    except httpx.ConnectError as exc:
        raise ModelServiceConnectionError(
            "Failed to connect to Model Service."
        ) from exc
    except httpx.RequestError as exc:
        raise ModelServiceConnectionError("Model Service request failed.") from exc

    if response.status_code != 200:
        raise ModelServiceResponseError(
            f"Model Service returned status {response.status_code}."
        )

    try:
        payload = response.json()
    except ValueError as exc:
        raise ModelServiceResponseError("Model Service returned invalid JSON.") from exc

    if not isinstance(payload, dict):
        raise ModelServiceResponseError("Model Service response must be a JSON object.")

    if "prediction" not in payload or "recommendation" not in payload:
        raise ModelServiceResponseError(
            "Model Service response missing prediction or recommendation."
        )

    return payload
