# Data Scientist/Engineering Interview Exercises

## Setup

1. **Create a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies:**
   ```bash
   pip install -r R51795/requirements.txt
   ```

3. **Verify your environment:**
   ```bash
   python --version  # Should be Python 3.12
   ```

---

## Exercises

## Exercise 1: Weekly Active Users (WAU) Calculation

### Description
Build a SQL query to calculate Weekly Active Users (WAU) and detect usage anomalies. The goal is to identify accounts where a single feature dominates activity (e.g., potential bot behavior or API abuse).

**Key Metrics:**
- **WAU**: Count of distinct active users per account per week
- **Top Feature Share**: Percentage of events dominated by the most-used feature
- **Anomaly Flag**: Binary flag when feature domination exceeds 70%

### Files
- `01_wau_calculation.sql` - SQL query implementation
- `01_wau_calculation.py` - Python script to execute the query
- `exercise_setup.py` - Database setup with sample events data


### Events Schema
- `account_id` (INTEGER): Account identifier
- `user_id` (INTEGER): User identifier
- `event_time` (TEXT): Timestamp of the event (YYYY-MM-DD HH:MM:SS)
- `event_type` (TEXT): Type of event (e.g., login, dashboard_view, report_export, api_call)

### How to Run
```bash
python R51795/01_wau_calculation.py
```

### Verify Your Solution
After completing the SQL blanks, run the test suite from the repo root to check your work:
```bash
python -m unittest R51795.test_01_wau_calculation -v
```
All 20 tests should pass when your implementation is correct.


## Exercise 2: Score Calibration & Lift Analysis

### Description
Evaluate a churn prediction model by analyzing how well predicted risk scores align with actual churn outcomes. Calculate key metrics like calibration curves, lift, and customer segmentation.

**Key Metrics:**
- **Baseline Rate**: Overall churn rate
- **Calibration by Decile**: Actual churn rate within each score decile
- **Lift**: How much better the model performs vs. random targeting
- **Capture**: Percentage of churns caught in top 10% riskiest accounts

### Files
- `02_score_calibration.py` - Python script for calibration analysis
- `exercise_setup.py` - Data generation function for synthetic churn data

### Data Schema

**Scores Dataframe Schema:**
- `account_id` (INTEGER): Account identifier
- `predict_period_end` (TEXT): End date of the prediction period (YYYY-MM-DD)
- `score` (FLOAT): Predicted churn risk score between 0 and 1

**Labels Dataframe Schema:**
- `account_id` (INTEGER): Account identifier
- `predict_period_end` (TEXT): End date of the prediction period (YYYY-MM-DD)
- `churn_label` (INTEGER): Actual churn outcome (1 = churned, 0 = retained)

### How to Run
```bash
python R51795/02_score_callibration.py
```

### Verify Your Solution
After completing the blanks in `02_score_callibration.py`, run the test suite from the repo root to check your work:
```bash
python -m unittest R51795.test_02_score_calibration -v
```
All 20 tests should pass when your implementation is correct.

### Exercise Tasks

For each exercise, you'll need to:

1. **Review the starter code** - Understand the data schema and expected outputs
2. **Fill in missing implementation** - Complete TODO sections or fix broken logic
3. **Explain your approach** - Be ready to discuss design decisions and trade-offs

## Questions?

During the interview, feel free to ask clarifying questions about:
- Business context and use cases
- Performance considerations
- Edge cases and assumptions
- Alternative approaches

Good luck! 🚀
