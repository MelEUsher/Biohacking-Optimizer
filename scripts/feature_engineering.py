"""Feature engineering and preprocessing utilities for numeric biohacking data."""

import pandas as pd
from sklearn.preprocessing import StandardScaler


def scale_features(df: pd.DataFrame) -> pd.DataFrame:
    """Scale all columns in a DataFrame using standardization.

    This function applies ``StandardScaler`` to every column in the provided
    DataFrame and returns a new DataFrame with the same index and column names.

    Args:
        df: Input DataFrame containing numeric feature columns.

    Returns:
        A new DataFrame where each column has been standardized to mean 0 and
        standard deviation 1 (using population standard deviation).
    """

    scaler = StandardScaler()
    scaled_values = scaler.fit_transform(df)
    return pd.DataFrame(scaled_values, columns=df.columns, index=df.index)


def add_derived_features(df: pd.DataFrame) -> pd.DataFrame:
    """Create derived feature columns used by the stress prediction workflow.

    The function adds two engineered features:
    - ``sleep_to_screen_ratio``: ``sleep_hours / screen_time``
    - ``workout_supplement_index``: ``workout_intensity * supplement_intake``

    Args:
        df: Input DataFrame containing the required base feature columns.

    Returns:
        A copy of the input DataFrame with the derived columns appended.
    """

    engineered_df = df.copy()
    engineered_df["sleep_to_screen_ratio"] = (
        engineered_df["sleep_hours"] / engineered_df["screen_time"]
    )
    engineered_df["workout_supplement_index"] = (
        engineered_df["workout_intensity"] * engineered_df["supplement_intake"]
    )
    return engineered_df


def handle_missing_values(df: pd.DataFrame) -> pd.DataFrame:
    """Impute missing values in numeric columns using column means.

    Args:
        df: Input DataFrame that may contain missing values.

    Returns:
        A new DataFrame where missing values in numeric columns are replaced
        with each column's mean value.
    """

    imputed_df = df.copy()
    numeric_columns = imputed_df.select_dtypes(include="number").columns
    for column in numeric_columns:
        mean_value = imputed_df[column].mean()
        imputed_df[column] = imputed_df[column].fillna(mean_value)
    return imputed_df


def build_preprocessing_pipeline(df: pd.DataFrame) -> pd.DataFrame:
    """Run the complete preprocessing pipeline on a DataFrame.

    The pipeline performs the following steps in order:
    1. Mean-impute missing numeric values
    2. Add derived feature columns
    3. Standardize all resulting columns

    Args:
        df: Input DataFrame containing numeric biohacking features.

    Returns:
        A transformed DataFrame containing imputed, engineered, and scaled
        features.
    """

    imputed_df = handle_missing_values(df)
    engineered_df = add_derived_features(imputed_df)
    return scale_features(engineered_df)
