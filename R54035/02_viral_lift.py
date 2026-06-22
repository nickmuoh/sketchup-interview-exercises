from pathlib import Path

from .utils import add_repo_to_path

_THIS_DIR, _ = add_repo_to_path(Path(__file__))

from .exercise_setup import setup_product_telemetry_database, execute_sql_script  # noqa: E402

SQL_PATH = _THIS_DIR / "02_viral_lift.sql"


def main():
    with setup_product_telemetry_database(db_path=":memory:") as conn:
        df = execute_sql_script(SQL_PATH, conn)

    if df is None:
        print("No results returned. Make sure your SQL ends with a SELECT statement.")
        return

    print(df.to_string(index=False))


if __name__ == "__main__":
    main()
