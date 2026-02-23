"""Run model evaluation across trained regression models and write a report."""

from __future__ import annotations

from pathlib import Path
import sys
from typing import Any

import joblib
import numpy as np
import pandas as pd
from scipy.stats import shapiro
from sklearn.model_selection import train_test_split

if __package__ is None or __package__ == "":
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.model_evaluation import (  # noqa: E402
    compare_models,
    compute_residuals,
    generate_evaluation_report,
    select_best_model,
)
from scripts.model_experiments import (  # noqa: E402
    get_experiment_models,
    load_experiment_data,
    train_model,
)

MODEL_FILE_NAMES = {
    "Linear Regression": "linear_regression.joblib",
    "Random Forest": "random_forest.joblib",
    "Gradient Boosting": "gradient_boosting.joblib",
}


def _format_table_for_console(results_df: pd.DataFrame) -> str:
    """Return a compact string table for console output."""

    display_df = results_df.copy()
    for column in ["mse", "mae", "rmse", "r2"]:
        if column in display_df.columns:
            display_df[column] = display_df[column].map(
                lambda value: f"{float(value):.4f}"
            )
    return display_df.to_string(index=False)


def _load_or_train_models(
    X_train: pd.DataFrame,
    y_train: pd.Series,
    models_dir: str | Path = "models",
    random_state: int = 42,
) -> tuple[dict[str, Any], dict[str, str]]:
    """Load trained models from disk, training missing ones as a fallback."""

    models_dir = Path(models_dir)
    models_dir.mkdir(parents=True, exist_ok=True)

    models: dict[str, Any] = {}
    load_notes: dict[str, str] = {}

    for model_name, model in get_experiment_models(random_state=random_state).items():
        file_name = MODEL_FILE_NAMES.get(
            model_name, f"{model_name.lower().replace(' ', '_')}.joblib"
        )
        model_path = models_dir / file_name

        if model_path.exists():
            models[model_name] = joblib.load(model_path)
            load_notes[model_name] = f"Loaded existing model from {model_path}."
            continue

        trained_model = train_model(model, X_train, y_train)
        joblib.dump(trained_model, model_path)
        models[model_name] = trained_model
        load_notes[model_name] = (
            f"Model file not found; trained and saved fallback model at {model_path}."
        )

    return models, load_notes


def _build_best_model_justification(
    results_df: pd.DataFrame, best_model_name: str
) -> str:
    """Create a short justification string using top R² and error metrics."""

    best_row = results_df.loc[results_df["model"] == best_model_name].iloc[0]
    if len(results_df) > 1:
        second_row = results_df.iloc[1]
        r2_margin = float(best_row["r2"]) - float(second_row["r2"])
        margin_text = f" It leads the next-best model by {r2_margin:.4f} R²."
    else:
        margin_text = ""

    return (
        f"{best_model_name} has the highest R² ({float(best_row['r2']):.4f}) "
        f"with RMSE {float(best_row['rmse']):.4f} and MAE {float(best_row['mae']):.4f}."
        f"{margin_text}"
    )


def _analyze_residuals(residuals: np.ndarray) -> tuple[dict[str, Any], str]:
    """Compute residual summary statistics and narrative observations."""

    mean_residual = float(np.mean(residuals))
    std_residual = float(np.std(residuals, ddof=0))

    if len(residuals) >= 3:
        stat, p_value = shapiro(residuals)
        normality_result = "approximately normal" if p_value > 0.05 else "not normal"
        normality_test = "Shapiro-Wilk"
        distribution_notes = (
            "Residuals are "
            f"{normality_result} at alpha=0.05 (test statistic={stat:.4f})."
        )
    else:
        p_value = float("nan")
        normality_test = "Shapiro-Wilk (not run)"
        distribution_notes = "Residual sample is too small to assess normality."

    bias_note = (
        "minimal bias"
        if abs(mean_residual) < 0.1 * max(std_residual, 1e-9)
        else "possible systematic bias"
    )
    spread_note = "tight spread" if std_residual < 1.0 else "wider spread"
    outlier_note = (
        "No large residual outliers detected."
        if len(residuals) == 0
        or np.max(np.abs(residuals)) <= 3 * max(std_residual, 1e-9)
        else (
            "Potential outliers present (max absolute residual exceeds "
            "3 standard deviations)."
        )
    )
    error_observations = (
        "Residual mean suggests "
        f"{bias_note}; residual variability shows {spread_note}. "
        f"{outlier_note}"
    )

    summary = {
        "mean": f"{mean_residual:.4f}",
        "std": f"{std_residual:.4f}",
        "normality_test": normality_test,
        "p_value": "nan" if np.isnan(p_value) else f"{float(p_value):.4f}",
        "distribution_notes": distribution_notes,
    }
    return summary, error_observations


def main() -> int:
    """Execute model evaluation and write the markdown report."""

    random_state = 42
    X, y = load_experiment_data()
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=random_state
    )

    models, load_notes = _load_or_train_models(
        X_train, y_train, random_state=random_state
    )

    results_dict: dict[str, dict[str, Any]] = {}
    for model_name, model in models.items():
        y_pred = model.predict(X_test)
        results_dict[model_name] = {"y_true": y_test.to_numpy(), "y_pred": y_pred}

    results_df = compare_models(results_dict)
    best_model_name = select_best_model(results_dict)
    best_residuals = compute_residuals(
        results_dict[best_model_name]["y_true"], results_dict[best_model_name]["y_pred"]
    )
    residual_summary, error_observations = _analyze_residuals(best_residuals)
    residual_summary["best_model_justification"] = _build_best_model_justification(
        results_df, best_model_name
    )

    print("Model Comparison")
    print(_format_table_for_console(results_df))
    print()
    print(f"Best Model: {best_model_name}")
    print(residual_summary["best_model_justification"])
    print()
    print("Residual Analysis")
    print(
        f"mean={residual_summary['mean']}, std={residual_summary['std']}, "
        f"{residual_summary['normality_test']} p-value={residual_summary['p_value']}"
    )

    if load_notes:
        print()
        print("Model Loading Notes")
        for model_name, note in load_notes.items():
            print(f"- {model_name}: {note}")

    generate_evaluation_report(
        results_df=results_df,
        best_model_name=best_model_name,
        output_path=Path("models") / "evaluation_report.md",
        residual_analysis=residual_summary,
        error_observations=error_observations,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
