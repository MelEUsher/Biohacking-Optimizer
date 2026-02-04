import csv
from pathlib import Path

SCHEMA_PATH = Path("data/schema.md")
RAW_CSV_PATH = Path("data/raw/synthetic_biohacking_data.csv")


def _load_schema_text() -> str:
    return SCHEMA_PATH.read_text(encoding="utf-8")


def _load_sources() -> list[str]:
    with RAW_CSV_PATH.open(newline="", encoding="utf-8") as csvfile:
        reader = csv.reader(csvfile)
        return next(reader)


def test_schema_file_exists() -> None:
    assert (
        SCHEMA_PATH.exists()
    ), "data/schema.md must be created before running schema validation tests."


def test_schema_covers_all_features() -> None:
    schema_text = _load_schema_text()
    features = _load_sources()

    missing = [feature for feature in features if feature not in schema_text]
    assert (
        not missing
    ), f"Schema document is missing feature definitions for: {', '.join(missing)}"


def test_schema_includes_required_fields() -> None:
    schema_text = _load_schema_text()
    required_fields = ["Data type", "Units"]
    missing = [field for field in required_fields if field not in schema_text]
    assert (
        not missing
    ), f"Schema document must document required fields: {', '.join(missing)}"

    valid_range_present = (
        "Valid range" in schema_text or "Valid/expected range" in schema_text
    )
    assert (
        valid_range_present
    ), "Schema document must describe valid ranges for each feature."


def test_schema_follows_data_dictionary_format() -> None:
    schema_text = _load_schema_text()
    assert (
        "Data Dictionary" in schema_text
    ), "Schema doc should include a Data Dictionary heading."
    assert (
        "Feature name" in schema_text
    ), "Schema doc should highlight each feature name within the data dictionary."
