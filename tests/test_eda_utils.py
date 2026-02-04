import pandas as pd
from matplotlib.axes import Axes
from matplotlib.figure import Figure

from scripts.eda_utils import (
    calculate_correlations,
    create_correlation_heatmap,
    create_distribution_plot,
    get_summary_statistics,
)

SAMPLE_DF = pd.DataFrame(
    {
        "sleep_hours": [6.0, 7.0, 8.0, 9.0],
        "workout_intensity": [3.0, 4.0, 5.0, 6.0],
        "stress_level": [3.0, 2.0, 1.0, 0.0],
        "group": ["A", "A", "B", "B"],
    }
)


def test_get_summary_statistics_returns_core_metrics():
    summary = get_summary_statistics(SAMPLE_DF)

    expected_stats = {"mean", "median", "std", "25%", "50%", "75%"}
    assert expected_stats.issubset(set(summary.columns))

    sleep_stats = summary.loc["sleep_hours"]
    assert sleep_stats["mean"] == 7.5
    assert sleep_stats["median"] == 7.5
    assert sleep_stats["25%"] == 6.75
    assert sleep_stats["75%"] == 8.25


def test_calculate_correlations_matches_pearson():
    corr = calculate_correlations(SAMPLE_DF)

    assert "group" not in corr.columns
    assert corr.loc["sleep_hours", "workout_intensity"] > 0.99
    assert corr.loc["sleep_hours", "stress_level"] < -0.99


def test_visual_helpers_return_matplotlib_artifacts():
    fig_dist, ax_dist = create_distribution_plot(SAMPLE_DF, "sleep_hours")
    assert isinstance(fig_dist, Figure)
    assert isinstance(ax_dist, Axes)

    corr_matrix = calculate_correlations(SAMPLE_DF)
    fig_corr, ax_corr = create_correlation_heatmap(corr_matrix)
    assert isinstance(fig_corr, Figure)
    assert isinstance(ax_corr, Axes)
