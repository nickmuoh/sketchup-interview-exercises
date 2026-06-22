# Data Engineer - Customer Insights & Analytics Interview Exercises

## Setup

1. **Create a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies:**
   ```bash
   pip install -r R54035/requirements.txt
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
python R54035/01_wau_calculation.py
```

### Verify Your Solution
After completing the SQL blanks, run the test suite from the repo root to check your work:
```bash
python -m unittest R54035.test_01_wau_calculation -v
```
All 20 tests should pass when your implementation is correct.

### Exercise Tasks

For each exercise, you'll need to:

1. **Review the starter code** - Understand the data schema and expected outputs
2. **Fill in missing implementation** - Complete TODO sections or fix broken logic
3. **Explain your approach** - Be ready to discuss design decisions and trade-offs

---

## Exercise 2: Viral Loop Analysis

### Description
Build a SQL query to calculate **Monthly Net-New Viral Lift**: the average number of unknown users brought into the ecosystem per unique shared file, per month. Also derive a Data Quality flag to verify that role counts are internally consistent.

**Key Metrics:**
- **Monthly Unique Files**: Count of distinct files shared per month
- **Net-New Viral Lift**: Average unknown contacts invited per unique shared file
- **Instrumentation Valid**: Binary flag — 1 if role counts sum to total recipients, 0 if not

### Files
- `02_viral_lift.sql` - SQL query implementation (fill in the blanks)
- `02_viral_lift.py` - Python script to execute the query
- `exercise_setup.py` - Database setup (includes `setup_product_telemetry_database`)

### Telemetry Schema

**Table:** `product_telemetry`

| Column | Type | Description |
|---|---|---|
| `event_time` | TEXT | Timestamp (YYYY-MM-DD HH:MM:SS) |
| `event_type` | TEXT | e.g. `share_invite_sent` |
| `event_properties` | TEXT | JSON string (see structure below) |

**`event_properties` JSON structure:**
```json
{
  "file_id": "skp-123-abc",
  "share_metadata": {
    "recipients_count": 5,
    "role_distribution": { "editors": 2, "commenters": 1, "viewers": 2 },
    "identity_stats":    { "known_contacts": 3, "unknown_contacts": 2 }
  }
}
```

### How to Run
```bash
python R54035/02_viral_lift.py
```

### Verify Your Solution
After completing the SQL blanks, run the test suite from the repo root to check your work:
```bash
python -m unittest R54035.test_02_viral_lift -v
```
All 13 tests should pass when your implementation is correct.

---

## Exercise 3: Subscription State Reconstruction (SCD2)

### Description
Build a SQL query to reconstruct a clean subscription history from a raw event-sourced entitlement ledger. The goal is to derive continuous effective date ranges for active entitlement periods while preserving revocation gaps and excluding terminal states from the final output.

**Key Concepts:**
- **State Boundary Detection**: Use a window function to look ahead to the next entitlement action for the user
- **SCD Type 2 Windows**: Convert each discrete state into an effective start and end date pair
- **Optimistic Open End**: Use `2050-12-31` when a user has no later entitlement event
- **Safety Filtering**: Remove any rows where the computed start date would exceed the end date

### Files
- `03_subscription_state_reconstruction.sql` - SQL query implementation (fill in the blanks)
- `03_subscription_state_reconstruction.py` - Python script to execute the query
- `exercise_setup.py` - Database setup (includes `setup_entitlements_database`)

### Entitlements Schema

**Table:** `ems_events_projected`

| Column | Type | Description |
|---|---|---|
| `user_id` | INTEGER | User identifier |
| `entitlement_sku` | TEXT | SKU in effect at the time of the event |
| `action` | TEXT | One of `assigned`, `upgraded`, `downgraded`, `revoked`, `expired` |
| `event_time` | TEXT | Timestamp (`YYYY-MM-DD HH:MM:SS`) |

### How to Run
```bash
python R54035/03_subscription_state_reconstruction.py
```

### Verify Your Solution
After completing the SQL blanks, run the test suite from the repo root to check your work:
```bash
python -m unittest R54035.test_03_subscription_state_reconstruction -v
```
All 16 tests should pass when your implementation is correct.

---

## Questions?

During the interview, feel free to ask clarifying questions about:
- Business context and use cases
- Performance considerations
- Edge cases and assumptions
- Alternative approaches

Good luck! 🚀
