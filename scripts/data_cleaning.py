import pandas as pd


def drop_missing_rows(df: pd.DataFrame) -> pd.DataFrame:
    """
    Drops rows with any missing values from the DataFrame.
    """
    return df.dropna()
