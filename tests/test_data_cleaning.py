import pandas as pd
from scripts.data_cleaning import drop_missing_rows, drop_columns_with_many_nans, drop_duplicate_rows


def test_drop_missing_rows_removes_nulls():
    # Create a simple test DataFrame with missing values
    data = {"sleep_hours": [7, 6, None, 8], "workout_intensity": [3, None, 5, 2]}
    df = pd.DataFrame(data)

    # Apply the function
    cleaned_df = drop_missing_rows(df)

    # Expectation: Should only keep rows without any NaNs
    assert cleaned_df.isnull().sum().sum() == 0
    assert len(cleaned_df) == 2


def test_drop_columns_with_many_nans():
    data = {
        "A": [1, 2, None, None, None],
        "B": [1, 2, 3, 4, 5],
        "C": [None, None, None, None, None],
    }
    df = pd.DataFrame(data)

    cleaned_df = drop_columns_with_many_nans(df, threshold=0.5)

    assert "C" not in cleaned_df.columns  # C should be dropped (100% missing)
    assert "A" not in cleaned_df.columns  # A should be dropped (60% missing)
    assert "B" in cleaned_df.columns  # B has 0% missing, stays


def test_drop_duplicate_rows():
    data = {
        'sleep_hours': [7, 6, 8, 5, 9],
        'workout_intensity': [3, 2, 4, 1, 5]
    }
    df = pd.DataFrame(data)

    # Intentionally create a duplicate row
    df = pd.concat([df, df.iloc[[0]]], ignore_index=True)

    cleaned_df = drop_duplicate_rows(df)

    # Expectation: only one duplicate should be removed
    assert len(cleaned_df) == len(df) - 1
    assert cleaned_df.duplicated().sum() == 0

