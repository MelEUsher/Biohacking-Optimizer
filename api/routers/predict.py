from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd
from fastapi import APIRouter, HTTPException, status

from api.models.schemas import PredictRequest

router = APIRouter(tags=["predict"])

FEATURE_COLUMNS = [
    "sleep_hours",
    "workout_intensity",
    "supplement_intake",
    "screen_time",
]

MODEL: Any | None = None
PREPROCESSING_PIPELINE: Any | None = None
MODEL_LOAD_ERROR: Exception | None = None


def _models_dir() -> Path:
    return Path(__file__).resolve().parents[2] / "models"


def _latest_artifact_path(pattern: str) -> Path:
    candidates = [path for path in _models_dir().glob(pattern) if path.is_file()]
    if not candidates:
        raise FileNotFoundError(f"No artifacts found for pattern: {pattern}")
    return max(candidates, key=lambda path: path.stat().st_mtime)


def _load_artifacts() -> tuple[Any, Any]:
    import joblib

    model_path = _latest_artifact_path("*.joblib")
    if model_path.name.startswith("preprocessing_pipeline"):
        model_candidates = [
            path
            for path in _models_dir().glob("*.joblib")
            if path.is_file() and not path.name.startswith("preprocessing_pipeline")
        ]
        if not model_candidates:
            raise FileNotFoundError("No serialized model artifact found in models/")
        model_path = max(model_candidates, key=lambda path: path.stat().st_mtime)

    pipeline_path = _latest_artifact_path("preprocessing_pipeline*.joblib")
    return joblib.load(model_path), joblib.load(pipeline_path)


try:
    MODEL, PREPROCESSING_PIPELINE = _load_artifacts()
except (ImportError, FileNotFoundError) as exc:
    MODEL_LOAD_ERROR = exc


def _ensure_model_ready() -> None:
    if MODEL is None or PREPROCESSING_PIPELINE is None:
        detail = "Prediction service unavailable: model artifacts are not loaded."
        if MODEL_LOAD_ERROR is not None:
            detail = f"{detail} {MODEL_LOAD_ERROR}"
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=detail,
        )


def _build_recommendation(prediction: float) -> str:
    if prediction < 3.0:
        return (
            "Low predicted stress. Maintain your current recovery and "
            "screen-time habits."
        )
    if prediction < 6.0:
        return (
            "Moderate predicted stress. Prioritize sleep consistency and "
            "reduce screen time where possible."
        )
    return (
        "High predicted stress. Focus on recovery, lower evening screen "
        "time, and avoid overtraining."
    )


@router.post("")
def predict(payload: PredictRequest) -> dict[str, Any]:
    _ensure_model_ready()

    input_received = payload.model_dump()
    features = pd.DataFrame(
        [[input_received[name] for name in FEATURE_COLUMNS]], columns=FEATURE_COLUMNS
    )
    processed_features = PREPROCESSING_PIPELINE.transform(features)
    prediction = float(MODEL.predict(processed_features)[0])

    return {
        "prediction": prediction,
        "recommendation": _build_recommendation(prediction),
        "input_received": input_received,
    }
