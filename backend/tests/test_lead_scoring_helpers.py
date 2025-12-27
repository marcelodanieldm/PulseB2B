import pandas as pd
from app.utils.lead_scoring_helpers import load_companies_data, calculate_hpi_scores, generate_report

class DummyCalculator:
    def batch_calculate(self, df):
        df['hpi_score'] = 80
        df['urgency_level'] = 'CRITICAL'
        return df

def test_load_companies_data(tmp_path):
    csv_path = tmp_path / 'companies.csv'
    pd.DataFrame({
        'company_name': ['A', 'B'],
        'country': ['MX', 'BR'],
        'employee_count': [10, 20],
        'hpi_score': [0, 0],
        'urgency_level': ['LOW', 'LOW']
    }).to_csv(csv_path, index=False)
    df = load_companies_data(str(csv_path))
    assert len(df) == 2

def test_calculate_hpi_scores():
    df = pd.DataFrame({
        'company_name': ['A'],
        'country': ['MX'],
        'employee_count': [10],
        'hpi_score': [0],
        'urgency_level': ['LOW']
    })
    result = calculate_hpi_scores(df, DummyCalculator())
    assert result['hpi_score'].iloc[0] == 80
    assert result['urgency_level'].iloc[0] == 'CRITICAL'

def test_generate_report(tmp_path):
    df = pd.DataFrame({
        'company_name': ['A'],
        'country': ['MX'],
        'last_funding_date': ['2025-01-01'],
        'employee_count': [10],
        'estimated_headcount_delta': [2],
        'hpi_score': [80],
        'hpi_category': ['HIGH'],
        'urgency_level': ['CRITICAL'],
        'funding_recency_score': [10],
        'growth_urgency_score': [10]
    })
    out = generate_report(df, str(tmp_path))
    assert 'full_report' in out and 'top_leads' in out and 'critical_leads' in out
