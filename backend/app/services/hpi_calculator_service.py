"""Service for Hiring Potential Index (HPI) calculations."""

import pandas as pd
from typing import Dict, Any
from sklearn.preprocessing import MinMaxScaler
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class HPICalculator:
    def __init__(self):
        self.scaler = MinMaxScaler(feature_range=(0, 100))

    def calculate_funding_recency_score(self, last_funding_date: str) -> Dict:
        try:
            funding_date = pd.to_datetime(last_funding_date)
            today = pd.Timestamp.now()
            days_since = (today - funding_date).days

            if days_since <= 180:
                score = 100 - (days_since / 180) * 15
                tier = 'Very Recent'
            elif days_since <= 365:
                score = 85 - ((days_since - 180) / 185) * 25
                tier = 'Recent'
            elif days_since <= 545:
                score = 60 - ((days_since - 365) / 180) * 25
                tier = 'Moderate'
            elif days_since <= 730:
                score = 35 - ((days_since - 545) / 185) * 20
                tier = 'Old'
            else:
                score = max(0, 15 - ((days_since - 730) / 365) * 10)
                tier = 'Very Old'

            return {
                'funding_recency_score': round(score, 2),
                'days_since_funding': days_since,
                'recency_tier': tier
            }
        except Exception as e:
            logger.error(f"Error calculating funding recency: {e}")
            return {'funding_recency_score': 0, 'days_since_funding': None, 'recency_tier': 'Unknown'}

    def calculate_growth_urgency_score(self, current_employees: int, employees_6m_ago: int) -> Dict:
        try:
            if employees_6m_ago <= 0:
                return {
                    'urgency_score': 50,
                    'growth_6m_pct': 0,
                    'urgency_level': 'MEDIUM',
                    'urgency_reason': 'No historical data'
                }
            growth_pct = ((current_employees - employees_6m_ago) / employees_6m_ago) * 100

            if growth_pct < 5:
                urgency_score = 95
                urgency_level = 'HIGH'
                reason = 'Low growth despite funding - urgent hiring need'
            elif growth_pct < 10:
                urgency_score = 75
                urgency_level = 'MEDIUM-HIGH'
                reason = 'Moderate-low growth - good hiring opportunity'
            elif growth_pct < 15:
                urgency_score = 60
                urgency_level = 'MEDIUM'
                reason = 'Normal growth - standard hiring'
            elif growth_pct < 20:
                urgency_score = 45
                urgency_level = 'MEDIUM-LOW'
                reason = 'Good growth - hiring at steady pace'
            else:
                urgency_score = 20
                urgency_level = 'LOW'
                reason = 'High growth - company already saturated with hiring'

            return {
                'urgency_score': urgency_score,
                'growth_6m_pct': round(growth_pct, 2),
                'urgency_level': urgency_level,
                'urgency_reason': reason
            }
        except Exception as e:
            logger.error(f"Error calculating growth urgency: {e}")
            return {
                'urgency_score': 50,
                'growth_6m_pct': 0,
                'urgency_level': 'MEDIUM',
                'urgency_reason': 'Calculation error'
            }

    def calculate_company_size_factor(self, employee_count: int) -> float:
        if employee_count < 10:
            return 20
        elif employee_count < 50:
            return 40
        elif employee_count < 100:
            return 55
        elif employee_count < 250:
            return 70
        elif employee_count < 500:
            return 80
        elif employee_count < 1000:
            return 90
        else:
            return 100

    def calculate_funding_amount_score(self, funding_amount: float) -> float:
        if pd.isna(funding_amount) or funding_amount <= 0:
            return 50
        if funding_amount < 1_000_000:
            return 20
        elif funding_amount < 10_000_000:
            return 50
        elif funding_amount < 50_000_000:
            return 70
        elif funding_amount < 100_000_000:
            return 85
        else:
            return 100

    def calculate_hpi(self, company_data: Dict) -> Dict:
        last_funding_date = company_data.get('last_funding_date')
        current_employees = company_data.get('employee_count', 0)
        employees_6m_ago = company_data.get('employee_count_6m_ago', 0)
        funding_amount = company_data.get('last_funding_amount', 0)

        funding_data = self.calculate_funding_recency_score(last_funding_date)
        urgency_data = self.calculate_growth_urgency_score(current_employees, employees_6m_ago)
        size_factor = self.calculate_company_size_factor(current_employees)
        amount_score = self.calculate_funding_amount_score(funding_amount)

        funding_score = funding_data['funding_recency_score']
        urgency_score = urgency_data['urgency_score']
        growth_6m_pct = urgency_data['growth_6m_pct']

        raw_hpi = (
            funding_score * 0.40 +
            urgency_score * 0.35 +
            size_factor * 0.15 +
            amount_score * 0.10
        )

        boost_applied = False
        if funding_score >= 85 and growth_6m_pct < 5:
            raw_hpi *= 1.2
            boost_applied = True

        final_hpi = min(100, raw_hpi)

        if final_hpi >= 80:
            category = 'CRITICAL'
        elif final_hpi >= 65:
            category = 'HIGH'
        elif final_hpi >= 45:
            category = 'MEDIUM'
        else:
            category = 'LOW'

        return {
            'hpi_score': round(final_hpi, 2),
            'hpi_category': category,
            'funding_recency_score': round(funding_score, 2),
            'growth_urgency_score': urgency_score,
            'company_size_factor': round(size_factor, 2),
            'funding_amount_score': round(amount_score, 2),
            'urgency_level': urgency_data['urgency_level'],
            'urgency_reason': urgency_data['urgency_reason'],
            'growth_6m_pct': growth_6m_pct,
            'days_since_funding': funding_data['days_since_funding'],
            'boost_applied': boost_applied
        }

    def batch_calculate(self, df: pd.DataFrame) -> pd.DataFrame:
        results = []
        for idx, row in df.iterrows():
            company_dict = row.to_dict()
            hpi_result = self.calculate_hpi(company_dict)
            result_row = {**company_dict, **hpi_result}
            results.append(result_row)
        results_df = pd.DataFrame(results)
        return results_df

    def generate_summary_stats(self, results_df: pd.DataFrame) -> Dict:
        return {
            'total_companies': len(results_df),
            'hpi_statistics': {
                'mean': round(results_df['hpi_score'].mean(), 2),
                'median': round(results_df['hpi_score'].median(), 2),
                'std': round(results_df['hpi_score'].std(), 2),
                'min': round(results_df['hpi_score'].min(), 2),
                'max': round(results_df['hpi_score'].max(), 2)
            },
            'category_distribution': {
                'CRITICAL': len(results_df[results_df['hpi_category'] == 'CRITICAL']),
                'HIGH': len(results_df[results_df['hpi_category'] == 'HIGH']),
                'MEDIUM': len(results_df[results_df['hpi_category'] == 'MEDIUM']),
                'LOW': len(results_df[results_df['hpi_category'] == 'LOW'])
            },
            'boosts_applied': len(results_df[results_df['boost_applied'] == True])
        }

# Singleton instance for use in endpoints
hpi_calculator = HPICalculator()
