import pandas as pd
import numpy as np
import sqlite3
from pathlib import Path
from contextlib import contextmanager


@contextmanager
def setup_events_database(db_path="events.db"):
    """
    Context manager that creates and populates a SQLite database with events data,
    then closes the connection on exit.

    Args:
        db_path: Path to the SQLite database file

    Yields:
        Connection object to the database
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Create table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS events (
            account_id INTEGER,
            user_id INTEGER,
            event_time TEXT,
            event_type TEXT
        )
    """)

    # Clear existing data if any
    cursor.execute("DELETE FROM events")

    # Insert data
    events_data = [
        # Account 1: Healthy "Power User" Account (High WAU, Balanced Feature Mix)
        # Week 1 (Starts 2024-07-01)
        (1, 101, "2024-07-02 10:00:00", "login"),
        (1, 101, "2024-07-02 10:05:00", "dashboard_view"),
        (1, 102, "2024-07-03 11:00:00", "report_export"),
        (1, 103, "2024-07-03 12:00:00", "login"),
        (1, 104, "2024-07-05 09:00:00", "login"),
        # Week 2 (Starts 2024-07-08)
        (1, 101, "2024-07-09 10:00:00", "login"),
        (1, 102, "2024-07-10 11:00:00", "report_export"),
        (1, 105, "2024-07-12 14:00:00", "dashboard_view"),
        (1, 105, "2024-07-12 14:10:00", "dashboard_view"),
        # Week 3 (Starts 2024-07-15)
        (1, 101, "2024-07-16 09:30:00", "login"),
        (1, 102, "2024-07-17 10:15:00", "dashboard_view"),
        (1, 103, "2024-07-18 11:00:00", "report_export"),
        (1, 106, "2024-07-19 13:00:00", "login"),
        (1, 106, "2024-07-20 14:00:00", "dashboard_view"),
        (1, 101, "2024-07-20 14:30:00", "report_export"),
        # Account 2: The "Anomaly" Account (Low WAU, 100% Feature Domination)
        # Week 1 (Normal behavior)
        (2, 201, "2024-07-02 09:00:00", "login"),
        (2, 202, "2024-07-02 09:05:00", "dashboard_view"),
        (2, 202, "2024-07-02 09:08:00", "report_export"),
        (2, 202, "2024-07-02 09:15:00", "report_export"),
        # Week 2 (Anomaly - Script abuse?)
        (2, 201, "2024-07-09 08:00:00", "api_call"),
        (2, 201, "2024-07-09 08:01:00", "api_call"),
        (2, 201, "2024-07-09 08:02:00", "api_call"),
        (2, 201, "2024-07-09 08:03:00", "api_call"),
        (2, 201, "2024-07-09 08:04:00", "api_call"),
        (2, 201, "2024-07-09 08:05:00", "api_call"),
        (2, 201, "2024-07-09 08:06:00", "api_call"),
        (2, 201, "2024-07-09 08:07:00", "api_call"),
        (2, 201, "2024-07-10 09:00:00", "login"),
        (2, 202, "2024-07-11 10:00:00", "dashboard_view"),
        (2, 202, "2024-07-12 11:00:00", "report_export"),
        # Week 3 (Return to normal)
        (2, 201, "2024-07-16 09:00:00", "login"),
        (2, 202, "2024-07-17 10:00:00", "dashboard_view"),
        (2, 203, "2024-07-18 11:00:00", "report_export"),
    ]

    cursor.executemany("INSERT INTO events VALUES (?, ?, ?, ?)", events_data)

    conn.commit()
    try:
        yield conn
    finally:
        conn.close()


def execute_sql_script(script_path, conn):
    """
    Execute a SQL script file against a SQLite database connection.

    Args:
        script_path: Path to the SQL script file
        conn: SQLite database connection object

    Returns:
        pandas DataFrame with the query results (if applicable)
    """
    sql_script = Path(script_path).read_text()

    cursor = conn.cursor()
    cursor.execute(sql_script)

    conn.commit()

    try:
        results = cursor.fetchall()
        if results:
            columns = [description[0] for description in cursor.description]
            return pd.DataFrame(results, columns=columns)
    except Exception:
        pass

    return None


def generate_churn_data(n=1000):
    np.random.seed(42)

    # 1. Generate Scores (skewed slightly towards lower scores)
    scores = np.random.beta(2, 5, n)

    # 2. Assign Labels based on Score (Higher score = Higher probability of churn)
    # If score > 0.7, 80% chance of churn. If score < 0.2, 1% chance.
    churn_prob = scores  # simplistic probability
    labels = [1 if (np.random.rand() < p) else 0 for p in churn_prob]

    scores_df = pd.DataFrame(
        {"account_id": range(n), "predict_period_end": "2024-07-01", "score": scores}
    )

    labels_df = pd.DataFrame(
        {
            "account_id": range(n),
            "predict_period_end": "2024-07-01",
            "churn_label": labels,
        }
    )

    return scores_df, labels_df
