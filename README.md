# 🧬 Biohacking Personal Optimization Predictor

[![Project Status: Active](https://img.shields.io/badge/Project%20Status-Active-brightgreen)](https://shields.io/)
[![Build Status: Passing](https://img.shields.io/badge/Build-Passing-brightgreen)](https://shields.io/)
[![Code Style: Black](https://img.shields.io/badge/Code%20Style-Black-000000.svg)](https://black.readthedocs.io/en/stable/)
[![Linting: Ruff](https://img.shields.io/badge/Linting-Ruff-blue)](https://docs.astral.sh/ruff/)

---
<!-- TOC -->
## 📚 Table of Contents
  - [Overview](#overview)
  - [🔍 System Overview](#-system-overview)
  - [🏗️ Production Architecture](#️-production-architecture)
    - [Application API (FastAPI)](#application-api-fastapi)
    - [Model Service (FastAPI)](#model-service-fastapi)
  - [🗃️ Data Model (Planned Production Schema)](#️-data-model-planned-production-schema)
    - [Users](#users)
    - [Daily\_Entries](#daily_entries)
    - [Predictions](#predictions)
  - [Getting Started](#getting-started)
  - [Database Setup (PostgreSQL + Alembic)](#database-setup-postgresql--alembic)
    - [Configure `DATABASE_URL`](#configure-database_url)
    - [Contributor `.env` Setup (Required)](#contributor-env-setup-required)
    - [Install Dependencies](#install-dependencies)
    - [Run Migrations](#run-migrations)
    - [Table Descriptions](#table-descriptions)
  - [Authentication](#authentication)
    - [Auth Flow](#auth-flow)
    - [Required Environment Variables](#required-environment-variables)
    - [Example Requests](#example-requests)
  - [Daily Entries CRUD](#daily-entries-crud)
    - [Endpoints](#endpoints)
    - [Entry Fields](#entry-fields)
    - [`POST /entries` (Create)](#post-entries-create)
    - [`GET /entries` (List)](#get-entries-list)
    - [`GET /entries/{id}` (Retrieve One)](#get-entriesid-retrieve-one)
    - [`PUT /entries/{id}` (Update)](#put-entriesid-update)
    - [`DELETE /entries/{id}` (Delete)](#delete-entriesid-delete)
  - [Project Goals](#project-goals)
  - [Skills and Technologies Used](#skills-and-technologies-used)
  - [Code Quality and Style](#code-quality-and-style)
    - [How to Format Code](#how-to-format-code)
    - [How to Lint Code](#how-to-lint-code)
  - [All code should pass both Black formatting and Ruff linting before being committed.](#all-code-should-pass-both-black-formatting-and-ruff-linting-before-being-committed)
  - [Project Structure](#project-structure)
  - [Test-Driven Development Workflow](#test-driven-development-workflow)
  - [Dataset(s)](#datasets)
  - [💼 Work Session Guidelines](#-work-session-guidelines)
  - [🛤️ Project Roadmap](#️-project-roadmap)
  - [Model Development](#model-development)
  - [Feature Engineering](#feature-engineering)
  - [Model Performance](#model-performance)
  - [Running the ML Pipeline](#running-the-ml-pipeline)
  - [License](#license)
  - [Acknowledgments](#acknowledgments)
<!-- /TOC -->

---
## Overview

This project evolves into a deployable ML-backed system that generates personalized biohacking recommendations based on structured lifestyle inputs (sleep patterns, workout intensity, supplement intake, screen time, etc.).  
The long-term goal is a production-ready application where users persist data, receive predictions, and compare trends over time.

---

## 🔍 System Overview

Biohacking Optimizer is evolving into a production-ready ML-backed system with:

- Isolated model inference service
- Relational time-series user data tracking
- Versioned model serialization
- Test-driven backend architecture
- CI/CD automated validation
- Deployable multi-service infrastructure

---
## 🏗️ Production Architecture

```
┌───────────────┐
│     User      │
└───────┬───────┘
        │  HTTPS
        v
┌──────────────────────────────┐
│  Application API (FastAPI)   │
│  - Auth / Profiles           │
│  - Daily Entries CRUD        │
│  - Orchestrates Inference    │
└───────┬───────────────┬──────┘
        │               │
        │ Internal HTTP │
        v               v
┌─────────────────┐   ┌──────────────────────────┐
│  Model Service  │   │  PostgreSQL               │
│  (FastAPI)      │   │  - users                  │
│  - /predict     │   │  - daily_entries          │
│  - model_version│   │  - predictions            │
└─────────────────┘   └──────────────────────────┘
```
The API is the system of record; the model service is isolated for safe iteration and independent scaling.

Biohacking Optimizer is designed as a two-service system.
Designed to balance system stability with adaptable model iteration as new data sources and features are introduced.

### Application API (FastAPI)
- Handles authentication
- Persists user inputs in PostgreSQL
- Exposes CRUD endpoints for daily entries
- Orchestrates model inference

### Model Service (FastAPI)
- Loads serialized ML model
- Exposes `/predict` endpoint
- Returns inference results to Application API

The Application API communicates with the Model Service via internal HTTP.

This separation:
- Isolates model runtime from core application logic
- Enables safe model iteration without disrupting user-facing systems
- Supports independent scaling of inference workloads

---

## 🗃️ Data Model (Planned Production Schema)
The schema supports longitudinal analytics, model version tracking, and future wearable data integrations.

### Users
- id (UUID)
- email
- password_hash
- created_at

### Daily_Entries
- id (UUID)
- user_id (FK)
- date
- sleep_hours
- resting_heart_rate
- caffeine_mg
- steps
- subjective_energy
- created_at

### Predictions
- id (UUID)
- user_id (FK)
- entry_id (FK)
- predicted_energy_score
- model_version
- created_at

  ---

## Getting Started

Follow these steps to prepare a local development environment that mirrors the project's continuous workflow:

1. Clone the repository and enter the project root:
   ```bash
   git clone https://github.com/YOUR-USERNAME/biohacking-optimizer.git
   cd biohacking-optimizer
   ```
2. Create an isolated virtual environment:
   ```bash
   python3 -m venv .venv
   ```
3. Activate the virtual environment:
   ```bash
   source .venv/bin/activate
   ```
4. Install development dependencies:
   ```bash
   pip install -r requirements.txt
   ```
5. Verify installation by running the primary test suite:
   ```bash
   python -m pytest
   ```

Note: Depending on your system configuration, you may need to use `python3` instead of `python`, and `python3 -m pytest` instead of `pytest` when running commands. This is common on macOS systems where both Python 2 and Python 3 are installed.

---

## Database Setup (PostgreSQL + Alembic)

This project uses PostgreSQL for persistent application data and Alembic for schema migrations.

### Configure `DATABASE_URL`

1. Copy `.env.example` to `.env`.
2. Set your PostgreSQL connection string in `.env`:

```bash
DATABASE_URL=postgresql://user:password@localhost:5432/biohacking
```

The application and Alembic read the database connection from `DATABASE_URL` only. Do not hardcode credentials in code.

### Contributor `.env` Setup (Required)

Create your own local `.env` file using `.env.example` as the template:

```bash
cp .env.example .env
```

Set these values in your local `.env`:

- `DATABASE_URL`: Create a free PostgreSQL database at `neon.tech` and paste the connection string Neon provides.
- `SECRET_KEY`: Generate a strong secret with `openssl rand -hex 32` and use the output value.
- `ALGORITHM`: Use `HS256`.
- `ACCESS_TOKEN_EXPIRE_MINUTES`: Use `30`.

Important: `.env` is gitignored and must never be committed.

### Install Dependencies

Install project dependencies (including SQLAlchemy, Alembic, `psycopg2-binary`, and `python-dotenv`):

```bash
pip install -r requirements.txt
```

### Run Migrations

Generate a new migration after model changes:

```bash
alembic revision --autogenerate -m "describe change"
```

Apply migrations manually as a deployment/setup step:

```bash
alembic upgrade head
```

Note: migrations are not applied automatically by the codebase.

### Table Descriptions

- `users`: Stores user accounts (`email`) and audit timestamps.
- `daily_entries`: Stores daily biohacking inputs per user (sleep, workout intensity, supplements, screen time, stress, and entry date).
- `predictions`: Stores model prediction outputs and recommendations linked to a user and daily entry.

---

## Authentication

The API uses JWT-based authentication for user access.

### Auth Flow

1. Register a user with `POST /auth/register` (email + password).
2. Login with `POST /auth/login` using the same credentials.
3. Receive a JWT access token (`bearer` token).
4. Send the token in the `Authorization` header (`Bearer <token>`) to access protected routes such as `GET /auth/me`.

### Required Environment Variables

Add these values to `.env` (see `.env.example`):

```bash
DATABASE_URL=postgresql://user:password@localhost:5432/biohacking
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### Example Requests

Register:

```bash
curl -X POST http://127.0.0.1:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"StrongPass123!"}'
```

Login:

```bash
curl -X POST http://127.0.0.1:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"StrongPass123!"}'
```

Protected route (`/auth/me`) with token:

```bash
curl http://127.0.0.1:8000/auth/me \
  -H "Authorization: Bearer <access_token>"
```

---

## Daily Entries CRUD

All Daily Entries endpoints require authentication.

- Send `Authorization: Bearer <access_token>` on every request.
- Each user can only access their own entries.
- `403` is returned for entries owned by another user.
- `404` is returned when an entry does not exist.

## Daily Workflow

The intended loop is to submit a daily entry, review the resulting prediction/recommendation output, and use that feedback to plan the next day.

### Endpoints

- `POST /entries`: Create a new daily entry for the authenticated user.
- `GET /entries`: List all daily entries for the authenticated user.
- `GET /entries/{id}`: Retrieve one daily entry by ID (ownership enforced).
- `PUT /entries/{id}`: Replace/update a daily entry by ID (ownership enforced).
- `DELETE /entries/{id}`: Delete a daily entry by ID (ownership enforced).

### Entry Fields

Request body (`POST`, `PUT`) fields:

- `sleep_hours` (number)
- `workout_intensity` (string)
- `supplement_intake` (string or `null`)
- `screen_time` (number)
- `stress_level` (integer)
- `date` (ISO date string, `YYYY-MM-DD`)

Response body (`POST`, `GET`, `PUT`) fields:

- `id`
- `sleep_hours`
- `workout_intensity`
- `supplement_intake`
- `screen_time`
- `stress_level`
- `date`

### `POST /entries` (Create)

Example request:

```bash
curl -X POST http://127.0.0.1:8000/entries \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "date": "2026-02-20",
    "sleep_hours": 7.5,
    "workout_intensity": "moderate",
    "supplement_intake": "magnesium, vitamin d",
    "screen_time": 4.0,
    "stress_level": 3
  }'
```

Example response (`201 Created`):

```json
{
  "id": 1,
  "sleep_hours": 7.5,
  "workout_intensity": "moderate",
  "supplement_intake": "magnesium, vitamin d",
  "screen_time": 4.0,
  "stress_level": 3,
  "date": "2026-02-20"
}
```

### `GET /entries` (List)

Example request:

```bash
curl -X GET http://127.0.0.1:8000/entries \
  -H "Authorization: Bearer <access_token>"
```

Example response (`200 OK`):

```json
[
  {
    "id": 1,
    "sleep_hours": 7.5,
    "workout_intensity": "moderate",
    "supplement_intake": "magnesium, vitamin d",
    "screen_time": 4.0,
    "stress_level": 3,
    "date": "2026-02-20"
  },
  {
    "id": 2,
    "sleep_hours": 8.0,
    "workout_intensity": "high",
    "supplement_intake": "creatine",
    "screen_time": 2.5,
    "stress_level": 2,
    "date": "2026-02-21"
  }
]
```

### `GET /entries/{id}` (Retrieve One)

Example request:

```bash
curl -X GET http://127.0.0.1:8000/entries/1 \
  -H "Authorization: Bearer <access_token>"
```

Example response (`200 OK`):

```json
{
  "id": 1,
  "sleep_hours": 7.5,
  "workout_intensity": "moderate",
  "supplement_intake": "magnesium, vitamin d",
  "screen_time": 4.0,
  "stress_level": 3,
  "date": "2026-02-20"
}
```

### `PUT /entries/{id}` (Update)

Example request:

```bash
curl -X PUT http://127.0.0.1:8000/entries/1 \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "date": "2026-02-21",
    "sleep_hours": 8.25,
    "workout_intensity": "high",
    "supplement_intake": "creatine",
    "screen_time": 2.5,
    "stress_level": 1
  }'
```

Example response (`200 OK`):

```json
{
  "id": 1,
  "sleep_hours": 8.25,
  "workout_intensity": "high",
  "supplement_intake": "creatine",
  "screen_time": 2.5,
  "stress_level": 1,
  "date": "2026-02-21"
}
```

### `DELETE /entries/{id}` (Delete)

Example request:

```bash
curl -X DELETE http://127.0.0.1:8000/entries/1 \
  -H "Authorization: Bearer <access_token>"
```

Example response (`204 No Content`):

No response body is returned.

---

## Project Goals

- Build and deploy a production-grade ML system using a two-service FastAPI architecture.
- Persist user data and predictions in a relational PostgreSQL database.
- Deliver personalized biohacking recommendations via a versioned, isolated model inference service.
- Demonstrate end-to-end software engineering practices: TDD, CI/CD, authentication, and cloud deployment.

---

## Skills and Technologies Used

- **Backend:** Python, FastAPI (Application API + Model Service)
- **Database:** PostgreSQL
- **Machine Learning:** Scikit-Learn, Pandas, NumPy
- **Authentication:** JWT / OAuth2
- **Testing:** PyTest (TDD, 100% coverage)
- **Code Quality:** Black, Ruff
- **CI/CD:** GitHub Actions
- **Containerization:** Docker
- **Frontend:** Streamlit
- **Version Control:** Git, GitHub

---

## Code Quality and Style

This project follows professional Python code quality standards:

- **Formatting:** [Black](https://black.readthedocs.io/en/stable/) is used to automatically format all `.py` files.
- **Linting:** [Ruff](https://docs.astral.sh/ruff/) is used for ultra-fast linting and code quality checking.

### How to Format Code

Format all Python files in the project automatically:

```bash
black .
```

### How to Lint Code

Check all Python files for code quality issues:

```bash
ruff check .
```

Automatically fix certain linting issues:

```bash
ruff check . --fix
```

## All code should pass both Black formatting and Ruff linting before being committed.

## Project Structure

```
biohacking-optimizer/
│
├── api/                   # Application API (FastAPI) - auth, CRUD, orchestration
├── model_service/         # Model Service (FastAPI) - isolated inference
├── data/                  # Datasets (raw, interim, processed)
├── notebooks/             # Jupyter notebooks for EDA, modeling
├── scripts/               # Core utilities (preprocessing, modeling)
├── models/                # Serialized model artifacts (versioned)
├── dashboard/             # Streamlit frontend
├── tests/                 # Unit and integration tests (TDD)
├── .github/workflows/     # CI/CD pipelines
├── .gitignore
├── README.md
├── requirements.txt
└── .venv/
```

---

## Test-Driven Development Workflow

- Define expected behavior for each function or module.
- Write unit tests inside `/tests/`.
- Write the actual code to pass those tests.
- Refactor while keeping all tests green.
- Run full test suite regularly using:
  ```bash
  pytest
  ```

---

## Dataset(s)

- [x] Synthetic biohacking dataset (500+ rows with realistic distributions)
- [ ] Future: Personal health tracking data (Apple Health, Oura Ring)

---

## 💼 Daily Workflow

**Start a session** – run these commands from the repo root in sequence:
- `git pull` (when collaborating) to sync the latest changes.
- `python3 -m venv .venv && source .venv/bin/activate` to create/enter the virtual environment.
- `pip install -r requirements.txt` to install or refresh dependencies.
- `pytest` (or a focused test such as `pytest tests/test_data_generation.py`) to confirm the test suite is green before coding.

**Wrap up a session** – before you stop working:
- Stop any running services (press `Ctrl+C` on Streamlit/dev servers).
- Run `git status` to understand outstanding edits and decide whether to stage or stash them.
- `deactivate` to leave the virtual environment.
- (Optional) `git diff`/`git diff --staged` plus `git commit` once you are ready to capture your progress.

## 🛤️ Project Roadmap

- [x] Phase 1: Foundation & Data
  - [x] Generate synthetic biohacking dataset
  - [x] Set up data versioning and storage structure
  - [x] Exploratory Data Analysis (EDA)
  - [x] Document data schema and feature descriptions
  - [x] Update README
- [x] Phase 2: ML Pipeline
  - [x] Feature engineering & preprocessing
  - [x] Model experimentation (multiple algorithms)
  - [x] Model evaluation & selection
  - [x] Model serialization
  - [x] Update README
- [ ] Phase 3: Backend API (In Progress)
  - [x] FastAPI setup & project structure
  - [x] PostgreSQL setup & database schema migrations
  - [x] User authentication (JWT/OAuth2)
  - [x] Daily entries CRUD endpoints
  - [ ] Create prediction endpoint
  - [ ] Application API orchestration - connect to Model Service
  - [ ] Add input validation
  - [ ] API testing (pytest)
  - [ ] Update README
- [ ] Phase 4: CI/CD
  - [ ] GitHub Actions for automated testing
  - [ ] Linting/formatting checks in CI
  - [ ] Model testing in CI pipeline
  - [ ] Update README
- [ ] Phase 5: Frontend Dashboard
  - [ ] Streamlit app structure
  - [ ] Input form for user data
  - [ ] Display predictions & visualizations
  - [ ] Connect to FastAPI backend
  - [ ] Update README
- [ ] Phase 6: Deployment
  - [ ] Deploy FastAPI to Render/Railway
  - [ ] Deploy Streamlit to Streamlit Cloud
  - [ ] Integration testing
  - [ ] Update README
- [ ] Phase 7: Real Data Integration
  - [ ] Apple Health export integration
  - [ ] Oura API integration
  - [ ] Compare synthetic vs real model performance
  - [ ] Update README
- [ ] Phase 8: Final Sweep
  - [ ] Code review and refactoring
  - [ ] Security audit
  - [ ] Performance testing
  - [ ] Documentation audit
  - [ ] Accessibility review
  - [ ] Final README polish
- [ ] Phase 9: HIPAA Compliance
  - [ ] HIPAA compliance assessment and gap analysis
  - [ ] Data encryption at rest and in transit
  - [ ] Access controls and authentication
  - [ ] Audit logging and monitoring
  - [ ] Data privacy and anonymization
  - [ ] Business Associate Agreement (BAA) preparation
  - [ ] Incident response and breach notification plan
  - [ ] HIPAA compliance training documentation
  - [ ] Update README

---

## Model Development

Phase 2 model development followed a Test-Driven Development (TDD) workflow: tests were written first for feature engineering, experimentation, evaluation, and serialization before implementation was added.

The ML experimentation pipeline trained and compared 3 regression algorithms on the synthetic biohacking dataset:

- Linear Regression
- Random Forest
- Gradient Boosting

Model comparison used 5-fold cross-validation in addition to holdout evaluation metrics (MSE, MAE, RMSE, and R²).

Best model selected (Phase 2, synthetic dataset): **Linear Regression** with **R² = 0.1819**.

This relatively low R² is expected for early synthetic data and should improve after Phase 7 (real data integration) when the model is trained on richer user-generated signals.

---

## Feature Engineering

Feature selection and modeling inputs are aligned with the documented schema in `data/schema.md`.

Phase 2 preprocessing decisions (documented for the `scripts/preprocessing.py` pipeline) include:

- Numeric feature scaling prior to model training to keep feature magnitudes comparable.
- Categorical encoding for any non-numeric fields included in the training set.
- Consistent train/inference preprocessing so serialized pipelines can reproduce transforms exactly.

Derived features created during feature engineering are generated from the core biohacking inputs (sleep, activity, hydration, caffeine, and related signals) to support stronger predictive patterns as the dataset matures.

---

## Model Performance

Phase 2 evaluation summary from `models/evaluation_report.md`:

| Model | MSE | MAE | RMSE | R² |
|---|---|---|---|---|
| Linear Regression | 1.5341 | 1.0108 | 1.2386 | 0.1819 |
| Gradient Boosting | 1.6527 | 1.0652 | 1.2856 | 0.1187 |
| Random Forest | 1.6928 | 1.0631 | 1.3011 | 0.0973 |

---

## Running the ML Pipeline

Run the Phase 2 ML workflow in order:

```bash
# Feature engineering
python -m scripts.preprocessing

# Model experimentation
python -m scripts.run_evaluation

# Serialize best model
python -m scripts.run_serialization
```

---

## License

This project is open-source and available under the [MIT License](LICENSE).

---

## Acknowledgments

- Open-source datasets and contributors.
- Inspiration from the biohacking, personal optimization, and data science communities.
