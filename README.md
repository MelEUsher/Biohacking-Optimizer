# 🧬 Biohacking Personal Optimization Predictor

[![Project Status: Active](https://img.shields.io/badge/Project%20Status-Active-brightgreen)](https://shields.io/)
[![Build Status: Passing](https://img.shields.io/badge/Build-Passing-brightgreen)](https://shields.io/)
[![Code Style: Black](https://img.shields.io/badge/Code%20Style-Black-000000.svg)](https://black.readthedocs.io/en/stable/)
[![Linting: Ruff](https://img.shields.io/badge/Linting-Ruff-blue)](https://docs.astral.sh/ruff/)

---

<!-- TOC -->
## 📚 Table of Contents

- [🧬 Biohacking Personal Optimization Predictor](#-biohacking-personal-optimization-predictor)
  - [📚 Table of Contents](#-table-of-contents)
  - [Overview](#overview)
  - [Getting Started](#getting-started)
  - [Project Goals](#project-goals)
  - [Skills and Technologies Used](#skills-and-technologies-used)
  - [Code Quality and Style](#code-quality-and-style)
    - [How to Format Code](#how-to-format-code)
    - [How to Lint Code](#how-to-lint-code)
  - [All code should pass both Black formatting and Ruff linting before being committed.](#all-code-should-pass-both-black-formatting-and-ruff-linting-before-being-committed)
  - [Project Structure](#project-structure)
  - [Test-Driven Development Workflow](#test-driven-development-workflow)
  - [Dataset(s)](#datasets)
  - [How to Run the Project](#how-to-run-the-project)
    - [1. Clone the Repository](#1-clone-the-repository)
    - [2. Set Up the Virtual Environment](#2-set-up-the-virtual-environment)
    - [3. Install Required Packages](#3-install-required-packages)
    - [4. Running Tests](#4-running-tests)
    - [5. Running the Streamlit App (Potential for Later)](#5-running-the-streamlit-app-potential-for-later)
  - [Daily Workflow](#daily-workflow)
  - [💼 Work Session Guidelines](#-work-session-guidelines)
  - [License](#license)
  - [Acknowledgments](#acknowledgments)
  - [✨ Project Status](#-project-status)
  - [🛤️ Roadmap](#️-roadmap)
    - [Core Development](#core-development)
    - [Machine Learning](#machine-learning)
    - [Dashboard Development](#dashboard-development)
    - [Code Quality and Maintenance](#code-quality-and-maintenance)
<!-- /TOC -->

---
## Overview

This project builds a machine learning model that predicts personalized biohacking recommendations based on individual lifestyle data inputs (sleep patterns, workout intensity, supplement intake, screen time, etc.).  
It follows a **Test-Driven Development (TDD)** approach: writing tests first, then building the functionality to pass those tests.

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

- Predict supplement regimens and habit optimizations based on user data.
- Visualize the relationships between health behaviors and biohacking goals.
- Build the project using a **Test-Driven Development** workflow to ensure reliability, maintainability, and professional-grade code quality.
- Deploy an interactive Streamlit dashboard for user inputs and predictions.

---

## Skills and Technologies Used

- **Programming Languages:** Python
- **Data Analysis:** Pandas, NumPy
- **Machine Learning:** Scikit-Learn
- **Testing Framework:** PyTest
- **Formatting Tool:** Black (auto-formatting Python code to PEP8 standards)
- **Linting Tool:** Ruff (fast Python linter and code quality checker)
- **Data Visualization:** Matplotlib, Seaborn
- **(Front-End):** Streamlit
- **Version Control:** Git, GitHub
- **Containerization:** Docker (for deployment)

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
├── data/                  # Datasets (raw and processed)
├── notebooks/             # Jupyter notebooks for EDA, modeling
├── scripts/               # Core functionality (cleaning, modeling)
├── tests/                 # Unit tests (TDD workflow)
├── models/                # Saved models (pickle files)
├── dashboard/             # Streamlit app (optional)
├── .gitignore             # Ignore venv/ and other unnecessary files
├── README.md              # Project overview
├── requirements.txt       # Python libraries needed
└── venv/                  # Local virtual environment (not pushed to GitHub)
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

### Machine Learning
- [ ] Build preprocessing pipeline (scaling, encoding, feature creation)
- [ ] Train multiple algorithms (Linear Regression, Random Forest, Gradient Boosting)
- [ ] Perform cross-validation and hyperparameter tuning
- [ ] Evaluate model performance (MSE, MAE, R²)
- [ ] Select best model based on metrics and business requirements
- [ ] Serialize trained model and preprocessing pipeline

### Dashboard Development 
- [ ] Set up FastAPI backend with prediction endpoint
- [ ] Implement input validation using Pydantic
- [ ] Develop Streamlit dashboard for user input
- [ ] Add visualizations for predictions and insights
- [ ] Connect frontend to FastAPI backend
- [ ] Deploy API and dashboard to cloud

### Code Quality and Maintenance
- [x] Maintain 100% passing unit tests
- [x] Maintain formatting and linting standards across all code
- [x] Update README and documentation as project evolves
- [ ] Set up GitHub Actions for CI/CD
- [ ] Add automated testing and code quality checks
- [ ] Deploy to production with monitoring

---