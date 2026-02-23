import numpy as np
import pandas as pd

from scripts.feature_engineering import (
    add_derived_features,
    build_preprocessing_pipeline,
    handle_missing_values,
    scale_features,
)


def test_scale_features_standardizes_each_column():
    df = pd.DataFrame(
        {
            "sleep_hours": [6.0, 7.0, 8.0, 9.0],
            "workout_intensity": [1.0, 2.0, 3.0, 4.0],
            "supplement_intake": [0.0, 1.0, 0.0, 1.0],
            "screen_time": [2.0, 4.0, 6.0, 8.0],
        }
    )

    scaled_df = scale_features(df)

    assert isinstance(scaled_df, pd.DataFrame)
    assert list(scaled_df.columns) == list(df.columns)
    assert list(scaled_df.index) == list(df.index)

    for column in scaled_df.columns:
        assert np.isclose(scaled_df[column].mean(), 0.0, atol=1e-9)
        assert np.isclose(scaled_df[column].std(ddof=0), 1.0, atol=1e-9)


def test_add_derived_features_creates_expected_columns():
    df = pd.DataFrame(
        {
            "sleep_hours": [8.0, 6.0],
            "workout_intensity": [3.0, 4.0],
            "supplement_intake": [2.0, 1.5],
            "screen_time": [4.0, 3.0],
        }
    )

    engineered_df = add_derived_features(df)

    assert "sleep_to_screen_ratio" in engineered_df.columns
    assert "workout_supplement_index" in engineered_df.columns

    assert engineered_df.loc[0, "sleep_to_screen_ratio"] == 2.0
    assert engineered_df.loc[1, "sleep_to_screen_ratio"] == 2.0
    assert engineered_df.loc[0, "workout_supplement_index"] == 6.0
    assert engineered_df.loc[1, "workout_supplement_index"] == 6.0


def test_handle_missing_values_imputes_nulls_with_mean():
    df = pd.DataFrame(
        {
            "sleep_hours": [7.0, np.nan, 9.0],
            "workout_intensity": [2.0, 4.0, np.nan],
            "supplement_intake": [1.0, 2.0, 3.0],
            "screen_time": [np.nan, 5.0, 7.0],
        }
    )

    imputed_df = handle_missing_values(df)

    assert imputed_df.isnull().sum().sum() == 0
    assert imputed_df.loc[1, "sleep_hours"] == df["sleep_hours"].mean()
    assert imputed_df.loc[2, "workout_intensity"] == df["workout_intensity"].mean()
    assert imputed_df.loc[0, "screen_time"] == df["screen_time"].mean()


def test_build_preprocessing_pipeline_returns_transformed_dataframe():
    df = pd.DataFrame(
        {
            "sleep_hours": [7.0, np.nan, 8.0, 6.0],
            "workout_intensity": [3.0, 4.0, np.nan, 2.0],
            "supplement_intake": [1.0, 2.0, 1.5, 1.0],
            "screen_time": [4.0, 5.0, 6.0, np.nan],
        }
    )

    transformed_df = build_preprocessing_pipeline(df)

    expected_columns = {
        "sleep_hours",
        "workout_intensity",
        "supplement_intake",
        "screen_time",
        "sleep_to_screen_ratio",
        "workout_supplement_index",
    }

    assert isinstance(transformed_df, pd.DataFrame)
    assert set(transformed_df.columns) == expected_columns
    assert transformed_df.shape == (len(df), len(expected_columns))
    assert transformed_df.isnull().sum().sum() == 0
