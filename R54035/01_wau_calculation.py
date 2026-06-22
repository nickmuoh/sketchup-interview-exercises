import pandas as pd
from pathlib import Path

from .utils import add_repo_to_path

_THIS_DIR, _ = add_repo_to_path(Path(__file__))

from .exercise_setup import setup_events_database, execute_sql_script  # noqa: E402

if __name__ == "__main__":
    with setup_events_database() as conn:
        wau_df = execute_sql_script(_THIS_DIR / "01_wau_calculation.sql", conn)

    pd.set_option('display.max_columns', None)
    pd.set_option('display.max_rows', None)
    pd.set_option('display.width', None)

    print(wau_df)
