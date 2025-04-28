import pandas as pd
from scripts.data_cleaning import drop_missing_rows


def test_drop_missing_rows_removes_nulls():
    # Create a simple test DataFrame with missing values
    data = {"sleep_hours": [7, 6, None, 8], "workout_intensity": [3, None, 5, 2]}
    df = pd.DataFrame(data)

    # Apply the function
    cleaned_df = drop_missing_rows(df)

    # Expectation: Should only keep rows without any NaNs
    assert cleaned_df.isnull().sum().sum() == 0
    assert len(cleaned_df) == 2
