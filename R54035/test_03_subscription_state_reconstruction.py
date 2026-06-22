"""
Test suite for Exercise 3: Subscription State Reconstruction (SCD2).

Run from the repo root:
    python -m unittest R54035.test_03_subscription_state_reconstruction -v

All tests are based on the fixed sample dataset created by exercise_setup.py.
Passing every test means your SQL implementation is correct.
"""
import unittest
from pathlib import Path

import pandas as pd

from .utils import add_repo_to_path

_THIS_DIR, _ = add_repo_to_path(Path(__file__))

from exercise_setup import setup_entitlements_database, execute_sql_script  # noqa: E402

SQL_PATH = _THIS_DIR / "03_subscription_state_reconstruction.sql"


def setUpModule():
    global _results

    with setup_entitlements_database(db_path=":memory:") as conn:
        df = execute_sql_script(SQL_PATH, conn)

    if df is None:
        raise AssertionError(
            "execute_sql_script returned None — make sure your SQL ends with a SELECT statement."
        )

    _results = df


def _rows_for_user(user_id: int) -> pd.DataFrame:
    return _results[_results["user_id"] == user_id]


def _row(user_id: int, start_date: str) -> pd.Series:
    mask = (_results["user_id"] == user_id) & (
        _results["effective_start_date"] == start_date
    )
    matched = _results[mask]

    if len(matched) != 1:
        raise AssertionError(
            f"Expected exactly 1 row for user_id={user_id}, "
            f"effective_start_date={start_date!r}, got {len(matched)}."
        )

    return matched.iloc[0]


class TestOutputSchema(unittest.TestCase):
    REQUIRED_COLUMNS = {
        "user_id",
        "entitlement_sku",
        "effective_start_date",
        "effective_end_date",
    }

    def test_required_columns_present(self):
        missing = self.REQUIRED_COLUMNS - set(_results.columns)
        self.assertFalse(missing, f"Missing columns: {missing}")

    def test_row_count(self):
        self.assertEqual(
            len(_results), 7,
            f"Expected 7 active entitlement rows, got {len(_results)}.\n{_results}",
        )

    def test_ordering(self):
        expected_pairs = [
            (1, "2024-01-01"),
            (1, "2024-01-31"),
            (1, "2025-01-31"),
            (2, "2024-05-01"),
            (2, "2024-08-15"),
            (4, "2024-03-01"),
            (4, "2024-03-15"),
        ]
        actual_pairs = list(
            zip(_results["user_id"], _results["effective_start_date"])
        )
        self.assertEqual(actual_pairs, sorted(expected_pairs))


class TestUser1Progression(unittest.TestCase):
    def test_user1_has_three_active_periods(self):
        self.assertEqual(len(_rows_for_user(1)), 3)

    def test_user1_trial_period(self):
        row = _row(1, "2024-01-01")
        self.assertEqual(row["entitlement_sku"], "SKP-TRIAL")
        self.assertEqual(row["effective_end_date"], "2024-01-30")

    def test_user1_pro_period(self):
        row = _row(1, "2024-01-31")
        self.assertEqual(row["entitlement_sku"], "SKP-PRO")
        self.assertEqual(row["effective_end_date"], "2025-01-30")

    def test_user1_studio_is_open_ended(self):
        row = _row(1, "2025-01-31")
        self.assertEqual(row["entitlement_sku"], "SKP-STUDIO")
        self.assertEqual(row["effective_end_date"], "2050-12-31")


class TestUser2GapHandling(unittest.TestCase):
    def test_user2_has_two_active_periods(self):
        self.assertEqual(len(_rows_for_user(2)), 2)

    def test_user2_first_subscription_closes_at_revoke_boundary(self):
        row = _row(2, "2024-05-01")
        self.assertEqual(row["entitlement_sku"], "SKP-PRO")
        self.assertEqual(row["effective_end_date"], "2024-05-31")

    def test_user2_reassignment_starts_new_period(self):
        row = _row(2, "2024-08-15")
        self.assertEqual(row["entitlement_sku"], "SKP-PRO")
        self.assertEqual(row["effective_end_date"], "2050-12-31")


class TestUser4DowngradeAndExpiration(unittest.TestCase):
    def test_user4_has_two_active_periods(self):
        self.assertEqual(len(_rows_for_user(4)), 2)

    def test_user4_studio_closes_before_downgrade(self):
        row = _row(4, "2024-03-01")
        self.assertEqual(row["entitlement_sku"], "SKP-STUDIO")
        self.assertEqual(row["effective_end_date"], "2024-03-14")

    def test_user4_pro_closes_before_expiration(self):
        row = _row(4, "2024-03-15")
        self.assertEqual(row["entitlement_sku"], "SKP-PRO")
        self.assertEqual(row["effective_end_date"], "2024-03-31")


class TestFilteringAndSafety(unittest.TestCase):
    def test_terminal_states_are_not_returned(self):
        self.assertNotIn("revoked", set(_results.get("action", [])))
        self.assertNotIn("expired", set(_results.get("action", [])))

    def test_same_day_assign_revoke_does_not_produce_negative_window(self):
        self.assertEqual(len(_rows_for_user(3)), 0)

    def test_all_rows_have_valid_date_windows(self):
        invalid = _results[
            _results["effective_start_date"] > _results["effective_end_date"]
        ]
        self.assertEqual(
            len(invalid), 0,
            f"Found invalid effective date windows:\n{invalid}",
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
