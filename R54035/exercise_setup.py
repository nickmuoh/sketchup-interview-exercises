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


@contextmanager
def setup_product_telemetry_database(db_path=":memory:"):
    """
    Context manager that creates and populates a SQLite database with product
    telemetry data for the Viral Loop Analysis exercise, then closes the
    connection on exit.

    Args:
        db_path: Path to the SQLite database file (defaults to in-memory)

    Yields:
        Connection object to the database
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS product_telemetry (
            event_time TEXT,
            event_type TEXT,
            event_properties TEXT
        )
    """)

    cursor.execute("DELETE FROM product_telemetry")

    telemetry_data = [
        # ── January 2025 ── (2 distinct files, both DQ-valid) ──────────────
        # skp-001: 5 recipients (2 editors, 1 commenter, 2 viewers), 2 unknown
        (
            "2025-01-10 09:00:00",
            "share_invite_sent",
            '{"file_id": "skp-001", "share_metadata": {"recipients_count": 5, '
            '"role_distribution": {"editors": 2, "commenters": 1, "viewers": 2}, '
            '"identity_stats": {"known_contacts": 3, "unknown_contacts": 2}}}',
        ),
        # skp-002: 3 recipients (1 editor, 1 commenter, 1 viewer), 1 unknown
        (
            "2025-01-20 14:00:00",
            "share_invite_sent",
            '{"file_id": "skp-002", "share_metadata": {"recipients_count": 3, '
            '"role_distribution": {"editors": 1, "commenters": 1, "viewers": 1}, '
            '"identity_stats": {"known_contacts": 2, "unknown_contacts": 1}}}',
        ),
        # ── February 2025 ── (1 file, DQ-invalid: roles sum to 3 ≠ 4) ─────
        # skp-003: 4 recipients (2 editors, 1 commenter, 0 viewers), 1 unknown
        (
            "2025-02-14 11:00:00",
            "share_invite_sent",
            '{"file_id": "skp-003", "share_metadata": {"recipients_count": 4, '
            '"role_distribution": {"editors": 2, "commenters": 1, "viewers": 0}, '
            '"identity_stats": {"known_contacts": 3, "unknown_contacts": 1}}}',
        ),
        # ── March 2025 ── (same file shared twice → DISTINCT count = 1) ───
        # skp-004, first share: 6 recipients (3 editors, 2 commenters, 1 viewer), 3 unknown
        (
            "2025-03-05 10:00:00",
            "share_invite_sent",
            '{"file_id": "skp-004", "share_metadata": {"recipients_count": 6, '
            '"role_distribution": {"editors": 3, "commenters": 2, "viewers": 1}, '
            '"identity_stats": {"known_contacts": 3, "unknown_contacts": 3}}}',
        ),
        # skp-004, second share: identical properties (tests COUNT DISTINCT)
        (
            "2025-03-18 16:00:00",
            "share_invite_sent",
            '{"file_id": "skp-004", "share_metadata": {"recipients_count": 6, '
            '"role_distribution": {"editors": 3, "commenters": 2, "viewers": 1}, '
            '"identity_stats": {"known_contacts": 3, "unknown_contacts": 3}}}',
        ),
        # ── Noise rows (must be filtered out by the SQL) ─────────────────
        # Pre-2025 event: filtered by event_time >= '2025-01-01'
        (
            "2024-12-31 23:59:00",
            "share_invite_sent",
            '{"file_id": "skp-000", "share_metadata": {"recipients_count": 10, '
            '"role_distribution": {"editors": 5, "commenters": 3, "viewers": 2}, '
            '"identity_stats": {"known_contacts": 4, "unknown_contacts": 6}}}',
        ),
        # Wrong event type: filtered by event_type = 'share_invite_sent'
        (
            "2025-01-15 08:00:00",
            "file_opened",
            '{"file_id": "skp-000", "share_metadata": {"recipients_count": 10, '
            '"role_distribution": {"editors": 5, "commenters": 3, "viewers": 2}, '
            '"identity_stats": {"known_contacts": 4, "unknown_contacts": 6}}}',
        ),
    ]

    cursor.executemany(
        "INSERT INTO product_telemetry VALUES (?, ?, ?)", telemetry_data
    )

    conn.commit()
    try:
        yield conn
    finally:
        conn.close()


@contextmanager
def setup_entitlements_database(db_path=":memory:"):
    """
    Context manager that creates and populates a SQLite database with raw
    entitlement action streams to test SCD2 reconstruction.

    Args:
        db_path: Path to the SQLite database file (defaults to in-memory)

    Yields:
        Connection object to the database
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ems_events_projected (
            user_id INTEGER,
            entitlement_sku TEXT,
            action TEXT,
            event_time TEXT
        )
    """)
    cursor.execute("DELETE FROM ems_events_projected")

    entitlement_data = [
        # User 1: Perfect progression (Trial -> Upgraded -> Upgraded)
        (1, "SKP-TRIAL", "assigned", "2024-01-01 10:00:00"),
        (1, "SKP-PRO", "upgraded", "2024-01-31 09:00:00"),
        (1, "SKP-STUDIO", "upgraded", "2025-01-31 08:00:00"),
        # User 2: Cancellation Gap (Assigned -> Revoked -> Gap -> Re-assigned)
        (2, "SKP-PRO", "assigned", "2024-05-01 12:00:00"),
        (2, "SKP-PRO", "revoked", "2024-06-01 12:00:00"),
        (2, "SKP-PRO", "assigned", "2024-08-15 12:00:00"),
        # User 3: Same-day Assignment and Revocation (Fraud/Immediate Refund)
        (3, "SKP-PRO", "assigned", "2024-02-01 09:00:00"),
        (3, "SKP-PRO", "revoked", "2024-02-01 15:00:00"),
        # User 4: Downgrade followed by expiration
        (4, "SKP-STUDIO", "assigned", "2024-03-01 08:00:00"),
        (4, "SKP-PRO", "downgraded", "2024-03-15 08:00:00"),
        (4, "SKP-PRO", "expired", "2024-04-01 08:00:00"),
    ]

    cursor.executemany(
        "INSERT INTO ems_events_projected VALUES (?, ?, ?, ?)", entitlement_data
    )

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
