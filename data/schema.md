# Data Dictionary

This data dictionary captures the structure for `data/raw/synthetic_biohacking_data.csv`, which is used to explore how lifestyle variables predict the biohacking target `stress_level`. Each feature section documents the metadata, expected ranges, business logic, relationship to the target, and an example value from the dataset.

## Sample Record (for reference)

| sleep_hours | workout_intensity | supplement_intake | screen_time | stress_level |
|-------------|-------------------|-------------------|-------------|--------------|
| 6.64        | 2.30              | 2.40              | 6.76        | 2.93         |

## Feature: sleep_hours
- **Feature name:** `sleep_hours`
- **Data type:** Continuous float
- **Units of measurement:** Hours per night
- **Valid/expected range:** 0.0 to 12.0 hours (typical adult sleep window; dataset samples center between ~4.5 and 8.5)
- **Business logic explanation:** Higher nightly sleep duration signals better recovery and energy reserves, which are foundational for consistent cognitive performance and hormone balance.
- **Relationship to target variable:** More sleep is expected to lower `stress_level`, because sufficient rest mitigates cortisol spikes and improves emotional regulation.
- **Example record:** 6.64 hours (first row of `synthetic_biohacking_data.csv`).

## Feature: workout_intensity
- **Feature name:** `workout_intensity`
- **Data type:** Continuous float (e.g., perceived exertion scale)
- **Units of measurement:** Arbitrary intensity score (1 low to 10 high)
- **Valid/expected range:** 1.0 to 10.0; synthetic data centers between ~2.0 and 7.0.
- **Business logic explanation:** Higher intensity workouts trigger acute stress responses that, when managed with recovery, build resilience and cardiovascular health.
- **Relationship to target variable:** Moderate increases in workout intensity can lower `stress_level` by releasing endorphins, while excessively high intensity without recovery may increase reported stress.
- **Example record:** 2.30 intensity (first row value).

## Feature: supplement_intake
- **Feature name:** `supplement_intake`
- **Data type:** Continuous float (amount of targeted supplements)
- **Units of measurement:** Daily dosage units (normalized scale)
- **Valid/expected range:** 0.0 to 10.0 (normalized; synthetic data spans ~2.0–5.0).
- **Business logic explanation:** Consistent supplement intake (vitamins, adaptogens) supports micronutrient sufficiency and buffer against daily stressors.
- **Relationship to target variable:** A balanced supplement routine is expected to slightly reduce `stress_level` by improving neurotransmitter precursors or micronutrient cofactors.
- **Example record:** 2.40 normalized dosage (first row value).

## Feature: screen_time
- **Feature name:** `screen_time`
- **Data type:** Continuous float
- **Units of measurement:** Hours per day
- **Valid/expected range:** 0.0 to 16.0 hours; dataset entries cluster between ~3 and ~9 hours.
- **Business logic explanation:** Prolonged screen exposure, especially before bedtime, disrupts circadian rhythm and increases cognitive load.
- **Relationship to target variable:** Higher screen time is correlated with higher `stress_level` due to reduced sleep quality and constant stimulation.
- **Example record:** 6.76 hours (first row value).

## Feature & Target: stress_level
- **Feature name:** `stress_level` (target variable)
- **Data type:** Continuous float
- **Units of measurement:** Self-reported stress score (1 low to 10 high)
- **Valid/expected range:** 1.0 to 10.0; synthetic data spans ~2.0–5.0 for this sample batch.
- **Business logic explanation:** Aggregates psycho-physiological signals and lifestyle context to represent current perceived strain.
- **Relationship to target variable:** This is the outcome variable. All other features are used to explain and predict fluctuations in this stress score.
- **Example record:** 2.93 stress score (first row value).
