# 🧬 Biohacking Personal Optimization Predictor

## Overview
This project builds a machine learning model that predicts personalized biohacking recommendations based on individual lifestyle data inputs (sleep patterns, workout intensity, supplement intake, screen time, etc.).  
It follows a **Test-Driven Development (TDD)** approach: writing tests first, then building the functionality to pass those tests.

---

## Project Goals
- Predict supplement regimens and habit optimizations based on user data.
- Visualize the relationships between health behaviors and biohacking goals.
- Build the project using a **Test-Driven Development** workflow to ensure reliability, maintainability, and professional-grade code quality.
- (Stretch Goal) Deploy an interactive Streamlit dashboard for user inputs and predictions.

---

## Skills and Technologies Used
- **Programming Languages:** Python
- **Data Analysis:** Pandas, NumPy
- **Machine Learning:** Scikit-Learn
- **Testing Framework:** PyTest
- **Data Visualization:** Matplotlib, Seaborn
- **(Optional Front-End):** Streamlit

---

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
- [ ] Public health/lifestyle datasets (Kaggle, UCI ML Repo, PhysioNet)
- [ ] Optional: Personal health tracking data (exported from devices or medical logs).

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

### 5. Running the Streamlit App (Optional Later)
```bash
streamlit run dashboard/app.py
```

---

## License
This project is open-source and available under the [MIT License](LICENSE).

---

## Acknowledgments
- Open-source datasets and contributors.
- Inspiration from the biohacking, personal optimization, and data science communities.

---

# ✨ Project Status
> 🚀 Initial project setup complete. 
> ✅ Virtual environment configured.  
> ✅ GitHub repository connected with clean, granular commits.  
> ✅ Project structure established with scripts/ and tests/ packages.  
> ✅ Pytest testing framework configured and auto-detected in VS Code.  
> ✅ First real TDD test and function (drop_missing_rows) implemented and passing.  
> 
> 🎯 Currently moving into Phase 2: expanding core data cleaning utilities and unit tests.

