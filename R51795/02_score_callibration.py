"""
Score Calibration & Lift

Goal:
Join predicted churn scores to labels, calibrate by decile, compute baseline churn, top-decile lift, and cumulative capture.
"""
import pandas as pd
import pprint as pp
from exercise_setup import generate_churn_data


def calibrate_and_lift(scores_df: pd.DataFrame, labels_df: pd.DataFrame):
    # Join predictions and labels
    df = scores_df.merge(labels_df, on=['account_id', 'predict_period_end'], how='____')

    assert 'score' in df and 'churn_label' in df, 'missing required columns'

    # Bin scores into deciles (0..9)
    df['decile'] = pd.qcut(df['score'], q=____, labels=False, duplicates='drop')

    # Observed churn rate per decile and baseline
    calib = df.groupby('decile')['churn_label'].____()
    baseline = df['churn_label'].____()

    # Top-decile churn and lift
    top_decile_rate = ____
    lift = ____

    # Cumulative capture in top 10% most risky
    df_sorted = df.sort_values('score', ascending=False)
    total_churns = df['churn_label'].sum()
    capture_top10 = ____

    # Example risk tiers (adjust thresholds as needed)
    tiers = pd.cut(df['score'], bins=[0.0, ____ , ____ , 1.0], labels=['low', 'medium', 'high'])

    summary = {
        'baseline_rate': float(baseline),
        'top_decile_rate': float(top_decile_rate),
        'lift': float(lift),
        'capture_top10': float(capture_top10),
        'calibration_by_decile': calib.to_dict(),
        'tiers_example_counts': tiers.value_counts().to_dict()
    }

    return summary


if __name__ == "__main__":
    scores_df, labels_df = generate_churn_data(n=10000)
    results = calibrate_and_lift(scores_df, labels_df)

    pp.pprint(results, indent=2, compact=True)
