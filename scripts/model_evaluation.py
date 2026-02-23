"""Utilities for evaluating trained regression models and writing reports."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping

import numpy as np
import pandas as pd
from numpy.typing import ArrayLike, NDArray
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score


def _to_numpy_1d(values: ArrayLike) -> NDArray[np.float64]:
    """Convert array-like values to a 1D float numpy array."""

    arr = np.asarray(values, dtype=float).reshape(-1)
    return arr


def calculate_metrics(y_true: ArrayLike, y_pred: ArrayLike) -> dict[str, float]:
    """Calculate common regression metrics for predicted values."""

    y_true_arr = _to_numpy_1d(y_true)
    y_pred_arr = _to_numpy_1d(y_pred)

    mse = float(mean_squared_error(y_true_arr, y_pred_arr))
    mae = float(mean_absolute_error(y_true_arr, y_pred_arr))
    r2 = float(r2_score(y_true_arr, y_pred_arr))
    rmse = float(np.sqrt(mse))
    return {"mse": mse, "mae": mae, "r2": r2, "rmse": rmse}


def compute_residuals(y_true: ArrayLike, y_pred: ArrayLike) -> NDArray[np.float64]:
    """Return residuals as actual minus predicted values."""

    y_true_arr = _to_numpy_1d(y_true)
    y_pred_arr = _to_numpy_1d(y_pred)
    return y_true_arr - y_pred_arr


def compare_models(results_dict: Mapping[str, Mapping[str, Any]]) -> pd.DataFrame:
    """Build a model comparison table sorted by R² descending."""

    rows: list[dict[str, float | str]] = []
    for model_name, result in results_dict.items():
        metrics = calculate_metrics(result["y_true"], result["y_pred"])
        rows.append({"model": model_name, **metrics})

    if not rows:
        return pd.DataFrame(columns=["model", "mse", "mae", "r2", "rmse"])

    comparison = pd.DataFrame(rows).sort_values("r2", ascending=False)
    return comparison.reset_index(drop=True)


def select_best_model(results_dict: Mapping[str, Mapping[str, Any]]) -> str:
    """Return the name of the model with the highest R² score."""

    comparison = compare_models(results_dict)
    if comparison.empty:
        raise ValueError("Cannot select a best model from empty results.")
    return str(comparison.iloc[0]["model"])


def _markdown_metrics_table(results_df: pd.DataFrame) -> str:
    """Render a markdown table for the metrics dataframe."""

    columns = ["model", "mse", "mae", "rmse", "r2"]
    present_columns = [column for column in columns if column in results_df.columns]
    if not present_columns:
        return "No metrics available."

    header = "| " + " | ".join(present_columns) + " |"
    divider = "| " + " | ".join(["---"] * len(present_columns)) + " |"
    rows = []
    for _, row in results_df.iterrows():
        rendered_values: list[str] = []
        for column in present_columns:
            value = row[column]
            if isinstance(value, (float, np.floating)):
                rendered_values.append(f"{float(value):.4f}")
            else:
                rendered_values.append(str(value))
        rows.append("| " + " | ".join(rendered_values) + " |")
    return "\n".join([header, divider, *rows])


def generate_evaluation_report(
    results_df: pd.DataFrame,
    best_model_name: str,
    output_path: str | Path,
    residual_analysis: Mapping[str, Any] | None = None,
    error_observations: str | None = None,
) -> None:
    """Write a markdown model evaluation report to disk."""

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    residual_analysis = residual_analysis or {}
    mean_value = residual_analysis.get("mean", "N/A")
    std_value = residual_analysis.get("std", "N/A")
    normality_test = residual_analysis.get("normality_test", "N/A")
    p_value = residual_analysis.get("p_value", "N/A")
    distribution_notes = residual_analysis.get("distribution_notes", "N/A")
    best_model_justification = residual_analysis.get(
        "best_model_justification",
        "Selected based on the highest R² score.",
    )
    error_observations = error_observations or "No error observations available."

    report = "\n".join(
        [
            "# Model Evaluation Report",
            "",
            "## Metrics Table",
            "",
            _markdown_metrics_table(results_df),
            "",
            "## Best Model Selection",
            "",
            f"Best Model: **{best_model_name}**",
            "",
            f"Justification: {best_model_justification}",
            "",
            "## Residual Analysis Summary",
            "",
            f"- Mean residual: {mean_value}",
            f"- Standard deviation of residuals: {std_value}",
            f"- Normality test: {normality_test}",
            f"- p-value: {p_value}",
            f"- Distribution notes: {distribution_notes}",
            "",
            "## Error Distribution Observations",
            "",
            error_observations,
            "",
        ]
    )
    output_path.write_text(report, encoding="utf-8")
