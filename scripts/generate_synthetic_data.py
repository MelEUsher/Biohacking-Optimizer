from pathlib import Path

import numpy as np
import pandas as pd

BASE_COLUMNS = [
    "sleep_hours",
    "workout_intensity",
    "supplement_intake",
    "screen_time",
    "stress_level",
]


def generate_synthetic_data(
    num_samples: int = 600, random_seed: int = 42
) -> pd.DataFrame:
    """Generate a realistic biohacking dataset with correlated lifestyle features."""

    rng = np.random.default_rng(random_seed)

    screen_time = rng.normal(loc=6.0, scale=2.5, size=num_samples)
    screen_time = np.clip(screen_time, 0, 14)

    sleep_noise = rng.normal(loc=0.0, scale=0.35, size=num_samples)
    sleep_hours = 7.0 - 0.08 * screen_time + sleep_noise
    sleep_hours = np.clip(sleep_hours, 3.5, 10.5)

    workout_base = rng.normal(loc=5.0, scale=1.8, size=num_samples)
    workout_intensity = workout_base + 0.1 * (sleep_hours - 6.5) - 0.05 * screen_time
    workout_intensity = np.clip(workout_intensity, 0, 10)

    supplement_noise = rng.normal(loc=0.0, scale=0.4, size=num_samples)
    supplement_intake = 1.5 + 0.4 * workout_intensity + supplement_noise
    supplement_intake = np.clip(supplement_intake, 0, 8)

    stress_base = rng.normal(loc=5.0, scale=1.2, size=num_samples)
    stress_level = (
        stress_base - 0.25 * sleep_hours - 0.18 * workout_intensity + 0.08 * screen_time
    )
    stress_level = np.clip(stress_level, 0, 10)

    data = {
        "sleep_hours": sleep_hours,
        "workout_intensity": workout_intensity,
        "supplement_intake": supplement_intake,
        "screen_time": screen_time,
        "stress_level": stress_level,
    }

    return pd.DataFrame(data)[BASE_COLUMNS]


def save_synthetic_data(dataframe: pd.DataFrame, output_path: Path | str) -> None:
    """Persist the generated biohacking dataset as a CSV file."""

    path_obj = Path(output_path)
    path_obj.parent.mkdir(parents=True, exist_ok=True)
    dataframe.to_csv(path_obj, index=False)
