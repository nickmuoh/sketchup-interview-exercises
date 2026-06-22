"""
Test suite for Exercise 1: Weekly Active Users (WAU) Calculation.

Run from the repo root:
    python -m unittest R51795.test_01_wau_calculation -v

All tests are based on the fixed sample dataset created by exercise_setup.py.
Passing every test means your SQL implementation is correct.
"""
import unittest
from pathlib import Path

import pandas as pd


from .utils import add_repo_to_path

_THIS_DIR, _ = add_repo_to_path(Path(__file__))

from exercise_setup import setup_events_database, execute_sql_script  # noqa: E402

SQL_PATH = _THIS_DIR / "01_wau_calculation.sql"


def setUpModule():
    """Run once for the entire module: create the DB and execute the SQL."""

    global _results

    with setup_events_database(db_path=":memory:") as conn:
        df = execute_sql_script(SQL_PATH, conn)

    if df is None:
        raise AssertionError(
            "execute_sql_script returned None — make sure your SQL ends with a SELECT statement."
        )

    _results = df


def _row(account_id: int, week_start: str) -> pd.Series:
    """Return the single result row for a given account and week."""

    mask = (_results["account_id"] == account_id) & (_results["week_start"] == week_start)
    matched = _results[mask]

    if len(matched) != 1:
        raise AssertionError(
            f"Expected exactly 1 row for account_id={account_id}, "
            f"week_start={week_start}, got {len(matched)}."
        )

    return matched.iloc[0]


# ---------------------------------------------------------------------------
# Schema tests
# ---------------------------------------------------------------------------

class TestOutputSchema(unittest.TestCase):
    REQUIRED_COLUMNS = {
        "account_id",
        "week_start",
        "wau",
        "top_feature_pct_share",
        "top_feature",
        "anomaly_flag",
    }

    def test_required_columns_present(self):
        missing = self.REQUIRED_COLUMNS - set(_results.columns)
        self.assertFalse(missing, f"Missing columns: {missing}")

    def test_row_count(self):
        """Exactly 6 rows: 2 accounts × 3 active weeks each."""
        self.assertEqual(
            len(_results), 6,
            f"Expected 6 rows (2 accounts × 3 weeks), got {len(_results)}.\n{_results}",
        )

    def test_two_accounts(self):
        self.assertEqual(set(_results["account_id"].unique()), {1, 2})

    def test_three_weeks_per_account(self):
        for acct in [1, 2]:
            weeks = _results[_results["account_id"] == acct]["week_start"].nunique()
            self.assertEqual(weeks, 3, f"Expected 3 weeks for account_id={acct}, got {weeks}.")

    def test_week_start_values(self):
        expected = {"2024-07-01", "2024-07-08", "2024-07-15"}
        actual = set(_results["week_start"].unique())
        self.assertEqual(actual, expected, f"Expected weeks {expected}, got {actual}.")


# ---------------------------------------------------------------------------
# WAU tests
# ---------------------------------------------------------------------------

class TestWAU(unittest.TestCase):
    """
    WAU = COUNT(DISTINCT user_id) per (account_id, week).
    Expected values derived from exercise_setup.py sample data.
    """

    def test_account1_week1_wau(self):
        # Users 101, 102, 103, 104 active in week of 2024-07-01
        self.assertEqual(_row(1, "2024-07-01")["wau"], 4)

    def test_account1_week2_wau(self):
        # Users 101, 102, 105 active in week of 2024-07-08
        self.assertEqual(_row(1, "2024-07-08")["wau"], 3)

    def test_account1_week3_wau(self):
        # Users 101, 102, 103, 106 active in week of 2024-07-15
        self.assertEqual(_row(1, "2024-07-15")["wau"], 4)

    def test_account2_week1_wau(self):
        # Users 201, 202 active in week of 2024-07-01
        self.assertEqual(_row(2, "2024-07-01")["wau"], 2)

    def test_account2_week2_wau(self):
        # Users 201, 202 active in week of 2024-07-08 (api abuse by 201)
        self.assertEqual(_row(2, "2024-07-08")["wau"], 2)

    def test_account2_week3_wau(self):
        # Users 201, 202, 203 active in week of 2024-07-15
        self.assertEqual(_row(2, "2024-07-15")["wau"], 3)


