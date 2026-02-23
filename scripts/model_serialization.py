"""Utilities for saving and loading trained models and preprocessing pipelines."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any

import joblib


def _timestamp_string() -> str:
    """Return a filesystem-safe timestamp string for serialized artifact names."""

    return datetime.now().strftime("%Y%m%d_%H%M%S")


def _artifact_path(directory: str | Path, artifact_name: str) -> Path:
    """Create a timestamped artifact path in the target directory."""

    output_dir = Path(directory)
    output_dir.mkdir(parents=True, exist_ok=True)
    filename = f"{artifact_name}_{_timestamp_string()}.joblib"
    return output_dir / filename


def save_model(model: Any, directory: str | Path, model_name: str) -> str:
    """Serialize a trained model to disk and return the saved file path."""

    save_path = _artifact_path(directory, model_name)
    joblib.dump(model, save_path)
    return str(save_path)


def load_model(path: str | Path) -> Any:
    """Load a serialized model from disk, raising a clear error if missing."""

    model_path = Path(path)
    if not model_path.exists():
        raise FileNotFoundError(f"Model file not found: {model_path}")
    return joblib.load(model_path)


def save_pipeline(pipeline: Any, directory: str | Path, pipeline_name: str) -> str:
    """Serialize a fitted preprocessing pipeline to disk and return its path."""

    save_path = _artifact_path(directory, pipeline_name)
    joblib.dump(pipeline, save_path)
    return str(save_path)


def load_pipeline(path: str | Path) -> Any:
    """Load a serialized preprocessing pipeline, raising a clear error if missing."""

    pipeline_path = Path(path)
    if not pipeline_path.exists():
        raise FileNotFoundError(f"Pipeline file not found: {pipeline_path}")
    return joblib.load(pipeline_path)
