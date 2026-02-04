from __future__ import annotations

from typing import Optional, Tuple

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from matplotlib.axes import Axes
from matplotlib.figure import Figure


def _numeric_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """Return only the numeric columns from the provided dataframe."""
    return df.select_dtypes(include="number")


def get_summary_statistics(df: pd.DataFrame) -> pd.DataFrame:
    """Return core summary statistics for every numeric feature."""
    numeric = _numeric_dataframe(df)
    if numeric.empty:
        return pd.DataFrame()

    metrics = {
        "mean": numeric.mean(),
        "median": numeric.median(),
        "std": numeric.std(ddof=0),
        "25%": numeric.quantile(0.25),
        "50%": numeric.quantile(0.5),
        "75%": numeric.quantile(0.75),
    }
    summary = pd.DataFrame(metrics)
    column_order = ["mean", "median", "std", "25%", "50%", "75%"]
    return summary.loc[:, column_order]


def calculate_correlations(df: pd.DataFrame, method: str = "pearson") -> pd.DataFrame:
    """Return numeric correlations using the requested method."""
    numeric = _numeric_dataframe(df)
    return numeric.corr(method=method)


def create_distribution_plot(
    df: pd.DataFrame,
    column: str,
    ax: Optional[Axes] = None,
    figsize: Tuple[float, float] = (6, 4),
) -> Tuple[Figure, Axes]:
    """Render a histogram + KDE for a numeric column."""
    numeric = _numeric_dataframe(df)
    if column not in numeric.columns:
        raise ValueError(f"Column {column!r} is not numeric or does not exist.")

    if ax is None:
        fig, ax = plt.subplots(figsize=figsize)
    else:
        fig = ax.figure

    series = numeric[column].dropna()
    sns.histplot(series, kde=True, ax=ax, stat="density", color="tab:blue")
    ax.set_title(f"Distribution of {column}")
    ax.set_xlabel(column)
    ax.set_ylabel("Density")
    ax.grid(True, alpha=0.3)
    return fig, ax


def create_correlation_heatmap(
    corr_matrix: pd.DataFrame,
    ax: Optional[Axes] = None,
    figsize: Tuple[float, float] = (8, 6),
    annot: bool = True,
    cmap: str = "vlag",
) -> Tuple[Figure, Axes]:
    """Render a heatmap for the correlation matrix."""
    if corr_matrix.empty:
        raise ValueError("Correlation matrix is empty.")

    if ax is None:
        fig, ax = plt.subplots(figsize=figsize)
    else:
        fig = ax.figure

    sns.heatmap(
        corr_matrix,
        annot=annot,
        fmt=".2f",
        cmap=cmap,
        center=0,
        square=True,
        cbar_kws={"shrink": 0.75},
        ax=ax,
    )
    ax.set_title("Correlation Matrix")
    return fig, ax
