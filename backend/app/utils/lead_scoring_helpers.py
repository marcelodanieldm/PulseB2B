"""
Helpers migrated from scripts/lead_scoring.py for HPI and lead scoring utilities.
"""
import os
import json
from datetime import datetime
from typing import Any
import pandas as pd

def load_companies_data(csv_path: str) -> pd.DataFrame:
    df = pd.read_csv(csv_path)
    df = df[df['country'].isin(['MX', 'BR'])].copy()
    return df

def calculate_hpi_scores(df: pd.DataFrame, calculator) -> pd.DataFrame:
    results_df = calculator.batch_calculate(df)
    results_df['estimated_headcount_delta'] = results_df.apply(
        lambda row: _estimate_headcount_delta(
            row['employee_count'], row['hpi_score'], row['urgency_level']
        ), axis=1
    )
    return results_df

def _estimate_headcount_delta(current_employees: int, hpi_score: float, urgency_level: str) -> int:
    growth_rates = {
        'CRITICAL': 0.20,
        'HIGH': 0.12,
        'MEDIUM': 0.06,
        'LOW': 0.02
    }
    growth_rate = growth_rates.get(urgency_level, 0.05)
    confidence_factor = hpi_score / 100
    adjusted_growth = growth_rate * confidence_factor
    delta = int(current_employees * adjusted_growth)
    return max(1, delta)

def generate_report(results_df: pd.DataFrame, output_dir: str) -> dict:
    os.makedirs(output_dir, exist_ok=True)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_cols = [
        'company_name', 'country', 'last_funding_date', 'employee_count',
        'estimated_headcount_delta', 'hpi_score', 'hpi_category',
        'urgency_level', 'funding_recency_score', 'growth_urgency_score'
    ]
    full_report_path = os.path.join(output_dir, f'lead_scoring_report_{timestamp}.csv')
    results_df[output_cols].to_csv(full_report_path, index=False)
    top_leads = results_df[results_df['hpi_score'] >= 65]
    top_leads_path = os.path.join(output_dir, f'top_leads_{timestamp}.csv')
    top_leads[output_cols].to_csv(top_leads_path, index=False)
    critical_leads = results_df[results_df['hpi_score'] >= 80]
    critical_leads_path = os.path.join(output_dir, f'critical_leads_{timestamp}.csv')
    critical_leads[output_cols].to_csv(critical_leads_path, index=False)
    return {
        'full_report': full_report_path,
        'top_leads': top_leads_path,
        'critical_leads': critical_leads_path
    }
