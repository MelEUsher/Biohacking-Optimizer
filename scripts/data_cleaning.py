import pandas as pd


def drop_missing_rows(df: pd.DataFrame) -> pd.DataFrame:
    """Drops rows with any missing values from the DataFrame."""

    return df.dropna()


def drop_columns_with_many_nans(
    df: pd.DataFrame, threshold: float = 0.5
) -> pd.DataFrame:
    """
    Drops columns where the fraction of missing values exceeds the given threshold.
    """
    missing_fraction = df.isnull().mean()
    cols_to_drop = missing_fraction[missing_fraction > threshold].index
    return df.drop(columns=cols_to_drop)


def drop_duplicate_rows(df: pd.DataFrame) -> pd.DataFrame:
    """
    Drops duplicate rows from the DataFrame.
    """
    return df.drop_duplicates()
