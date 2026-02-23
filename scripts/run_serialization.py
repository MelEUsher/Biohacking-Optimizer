"""Train, serialize, and verify a regression model plus preprocessing pipeline."""

from __future__ import annotations

from pathlib import Path
import re
import sys
from typing import Any

import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

if __package__ is None or __package__ == "":
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.model_experiments import (
    get_experiment_models,
    load_experiment_data,
    train_model,
)  # noqa: E402
from scripts.model_serialization import (  # noqa: E402
    load_model,
    load_pipeline,
    save_model,
    save_pipeline,
)


def _extract_best_model_name(
    report_path: str | Path = "models/evaluation_report.md",
) -> str:
    """Read the evaluation report and return the recorded best model name."""

    path = Path(report_path)
    if not path.exists():
        return "Gradient Boosting"

    content = path.read_text(encoding="utf-8")
    match = re.search(r"Best Model:\s+\*\*(.+?)\*\*", content)
    if match:
        return match.group(1).strip()
    return "Gradient Boosting"


def _build_preprocessing_pipeline() -> tuple[Any, str]:
    """Return a preprocessing pipeline, preferring scripts.preprocessing."""

    try:
        from scripts import preprocessing as preprocessing_module  # type: ignore
    except ImportError:
        return (
            Pipeline([("scaler", StandardScaler())]),
            (
                "Using fallback StandardScaler pipeline "
                "(scripts/preprocessing.py not available)."
            ),
        )

    for factory_name in (
        "build_preprocessing_pipeline",
        "create_preprocessing_pipeline",
        "get_preprocessing_pipeline",
    ):
        factory = getattr(preprocessing_module, factory_name, None)
        if callable(factory):
            return (
                factory(),
                f"Using pipeline from scripts.preprocessing.{factory_name}().",
            )

    return (
        Pipeline([("scaler", StandardScaler())]),
        (
            "Using fallback StandardScaler pipeline "
            "(no supported pipeline factory found in scripts/preprocessing.py)."
        ),
    )


def _predictions_match(a: np.ndarray, b: np.ndarray) -> bool:
    """Return True when predictions match exactly or within floating tolerance."""

    return bool(np.array_equal(a, b) or np.allclose(a, b))


def main() -> int:
    """Train, serialize, and verify the selected model and preprocessing pipeline."""

    X, y = load_experiment_data()
    X_train, X_test, y_train, _ = train_test_split(X, y, test_size=0.2, random_state=42)

    preprocessing_pipeline, pipeline_note = _build_preprocessing_pipeline()
    X_train_processed = preprocessing_pipeline.fit_transform(X_train)
    X_test_processed = preprocessing_pipeline.transform(X_test)

    best_model_name = _extract_best_model_name()
    available_models = get_experiment_models(random_state=42)
    model = available_models.get(best_model_name, available_models["Gradient Boosting"])
    if best_model_name not in available_models:
        best_model_name = "Gradient Boosting"

    trained_model = train_model(model, X_train_processed, y_train)

    model_path = save_model(
        trained_model,
        directory="models",
        model_name=best_model_name.lower().replace(" ", "_"),
    )
    pipeline_path = save_pipeline(
        preprocessing_pipeline,
        directory="models",
        pipeline_name="preprocessing_pipeline",
    )

    loaded_model = load_model(model_path)
    loaded_pipeline = load_pipeline(pipeline_path)

    original_predictions = trained_model.predict(X_test_processed)
    loaded_predictions = loaded_model.predict(loaded_pipeline.transform(X_test))
    verification_passed = _predictions_match(original_predictions, loaded_predictions)

    print(f"Selected model: {best_model_name}")
    print(pipeline_note)
    print(f"Saved model to: {model_path}")
    print(f"Saved pipeline to: {pipeline_path}")
    print(f"Prediction verification passed: {verification_passed}")

    return 0 if verification_passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