# ---------------------------------------------------------------------------
# Top-feature share tests
# ---------------------------------------------------------------------------

class TestTopFeatureShare(unittest.TestCase):
    """
    top_feature_pct_share = events_of_top_feature / total_events for that week.
    """

    def test_account1_week1_share(self):
        # login: 3 of 5 events → 0.60
        share = _row(1, "2024-07-01")["top_feature_pct_share"]
        self.assertAlmostEqual(share, 0.60, places=6)

    def test_account1_week2_share(self):
        # dashboard_view: 2 of 4 events → 0.50 (login and report_export each have 1)
        share = _row(1, "2024-07-08")["top_feature_pct_share"]
        self.assertAlmostEqual(share, 0.50, places=6)

    def test_account1_week3_share(self):
        # login, dashboard_view, report_export: each 2 of 6 → 0.333...
        share = _row(1, "2024-07-15")["top_feature_pct_share"]
        self.assertAlmostEqual(share, 1 / 3, places=6)

    def test_account2_week1_share(self):
        # report_export: 2 of 4 events → 0.50
        share = _row(2, "2024-07-01")["top_feature_pct_share"]
        self.assertAlmostEqual(share, 0.50, places=6)

    def test_account2_week2_share(self):
        # api_call: 8 of 11 events → ~0.7273
        share = _row(2, "2024-07-08")["top_feature_pct_share"]
        self.assertAlmostEqual(share, 8 / 11, places=6)

    def test_account2_week3_share(self):
        # login, dashboard_view, report_export: each 1 of 3 → 0.333...
        share = _row(2, "2024-07-15")["top_feature_pct_share"]
        self.assertAlmostEqual(share, 1 / 3, places=6)


# ---------------------------------------------------------------------------
# Top-feature identity tests
# ---------------------------------------------------------------------------

class TestTopFeature(unittest.TestCase):
    """The top_feature column should name the event_type with the highest count."""

    def test_account1_week1_top_feature_is_login(self):
        self.assertEqual(_row(1, "2024-07-01")["top_feature"], "login")

    def test_account1_week2_top_feature_is_dashboard_view(self):
        self.assertEqual(_row(1, "2024-07-08")["top_feature"], "dashboard_view")

    def test_account2_week2_top_feature_is_api_call(self):
        self.assertEqual(_row(2, "2024-07-08")["top_feature"], "api_call")


# ---------------------------------------------------------------------------
# Anomaly flag tests
# ---------------------------------------------------------------------------

class TestAnomalyFlag(unittest.TestCase):
    """
    anomaly_flag = 1 when top_feature_pct_share > 0.70, else 0.
    Only Account 2, Week 2024-07-08 should be flagged (api_call = 72.7%).
    """

    def test_only_one_anomaly_in_dataset(self):
        n_anomalies = int(_results["anomaly_flag"].sum())
        self.assertEqual(n_anomalies, 1, f"Expected exactly 1 anomaly row, found {n_anomalies}.")

    def test_account2_week2_is_flagged(self):
        self.assertEqual(_row(2, "2024-07-08")["anomaly_flag"], 1)

    def test_account1_never_flagged(self):
        account1 = _results[_results["account_id"] == 1]
        self.assertEqual(
            int(account1["anomaly_flag"].sum()), 0,
            "Account 1 should have no anomaly flags.",
        )

    def test_account2_week1_not_flagged(self):
        self.assertEqual(_row(2, "2024-07-01")["anomaly_flag"], 0)

    def test_account2_week3_not_flagged(self):
        self.assertEqual(_row(2, "2024-07-15")["anomaly_flag"], 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
