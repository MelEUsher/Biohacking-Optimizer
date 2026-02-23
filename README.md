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
- [🗃️ Data Model](#️-data-model-planned-production-schema)
- [Getting Started](#getting-started)
- [Project Goals](#project-goals)
- [Skills and Technologies Used](#skills-and-technologies-used)
- [Code Quality and Style](#code-quality-and-style)
- [Project Structure](#project-structure)
- [Test-Driven Development Workflow](#test-driven-development-workflow)
- [Dataset(s)](#datasets)
- [How to Run the Project](#how-to-run-the-project)
- [Daily Workflow](#daily-workflow)
- [💼 Work Session Guidelines](#-work-session-guidelines)
- [License](#license)
- [Acknowledgments](#acknowledgments)
- [✨ Project Status](#-project-status)
- [🛤️ Roadmap](#️-roadmap)
  - [Core Development](#core-development)
  - [Backend & API](#backend--api)
  - [Infrastructure & Deployment](#infrastructure--deployment)
  - [Frontend](#frontend)
  - [Code Quality and Maintenance](#code-quality-and-maintenance)
- [🗺️ Production Plan](#️-production-plan)
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
        │               │
        v               v
┌─────────────────┐   ┌──────────────────────────┐
│ Model Service    │   │ PostgreSQL                │
│ (FastAPI)        │   │ - users                   │
│ - /predict       │   │ - daily_entries           │
│ - model_version  │   │ - predictions             │
└─────────────────┘   └──────────────────────────┘
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

## How to Run the Project

### 1. Clone the Repository

```bash
git clone https://github.com/YOUR-USERNAME/biohacking-optimizer.git
cd biohacking-optimizer
```

### 2. Set Up the Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Required Packages

```bash
pip install -r requirements.txt
```

### 4. Running Tests

```bash
pytest
```

### 5. Running the Streamlit App (Potential for Later)

```bash
streamlit run dashboard/app.py
```

## Daily Workflow

Maintain focus on Fast Feedback and consistent quality by following this daily rhythm:

- Activate the shared virtual environment (start a session):
  ```bash
  source .venv/bin/activate
  ```
- Deactivate the environment when you stop working (end a session):
  ```bash
  deactivate
  ```
- Run the core test suite:
  ```bash
  python -m pytest
  ```
- Format code before committing:
  ```bash
  black .
  ```
- Lint with Ruff before pushing:
  ```bash
  ruff check .
  ```

## 💼 Work Session Guidelines

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

---

## License

This project is open-source and available under the [MIT License](LICENSE).

---

## Acknowledgments

- Open-source datasets and contributors.
- Inspiration from the biohacking, personal optimization, and data science communities.

---


## ✨ Project Status

> **Phase 1: Foundation & Data - COMPLETE ✅**
> 
> ✅ Synthetic biohacking dataset generated (500+ rows)  
> ✅ Data versioning structure (raw/interim/processed directories)  
> ✅ Exploratory Data Analysis completed with reusable utilities  
> ✅ Data schema documented (feature descriptions, types, ranges)  
> ✅ README updated with setup and workflow instructions  
> ✅ All Phase 1 tests passing (25/25)
> 
> 🎯 **Next: Phase 2 - ML Pipeline**
> - Feature engineering & preprocessing
> - Model experimentation (multiple algorithms)
> - Model evaluation & selection
> - Model serialization for deployment

---

## 🛤️ Roadmap

The following milestones are planned to expand the Biohacking Personal Optimization Predictor project:

### Core Development
- [x] Set up virtual environment, GitHub repo, and project structure
- [x] Configure Pytest for Test-Driven Development (TDD)
- [x] Configure Black for code formatting and Ruff for linting
- [x] Generate synthetic biohacking dataset
- [x] Set up data versioning/storage structure
- [x] Build data cleaning utilities with 100% test coverage
- [x] Perform Exploratory Data Analysis (EDA)
- [x] Document data schema and feature descriptions
- [x] Update README with setup and session management
- [ ] Feature engineering & preprocessing pipeline
- [ ] Model experimentation (multiple algorithms)
- [ ] Model evaluation & selection
- [ ] Model serialization for deployment

### Backend & API
- [ ] Feature engineering & preprocessing pipeline
- [ ] Model experimentation and evaluation (MSE, MAE, R²)
- [ ] Model serialization and versioning
- [ ] Application API (FastAPI) — auth, CRUD, PostgreSQL integration
- [ ] Model Service (FastAPI) — isolated inference endpoint
- [ ] Input validation using Pydantic

### Infrastructure & Deployment
- [ ] Set up GitHub Actions for CI/CD
- [ ] Automated testing and code quality checks in CI
- [ ] Containerize services with Docker
- [ ] Deploy Application API and Model Service to cloud
- [ ] Deploy Streamlit frontend

### Frontend
- [ ] Streamlit dashboard for user input and predictions
- [ ] Visualizations for trends and insights
- [ ] Connect frontend to Application API

### Code Quality and Maintenance
- [x] Maintain 100% passing unit tests
- [x] Maintain formatting and linting standards across all code
- [x] Update README and documentation as project evolves
- [ ] Set up GitHub Actions for CI/CD
- [ ] Add automated testing and code quality checks
- [ ] Deploy to production with monitoring

---

---

## 🗺️ Production Plan

This project follows a structured 9-phase development plan. Each phase uses Test-Driven Development (TDD) with full test coverage before implementation.

| Phase | Focus | Status |
|-------|-------|--------|
| 1 | Foundation & Data | ✅ Complete |
| 2 | ML Pipeline | 🔄 In Progress |
| 3 | Backend API | ⏳ Planned |
| 4 | CI/CD | ⏳ Planned |
| 5 | Frontend Dashboard | ⏳ Planned |
| 6 | Deployment | ⏳ Planned |
| 7 | Real Data Integration | ⏳ Planned |
| 8 | Final Sweep | ⏳ Planned |
| 9 | HIPAA Compliance | ⏳ Planned |
