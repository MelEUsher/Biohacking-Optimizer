from pathlib import Path

import numpy as np
import pytest
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from scripts.model_serialization import (
    load_model,
    load_pipeline,
    save_model,
    save_pipeline,
)


@pytest.fixture
def sample_regression_data():
    rng = np.random.default_rng(42)
    X = rng.normal(size=(80, 4))
    y = (
        1.2 * X[:, 0]
        - 0.8 * X[:, 1]
        + 0.5 * X[:, 2]
        + 2.1 * X[:, 3]
        + rng.normal(scale=0.05, size=80)
    )
    return X, y


@pytest.fixture
def trained_model(sample_regression_data):
    X, y = sample_regression_data
    model = GradientBoostingRegressor(random_state=42)
    model.fit(X, y)
    return model, X


@pytest.fixture
def fitted_pipeline(sample_regression_data):
    X, _ = sample_regression_data
    pipeline = Pipeline([("scaler", StandardScaler())])
    pipeline.fit(X)
    return pipeline, X


def test_save_model_creates_file_on_disk(tmp_path, trained_model):
    model, _ = trained_model

    saved_path = save_model(model, tmp_path, "test_model")

    assert Path(saved_path).exists()
    assert Path(saved_path).is_file()


def test_save_model_filename_contains_timestamp_version_string(tmp_path, trained_model):
    model, _ = trained_model

    saved_path = save_model(model, tmp_path, "stress_model")
    name = Path(saved_path).name

    assert name.startswith("stress_model_")
    assert name.endswith(".joblib")

    timestamp = name.removeprefix("stress_model_").removesuffix(".joblib")
    assert len(timestamp) == 15
    assert timestamp[8] == "_"
    assert timestamp.replace("_", "").isdigit()


def test_load_model_returns_model_with_identical_predictions(tmp_path, trained_model):
    model, X = trained_model
    saved_path = save_model(model, tmp_path, "gb_model")

    loaded_model = load_model(saved_path)

    original_predictions = model.predict(X)
    loaded_predictions = loaded_model.predict(X)
    assert np.array_equal(original_predictions, loaded_predictions) or np.allclose(
        original_predictions, loaded_predictions
    )


def test_load_model_missing_path_raises_clear_file_not_found_error(tmp_path):
    missing_path = tmp_path / "nonexistent" / "path.joblib"

    with pytest.raises(FileNotFoundError, match="not found|does not exist"):
        load_model(missing_path)


def test_save_pipeline_creates_file_on_disk(tmp_path, fitted_pipeline):
    pipeline, _ = fitted_pipeline

    saved_path = save_pipeline(pipeline, tmp_path, "preprocess_pipeline")

    assert Path(saved_path).exists()
    assert Path(saved_path).is_file()


def test_load_pipeline_returns_pipeline_with_identical_transform_output(
    tmp_path, fitted_pipeline
):
    pipeline, X = fitted_pipeline
    saved_path = save_pipeline(pipeline, tmp_path, "preprocess_pipeline")

    loaded_pipeline = load_pipeline(saved_path)

    original_output = pipeline.transform(X)
    loaded_output = loaded_pipeline.transform(X)
    assert np.array_equal(original_output, loaded_output) or np.allclose(
        original_output, loaded_output
    )
