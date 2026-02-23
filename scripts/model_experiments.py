"""Utilities for training and comparing regression models."""

from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import cross_val_score, train_test_split


def train_model(model: Any, X_train: Any, y_train: Any) -> Any:
    """Fit a regression model and return the trained model instance."""

    model.fit(X_train, y_train)
    return model


def evaluate_model(model: Any, X_test: Any, y_test: Any) -> dict[str, float]:
    """Evaluate a trained regression model and return common regression metrics."""

    predictions = model.predict(X_test)
    return {
        "mse": float(mean_squared_error(y_test, predictions)),
        "mae": float(mean_absolute_error(y_test, predictions)),
        "r2": float(r2_score(y_test, predictions)),
    }


def cross_validate_model(model: Any, X: Any, y: Any, cv: int = 5) -> np.ndarray:
    """Run cross-validation and return the score array."""

    return np.asarray(cross_val_score(model, X, y, cv=cv, scoring="r2"))


def get_experiment_models(random_state: int = 42) -> dict[str, Any]:
    """Return the set of regression models used for experimentation."""

    return {
        "Linear Regression": LinearRegression(),
        "Random Forest": RandomForestRegressor(
            n_estimators=100, random_state=random_state
        ),
        "Gradient Boosting": GradientBoostingRegressor(random_state=random_state),
    }


def load_experiment_data(
    processed_dir: str | Path = "data/processed",
    raw_path: str | Path = "data/raw/synthetic_biohacking_data.csv",
    target_column: str = "stress_level",
) -> tuple[pd.DataFrame, pd.Series]:
    """Load model experimentation data from processed data when available, else raw."""

    processed_dir = Path(processed_dir)
    raw_path = Path(raw_path)

    candidate_files = sorted(
        path
        for path in processed_dir.glob("*.csv")
        if path.is_file() and not path.name.startswith(".")
    )
    data_path = candidate_files[0] if candidate_files else raw_path

    if not data_path.exists():
        raise FileNotFoundError(f"No dataset found at {data_path}")

    df = pd.read_csv(data_path)
    numeric_df = df.select_dtypes(include=["number"]).copy()

    if numeric_df.empty:
        raise ValueError("Dataset does not contain numeric columns for modeling.")

    if target_column not in numeric_df.columns:
        target_column = numeric_df.columns[-1]

    X = numeric_df.drop(columns=[target_column])
    y = numeric_df[target_column]
    return X, y


def run_model_experiments(
    X: pd.DataFrame,
    y: pd.Series,
    test_size: float = 0.2,
    random_state: int = 42,
    cv: int = 5,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Train all experiment models and return metrics and cross-validation tables."""

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=random_state
    )

    metrics_rows: list[dict[str, float | str]] = []
    cv_rows: list[dict[str, float | str]] = []

    for name, model in get_experiment_models(random_state=random_state).items():
        trained_model = train_model(model, X_train, y_train)
        metrics = evaluate_model(trained_model, X_test, y_test)
        cv_scores = cross_validate_model(model, X, y, cv=cv)

        metrics_rows.append({"model": name, **metrics})
        cv_rows.append(
            {
                "model": name,
                "mean_r2": float(cv_scores.mean()),
                "std_r2": float(cv_scores.std()),
                "folds": int(len(cv_scores)),
            }
        )

    metrics_df = pd.DataFrame(metrics_rows).sort_values("r2", ascending=False)
    cv_df = pd.DataFrame(cv_rows).sort_values("mean_r2", ascending=False)
    return metrics_df.reset_index(drop=True), cv_df.reset_index(drop=True)
