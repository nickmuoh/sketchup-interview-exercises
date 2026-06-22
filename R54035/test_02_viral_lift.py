"""
Test suite for Exercise 2: Viral Loop Analysis.

Run from the repo root:
    python -m unittest R54035.test_02_viral_lift -v

All tests are based on the fixed sample dataset created by exercise_setup.py.
Passing every test means your SQL implementation is correct.
"""
import unittest
from pathlib import Path

import pandas as pd

from .utils import add_repo_to_path

_THIS_DIR, _ = add_repo_to_path(Path(__file__))

from .exercise_setup import setup_product_telemetry_database, execute_sql_script  # noqa: E402

SQL_PATH = _THIS_DIR / "02_viral_lift.sql"


def setUpModule():
    """Run once for the entire module: create the DB and execute the SQL."""

    global _results

    with setup_product_telemetry_database(db_path=":memory:") as conn:
        df = execute_sql_script(SQL_PATH, conn)

    if df is None:
        raise AssertionError(
            "execute_sql_script returned None — make sure your SQL ends with a SELECT statement."
        )

    _results = df


def _month(event_month: str) -> pd.Series:
    """Return the single result row for a given event_month."""

    mask = _results["event_month"] == event_month
    matched = _results[mask]

    if len(matched) != 1:
        raise AssertionError(
            f"Expected exactly 1 row for event_month={event_month!r}, "
            f"got {len(matched)}."
        )

    return matched.iloc[0]


# ---------------------------------------------------------------------------
# Schema tests
# ---------------------------------------------------------------------------

class TestOutputSchema(unittest.TestCase):
    REQUIRED_COLUMNS = {
        "event_month",
        "monthly_unique_files",
        "net_new_viral_lift",
        "is_instrumentation_valid",
    }

    def test_required_columns_present(self):
        missing = self.REQUIRED_COLUMNS - set(_results.columns)
        self.assertFalse(missing, f"Missing columns: {missing}")

    def test_row_count(self):
        """Exactly 3 rows: one per active month (Jan, Feb, Mar 2025)."""
        self.assertEqual(
            len(_results), 3,
            f"Expected 3 rows (2025-01, 2025-02, 2025-03), got {len(_results)}.\n{_results}",
        )

    def test_ordering_descending(self):
        """Rows must be ordered by event_month DESC — newest first."""
        months = list(_results["event_month"])
        self.assertEqual(
            months, ["2025-03", "2025-02", "2025-01"],
            f"Expected DESC order, got {months}.",
        )


# ---------------------------------------------------------------------------
# January 2025 — two distinct files, DQ-valid
# ---------------------------------------------------------------------------

class TestJanuary2025(unittest.TestCase):
    """
    Jan data: skp-001 (5 recipients, 2 unknown) + skp-002 (3 recipients, 1 unknown).
    Expected: unique_files=2, net_new=3, viral_lift=1.5, DQ=1.
    """

    def test_jan_monthly_unique_files(self):
        self.assertEqual(_month("2025-01")["monthly_unique_files"], 2)

    def test_jan_net_new_viral_lift(self):
        # 3 net-new across 2 unique files → 1.5
        self.assertAlmostEqual(_month("2025-01")["net_new_viral_lift"], 1.5, places=6)

    def test_jan_viral_lift_is_float(self):
        """SQLite integer division trap: lift must be a float, not an integer."""
        self.assertIsInstance(
            float(_month("2025-01")["net_new_viral_lift"]), float
        )

    def test_jan_is_instrumentation_valid(self):
        # roles (2+1+2) + (1+1+1) = 8 = total recipients 8 → valid
        self.assertEqual(_month("2025-01")["is_instrumentation_valid"], 1)


# ---------------------------------------------------------------------------
# February 2025 — one file, DQ-invalid (roles sum ≠ recipients)
# ---------------------------------------------------------------------------

class TestFebruary2025(unittest.TestCase):
    """
    Feb data: skp-003 (4 recipients, roles 2+1+0=3 ≠ 4, 1 unknown).
    Expected: unique_files=1, viral_lift=1.0, DQ=0.
    """

    def test_feb_monthly_unique_files(self):
        self.assertEqual(_month("2025-02")["monthly_unique_files"], 1)

    def test_feb_net_new_viral_lift(self):
        # 1 net-new across 1 unique file → 1.0
        self.assertAlmostEqual(_month("2025-02")["net_new_viral_lift"], 1.0, places=6)

    def test_feb_is_instrumentation_invalid(self):
        # roles (2+1+0)=3 ≠ recipients 4 → DQ flag = 0
        self.assertEqual(_month("2025-02")["is_instrumentation_valid"], 0)


# ---------------------------------------------------------------------------
# March 2025 — same file shared twice (tests COUNT DISTINCT)
# ---------------------------------------------------------------------------

class TestMarch2025(unittest.TestCase):
    """
    Mar data: skp-004 shared twice (6 recipients, 3 unknown each time).
    Expected: unique_files=1 (DISTINCT), net_new=6 (sum), viral_lift=6.0, DQ=1.
    """

    def test_mar_monthly_unique_files(self):
        # Two rows, same file_id → COUNT(DISTINCT) must be 1
        self.assertEqual(_month("2025-03")["monthly_unique_files"], 1)

    def test_mar_net_new_viral_lift(self):
        # 6 total net-new / 1 unique file → 6.0
        self.assertAlmostEqual(_month("2025-03")["net_new_viral_lift"], 6.0, places=6)

    def test_mar_is_instrumentation_valid(self):
        # roles (3+2+1)*2 = 12 = total recipients 12 → valid
        self.assertEqual(_month("2025-03")["is_instrumentation_valid"], 1)


# ---------------------------------------------------------------------------
# Filter tests — noise rows must be excluded
# ---------------------------------------------------------------------------

class TestFiltering(unittest.TestCase):

    def test_no_pre_2025_rows(self):
        """The 2024-12-31 event must be excluded by event_time >= '2025-01-01'."""
        pre_2025 = _results[_results["event_month"] < "2025-01"]
        self.assertEqual(
            len(pre_2025), 0,
            f"Found unexpected pre-2025 rows:\n{pre_2025}",
        )

    def test_non_share_events_excluded(self):
        """The 'file_opened' event in Jan must not inflate monthly counts."""
        # If the file_opened row were included, Jan unique_files could be 3 (skp-000 added)
        # and net_new would be inflated. unique_files=2 proves the filter works.
        self.assertEqual(_month("2025-01")["monthly_unique_files"], 2)


if __name__ == "__main__":
    unittest.main(verbosity=2)
