# Data Scientist/Engineering Interview Exercises

This directory contains two exercises evaluating your proficiency in advanced SQL (Recursive CTEs, window functions, date functions), Python/Pandas (data manipulation, decile binning), ML evaluation metrics i.e lift, and communicating churn-related insights to stakeholders.

## Setup

1. **Create a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Verify your environment:**
   ```bash
   python --version  # Should be Python 3.12
   ```

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

### How to Run
```bash
python R51795/01_wau_calculation.py
```

### Topics Covered
- SQL window functions and CTEs
- Time-series aggregation (weekly bucketing)
- Anomaly detection patterns
- SQLite date functions

---

## Exercise 2: Score Calibration & Lift Analysis

### Description
Evaluate a churn prediction model by analyzing how well predicted risk scores align with actual churn outcomes. Calculate key metrics like calibration curves, lift, and customer segmentation.

**Key Metrics:**
- **Baseline Rate**: Overall churn rate
- **Calibration by Decile**: Actual churn rate within each score decile
- **Lift**: How much better the model performs vs. random targeting
- **Capture**: Percentage of churns caught in top 10% riskiest accounts

### Files
- `02_score_callibration.py` - Python script for calibration analysis
- `exercise_setup.py` - Data generation function

### How to Run
```bash
python R51795/02_score_callibration.py
```

### Topics Covered
- Model calibration and evaluation
- Risk stratification and segmentation
- Pandas data manipulation
- Business metrics for ML models (lift, capture rate)

---

## Exercise Tasks

For each exercise, you'll need to:

1. **Review the starter code** - Understand the data schema and expected outputs
2. **Fill in missing implementation** - Complete TODO sections or fix broken logic
4. **Explain your approach** - Be ready to discuss design decisions and trade-offs

## Common Issues

### Database Not Found
If you see `no such table: events`, run the setup first:
```python
from exercise_setup import setup_events_database
conn = setup_events_database()
```

### Import Errors
Make sure you're running from the correct directory:
```bash
cd /workspaces/sketchup-interview-exercises
python R51795/01_wau_calculation.py
```

## Questions?

During the interview, feel free to ask clarifying questions about:
- Business context and use cases
- Performance considerations
- Edge cases and assumptions
- Alternative approaches

Good luck! 🚀
