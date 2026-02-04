import subprocess
from pathlib import Path


def test_required_data_directories_exist():
    base = Path("data")
    for subdir in ("raw", "interim", "processed"):
        directory = base / subdir
        assert (
            directory.exists() and directory.is_dir()
        ), f"Missing directory: {directory}"


def run_git_check_ignore(path: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["git", "check-ignore", str(path)],
        capture_output=True,
        text=True,
    )


def test_large_data_files_are_ignored():
    large_file = Path("data") / "raw" / "huge_dataset.parquet"
    result = run_git_check_ignore(large_file)
    assert result.returncode == 0, "Large data files should be ignored by .gitignore"


def test_synthetic_data_remains_tracked():
    synthetic_file = Path("data") / "raw" / "synthetic_biohacking_data.csv"
    result = run_git_check_ignore(synthetic_file)
    assert result.returncode == 1, "synthetic_biohacking_data.csv must not be ignored"
