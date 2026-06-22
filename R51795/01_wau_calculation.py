from exercise_setup import setup_events_database, execute_sql_script
import pandas as pd

if __name__ == "__main__":
    with setup_events_database() as conn:
        wau_df = execute_sql_script('R51795/01_wau_calculation.sql', conn)

    pd.set_option('display.max_columns', None)
    pd.set_option('display.max_rows', None)
    pd.set_option('display.width', None)

    print(wau_df)
