import numpy as np
import pytest
from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor
from sklearn.linear_model import LinearRegression

from scripts.model_experiments import (
    cross_validate_model,
    evaluate_model,
    train_model,
)


@pytest.fixture
def sample_regression_data():
    rng = np.random.default_rng(42)
    X = rng.normal(size=(60, 4))
    coefficients = np.array([1.5, -2.0, 0.75, 3.0])
    noise = rng.normal(scale=0.1, size=60)
    y = X @ coefficients + noise
    return X[:45], X[45:], y[:45], y[45:], X, y


@pytest.fixture
def models():
    return [
        LinearRegression(),
        RandomForestRegressor(n_estimators=10, random_state=42),
        GradientBoostingRegressor(random_state=42),
    ]


def test_train_model_returns_trained_model(sample_regression_data):
    X_train, _, y_train, _, _, _ = sample_regression_data
    model = LinearRegression()

    trained_model = train_model(model, X_train, y_train)

    assert trained_model is model
    assert hasattr(trained_model, "predict")
    assert hasattr(trained_model, "n_features_in_")
    assert trained_model.n_features_in_ == X_train.shape[1]


def test_predictions_return_array_with_expected_length(sample_regression_data):
    X_train, X_test, y_train, _, _, _ = sample_regression_data
    model = train_model(LinearRegression(), X_train, y_train)

    predictions = model.predict(X_test)

    assert isinstance(predictions, np.ndarray)
    assert len(predictions) == len(X_test)


def test_evaluate_model_returns_required_metrics(sample_regression_data):
    X_train, X_test, y_train, y_test, _, _ = sample_regression_data
    model = train_model(LinearRegression(), X_train, y_train)

    metrics = evaluate_model(model, X_test, y_test)

    assert set(["mse", "mae", "r2"]).issubset(metrics.keys())
    assert all(isinstance(metrics[key], float) for key in ["mse", "mae", "r2"])


def test_cross_validate_model_returns_scores_with_requested_fold_count(
    sample_regression_data,
):
    _, _, _, _, X, y = sample_regression_data

    scores = cross_validate_model(LinearRegression(), X, y, cv=3)

    assert isinstance(scores, np.ndarray)
    assert len(scores) == 3


@pytest.mark.parametrize(
    "model",
    [
        LinearRegression(),
        RandomForestRegressor(n_estimators=10, random_state=42),
        GradientBoostingRegressor(random_state=42),
    ],
)
def test_supported_models_train_and_predict_without_error(
    model, sample_regression_data
):
    X_train, X_test, y_train, _, _, _ = sample_regression_data

    trained_model = train_model(model, X_train, y_train)
    predictions = trained_model.predict(X_test)

    assert isinstance(predictions, np.ndarray)
    assert predictions.shape == (len(X_test),)
