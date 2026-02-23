from pathlib import Path

import joblib
import numpy as np
import pandas as pd
import pytest
from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score


def _build_regression_dataframe(rows: int = 80) -> pd.DataFrame:
    rng = np.random.default_rng(42)
    sleep = rng.normal(7.0, 1.0, size=rows)
    steps = rng.normal(8000, 1200, size=rows)
    hydration = rng.normal(2.5, 0.4, size=rows)
    caffeine = rng.normal(180, 50, size=rows)
    noise = rng.normal(0, 0.2, size=rows)

    stress = (
        8.0 - 0.6 * sleep - 0.0002 * steps - 0.8 * hydration + 0.005 * caffeine + noise
    )
    return pd.DataFrame(
        {
            "sleep_hours": sleep,
            "steps": steps,
            "hydration_liters": hydration,
            "caffeine_mg": caffeine,
            "stress_level": stress,
        }
    )


def _create_trained_models(df: pd.DataFrame, models_dir: Path) -> None:
    from sklearn.model_selection import train_test_split

    X = df.drop(columns=["stress_level"])
    y = df["stress_level"]
    X_train, _, y_train, _ = train_test_split(X, y, test_size=0.2, random_state=42)

    models_dir.mkdir(parents=True, exist_ok=True)
    model_map = {
        "linear_regression.joblib": LinearRegression(),
        "random_forest.joblib": RandomForestRegressor(n_estimators=25, random_state=42),
        "gradient_boosting.joblib": GradientBoostingRegressor(random_state=42),
    }
    for file_name, model in model_map.items():
        model.fit(X_train, y_train)
        joblib.dump(model, models_dir / file_name)


def test_calculate_metrics_returns_required_keys_and_values():
    from scripts.model_evaluation import calculate_metrics

    y_true = np.array([3.0, -0.5, 2.0, 7.0])
    y_pred = np.array([2.5, 0.0, 2.0, 8.0])

    metrics = calculate_metrics(y_true, y_pred)

    assert set(metrics.keys()) == {"mse", "mae", "r2", "rmse"}
    assert metrics["mse"] == pytest.approx(mean_squared_error(y_true, y_pred))
    assert metrics["mae"] == pytest.approx(mean_absolute_error(y_true, y_pred))
    assert metrics["r2"] == pytest.approx(r2_score(y_true, y_pred))
    assert metrics["rmse"] == pytest.approx(np.sqrt(mean_squared_error(y_true, y_pred)))


def test_compare_models_returns_sorted_dataframe_by_r2():
    from scripts.model_evaluation import compare_models

    y_true = np.array([1.0, 2.0, 3.0, 4.0])
    results_dict = {
        "Worse Model": {
            "y_true": y_true,
            "y_pred": np.array([1.3, 1.7, 3.5, 3.5]),
        },
        "Best Model": {
            "y_true": y_true,
            "y_pred": np.array([1.0, 2.0, 3.1, 3.9]),
        },
        "Middle Model": {
            "y_true": y_true,
            "y_pred": np.array([1.1, 2.1, 2.8, 4.2]),
        },
    }

    comparison = compare_models(results_dict)

    assert isinstance(comparison, pd.DataFrame)
    assert len(comparison) == 3
    assert list(comparison["model"]) == ["Best Model", "Middle Model", "Worse Model"]
    assert comparison["r2"].tolist() == sorted(comparison["r2"].tolist(), reverse=True)
    assert {"mse", "mae", "r2", "rmse"}.issubset(comparison.columns)


def test_select_best_model_returns_name_with_highest_r2():
    from scripts.model_evaluation import select_best_model

    y_true = np.array([1.0, 2.0, 3.0, 4.0])
    results_dict = {
        "Linear Regression": {
            "y_true": y_true,
            "y_pred": np.array([1.1, 1.9, 3.0, 3.8]),
        },
        "Random Forest": {"y_true": y_true, "y_pred": np.array([1.0, 2.0, 3.0, 4.0])},
        "Gradient Boosting": {
            "y_true": y_true,
            "y_pred": np.array([0.9, 2.2, 2.7, 4.2]),
        },
    }

    best_model = select_best_model(results_dict)

    assert best_model == "Random Forest"


def test_compute_residuals_returns_expected_values_and_length():
    from scripts.model_evaluation import compute_residuals

    y_true = np.array([10.0, 8.0, 6.0, 4.0])
    y_pred = np.array([9.5, 8.5, 5.0, 4.0])

    residuals = compute_residuals(y_true, y_pred)

    assert isinstance(residuals, np.ndarray)
    assert len(residuals) == len(y_true)
    assert np.allclose(residuals, np.array([0.5, -0.5, 1.0, 0.0]))


def test_evaluation_script_loads_trained_models_without_error(
    tmp_path, monkeypatch, capsys
):
    from scripts import run_evaluation

    project_root = tmp_path
    raw_dir = project_root / "data" / "raw"
    raw_dir.mkdir(parents=True, exist_ok=True)
    df = _build_regression_dataframe()
    df.to_csv(raw_dir / "synthetic_biohacking_data.csv", index=False)
    _create_trained_models(df, project_root / "models")

    monkeypatch.chdir(project_root)

    exit_code = run_evaluation.main()
    output = capsys.readouterr().out

    assert exit_code == 0
    assert "Model Comparison" in output
    assert "Best Model" in output
    assert (project_root / "models" / "evaluation_report.md").exists()


def test_evaluation_script_creates_report_with_required_sections(tmp_path, monkeypatch):
    from scripts import run_evaluation

    project_root = tmp_path
    raw_dir = project_root / "data" / "raw"
    raw_dir.mkdir(parents=True, exist_ok=True)
    df = _build_regression_dataframe()
    df.to_csv(raw_dir / "synthetic_biohacking_data.csv", index=False)
    _create_trained_models(df, project_root / "models")

    monkeypatch.chdir(project_root)

    exit_code = run_evaluation.main()
    report_path = project_root / "models" / "evaluation_report.md"
    report_content = report_path.read_text(encoding="utf-8")

    assert exit_code == 0
    assert report_path.exists()
    assert "## Metrics Table" in report_content
    assert "## Best Model Selection" in report_content
    assert "## Residual Analysis Summary" in report_content
    assert "## Error Distribution Observations" in report_content
