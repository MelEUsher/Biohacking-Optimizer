from pathlib import Path

README_PATH = Path(__file__).resolve().parents[1] / "README.md"
README_TEXT = README_PATH.read_text(encoding="utf-8")


def test_readme_has_api_documentation_section_or_equivalent():
    has_api_doc_heading = "API Documentation" in README_TEXT
    has_equivalent_sections = all(
        section in README_TEXT
        for section in ["## Authentication", "## Daily Entries CRUD"]
    )
    assert has_api_doc_heading or has_equivalent_sections


def test_readme_includes_uvicorn_run_instructions():
    assert "uvicorn" in README_TEXT
    assert "api.main:app" in README_TEXT


def test_readme_contains_example_api_requests():
    required_snippets = [
        "curl -X POST http://127.0.0.1:8000/auth/register",
        "curl -X POST http://127.0.0.1:8000/auth/login",
        "curl -X POST http://127.0.0.1:8000/entries",
    ]
    for snippet in required_snippets:
        assert snippet in README_TEXT


def test_readme_contains_api_testing_instructions():
    assert "tests/test_api.py" in README_TEXT
    assert "pytest" in README_TEXT


def test_readme_project_status_reflects_phase3_complete_and_phase4_next():
    assert "- [x] Phase 3: Backend API" in README_TEXT
    assert "Phase 3: Backend API (In Progress)" not in README_TEXT
    assert "- [ ] Phase 4: CI/CD" in README_TEXT
    assert "Phase 4: CI/CD (Next)" in README_TEXT or "Next: Phase 4" in README_TEXT
