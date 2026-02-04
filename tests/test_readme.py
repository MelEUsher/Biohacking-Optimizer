from pathlib import Path

README_PATH = Path(__file__).resolve().parents[1] / "README.md"
README_TEXT = README_PATH.read_text()


def test_readme_has_getting_started_section():
    assert "Getting Started" in README_TEXT


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
    assert "Daily Workflow" in README_TEXT


def test_readme_contains_installation_verification():
    assert "Verify installation" in README_TEXT
