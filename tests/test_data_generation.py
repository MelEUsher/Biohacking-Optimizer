import os
from pathlib import Path

import numpy as np
import pandas as pd

from scripts.generate_synthetic_data import generate_synthetic_data, save_synthetic_data


REQUIRED_COLUMNS = [
    "sleep_hours",
    "workout_intensity",
    "supplement_intake",
    "screen_time",
    "stress_level",
]


def test_synthetic_data_schema_and_size():
    df = generate_synthetic_data()

    assert set(REQUIRED_COLUMNS).issubset(df.columns)
    assert len(df) >= 500
    assert df[REQUIRED_COLUMNS].count().min() == len(df)

    for column in REQUIRED_COLUMNS:
        assert pd.api.types.is_numeric_dtype(df[column])


def test_synthetic_data_ranges():
    df = generate_synthetic_data()

    assert df["sleep_hours"].between(3.5, 10.5).all()
    assert df["workout_intensity"].between(0, 10).all()
    assert df["supplement_intake"].between(0, 8).all()
    assert df["screen_time"].between(0, 14).all()
    assert df["stress_level"].between(0, 10).all()


def test_synthetic_data_distribution_quality():
    df = generate_synthetic_data()

    assert df[REQUIRED_COLUMNS].std().gt(0).all()
    assert df["sleep_hours"].mean() >= 5.5
    assert df["sleep_hours"].mean() <= 8
    assert df["stress_level"].mean() >= 3
    assert df["stress_level"].mean() <= 7


def test_synthetic_data_correlations():
    df = generate_synthetic_data()
    corr = df[REQUIRED_COLUMNS].corr()

    assert corr.loc["sleep_hours", "stress_level"] < -0.1
    assert corr.loc["workout_intensity", "stress_level"] < -0.05
    assert corr.loc["workout_intensity", "supplement_intake"] > 0.1
    assert corr.loc["screen_time", "sleep_hours"] < -0.05


def test_save_synthetic_data_creates_csv():
    df = generate_synthetic_data()
    output_path = Path("data/raw/synthetic_biohacking_data.csv")
    output_path.parent.mkdir(parents=True, exist_ok=True)

    if output_path.exists():
        output_path.unlink()

    save_synthetic_data(df, output_path)

    assert output_path.exists()
    saved = pd.read_csv(output_path)
    assert len(saved) >= 500
    assert set(REQUIRED_COLUMNS).issubset(saved.columns)
