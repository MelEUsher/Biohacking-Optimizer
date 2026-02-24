from pathlib import Path

README_PATH = Path(__file__).resolve().parents[1] / "README.md"
README_TEXT = README_PATH.read_text(encoding="utf-8")


def test_readme_exists_at_repo_root():
    assert README_PATH.exists()


def test_readme_has_getting_started_section():
    assert "## Getting Started" in README_TEXT


def test_readme_includes_setup_instructions():
    expected_snippets = [
        "git clone",
        "python3 -m venv",
        "pip install -r requirements.txt",
    ]
    for snippet in expected_snippets:
        assert snippet in README_TEXT


def test_readme_mentions_virtual_environment_commands():
    expected_entries = [
        "source .venv/bin/activate",
        "deactivate",
    ]
    for entry in expected_entries:
        assert entry in README_TEXT


def test_readme_lists_test_lint_format_commands():
    commands = ["python -m pytest", "black .", "ruff check ."]
    for command in commands:
        assert command in README_TEXT


def test_readme_has_daily_workflow_section():
    assert "## 💼 Daily Workflow" in README_TEXT


def test_readme_contains_installation_verification():
    assert "Verify installation by running the primary test suite" in README_TEXT


def test_readme_contains_model_development_section():
    assert "Model Development" in README_TEXT


def test_readme_contains_feature_engineering_section():
    assert "Feature Engineering" in README_TEXT


def test_readme_contains_model_performance_section_or_metrics_table():
    has_section = "Model Performance" in README_TEXT
    has_metrics_table = "| Model | MSE | MAE | RMSE | R² |" in README_TEXT
    assert has_section or has_metrics_table


def test_readme_contains_ml_pipeline_run_instructions():
    required_snippets = [
        "Running the ML Pipeline",
        "python -m scripts.preprocessing",
        "python -m scripts.run_evaluation",
        "python -m scripts.run_serialization",
    ]
    for snippet in required_snippets:
        assert snippet in README_TEXT


def test_readme_contains_project_status_section():
    assert "Project Status" in README_TEXT


def test_all_required_phase2_headers_present():
    required_headers = [
        "Model Development",
        "Feature Engineering",
        "Model Performance",
        "Running the ML Pipeline",
        "Project Status",
    ]
    for header in required_headers:
        assert header in README_TEXT
