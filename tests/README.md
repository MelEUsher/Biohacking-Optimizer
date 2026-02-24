# Test Suite Guide

## Overview

The `tests/` directory contains the automated checks for the Biohacking Optimizer project.
Tests are grouped by feature area:

- API endpoint and integration behavior (`test_api.py`, `test_auth.py`, `test_entries.py`, etc.)
- Data pipeline utilities (generation, cleaning, feature engineering, EDA)
- Model experimentation, evaluation, and serialization
- Project documentation and schema validation
- Database structure and connectivity checks

`tests/test_api.py` is the consolidated API integration suite added for Phase 3 Issue #14. It focuses on coverage gaps and end-to-end behavior across endpoints without duplicating the existing endpoint-specific tests.

## Test File Coverage Map

- `tests/test_api.py`: Consolidated API integration tests for cross-endpoint flows and uncovered edge cases (end-to-end register/login/create entry/predict flow, predict service unavailable, auth token user-missing case, entries ordering, orchestration connection error, predict unknown-field validation).
- `tests/test_api_health.py`: `/health` endpoint response status and payload basics.
- `tests/test_auth.py`: `/auth/register`, `/auth/login`, and `/auth/me` endpoint behavior, password hashing, JWT auth, invalid/expired token handling.
- `tests/test_entries.py`: `/entries` CRUD endpoints (create/list/get/update/delete), auth requirements, ownership checks, and core error handling.
- `tests/test_orchestration.py`: Entry creation orchestration with the Model Service (`api.utils.model_client` integration path), including timeout and service-error scenarios.
- `tests/test_predict_endpoint.py`: `/predict` endpoint happy path and core request validation outcomes.
- `tests/test_input_validation.py`: Pydantic request validation edge cases for predict and daily entry payloads (ranges, types, required fields, formatting).
- `tests/test_database.py`: Database connection behavior, metadata/table presence, and schema column expectations.
- `tests/test_data_structure.py`: Repository data directory structure and tracked/ignored file expectations.
- `tests/test_data_generation.py`: Synthetic dataset generation quality, ranges, schema, correlations, and CSV persistence.
- `tests/test_data_cleaning.py`: Data cleaning helpers (null handling, duplicate removal, imputation).
- `tests/test_feature_engineering.py`: Feature engineering helpers and preprocessing pipeline transformations.
- `tests/test_eda_utils.py`: EDA summary statistics, correlations, and plotting helper outputs.
- `tests/test_model_experiments.py`: Model training, prediction, evaluation, cross-validation, and supported model smoke tests.
- `tests/test_model_evaluation.py`: Model evaluation utilities, report generation, and model comparison selection logic.
- `tests/test_model_serialization.py`: Model/pipeline save/load behavior, filenames, and error handling for missing artifacts.
- `tests/test_schema.py`: Schema file presence, completeness, and format requirements.
- `tests/test_readme.py`: Root `README.md` content/section coverage requirements.

## How To Run Tests

Run the full test suite:

```bash
.venv/bin/python -m pytest -v
```

Run a single test file:

```bash
.venv/bin/python -m pytest -v tests/test_api.py
```

Run API coverage report:

```bash
.venv/bin/python -m pytest --cov=api --cov-report=term-missing
```

Collect tests without executing them (useful for auditing coverage layout):

```bash
.venv/bin/python -m pytest --co -q
```
