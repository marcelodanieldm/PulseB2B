"""Lead Scoring System - Main Script"""

import os
import sys
import argparse
import logging
from datetime import datetime
from pathlib import Path
import json

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.web_scraper import LinkedInScraper, FallbackDataEnricher
from src.hpi_calculator import HPICalculator
import pandas as pd
import numpy as np

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def load_companies_data(csv_path: str) -> pd.DataFrame:
    logger.info(f"Loading companies data from {csv_path}")
    df = pd.read_csv(csv_path)
    df = df[df['country'].isin(['MX', 'BR'])].copy()
    logger.info(f"Loaded {len(df)} companies")
    return df


def scrape_employee_data(df: pd.DataFrame, use_scraper: bool = True) -> pd.DataFrame:
    if not use_scraper:
        logger.info("Using mock data")
        df['employee_count'] = df.apply(
            lambda row: FallbackDataEnricher.estimate_from_funding(
                row['funding_stage'], row.get('last_funding_amount', None)
            ), axis=1
        )
        np.random.seed(42)
        df['employee_count_6m_ago'] = df['employee_count'].apply(
            lambda x: int(x * np.random.uniform(0.85, 0.98))
        )
    else:
        logger.info("Starting web scraping...")
        scraper = LinkedInScraper()
        companies_list = df[['company_name', 'country']].to_dict('records')
        results = scraper.batch_extract(companies_list)
        
        df['employee_count'] = [r['employee_count'] for r in results]
        df['linkedin_url'] = [r['linkedin_url'] for r in results]
        
        failed_mask = df['employee_count'].isna()
        if failed_mask.any():
            df.loc[failed_mask, 'employee_count'] = df[failed_mask].apply(
                lambda row: FallbackDataEnricher.estimate_from_funding(
                    row['funding_stage'], row.get('last_funding_amount', None)
                ), axis=1
            )
        
        np.random.seed(42)
        df['employee_count_6m_ago'] = df['employee_count'].apply(
            lambda x: int(x * np.random.uniform(0.85, 0.98)) if pd.notna(x) else None
        )
    
    return df


def calculate_hpi_scores(df: pd.DataFrame) -> pd.DataFrame:
    logger.info("Calculating HPI scores...")
    calculator = HPICalculator()
    results_df = calculator.batch_calculate(df)
    
    results_df['estimated_headcount_delta'] = results_df.apply(
        lambda row: _estimate_headcount_delta(
            row['employee_count'], row['hpi_score'], row['urgency_level']
        ), axis=1
    )
    
    summary = calculator.generate_summary_stats(results_df)
    logger.info(f"HPI Summary: {json.dumps(summary, indent=2)}")
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
    results_df = results_df.sort_values('hpi_score', ascending=False)
    
    output_cols = [
        'company_name', 'country', 'last_funding_date', 'employee_count',
        'estimated_headcount_delta', 'hpi_score', 'hpi_category',
        'urgency_level', 'funding_recency_score', 'growth_urgency_score'
    ]
    
    full_report_path = os.path.join(output_dir, f'lead_scoring_report_{timestamp}.csv')
    results_df[output_cols].to_csv(full_report_path, index=False)
    logger.info(f"Full report saved: {full_report_path}")
    
    top_leads = results_df[results_df['hpi_score'] >= 65]
    top_leads_path = os.path.join(output_dir, f'top_leads_{timestamp}.csv')
    top_leads[output_cols].to_csv(top_leads_path, index=False)
    logger.info(f"Top leads: {top_leads_path} ({len(top_leads)} leads)")
    
    critical_leads = results_df[results_df['hpi_score'] >= 80]
    critical_leads_path = os.path.join(output_dir, f'critical_leads_{timestamp}.csv')
    critical_leads[output_cols].to_csv(critical_leads_path, index=False)
    logger.info(f"Critical leads: {critical_leads_path} ({len(critical_leads)} leads)")
    
    summary_stats = {
        'timestamp': timestamp,
        'total_companies': len(results_df),
        'by_country': {
            'MX': len(results_df[results_df['country'] == 'MX']),
            'BR': len(results_df[results_df['country'] == 'BR'])
        },
        'by_urgency': {
            urgency: len(results_df[results_df['urgency_level'] == urgency])
            for urgency in results_df['urgency_level'].unique()
        },
        'hpi_distribution': {
            'mean': float(results_df['hpi_score'].mean()),
            'median': float(results_df['hpi_score'].median()),
            'std': float(results_df['hpi_score'].std())
        }
    }
    
    stats_path = os.path.join(output_dir, f'summary_stats_{timestamp}.json')
    with open(stats_path, 'w') as f:
        json.dump(summary_stats, f, indent=2)
    logger.info(f"Summary stats saved: {stats_path}")
    
    return {
        'full_report': full_report_path,
        'top_leads': top_leads_path,
        'critical_leads': critical_leads_path,
        'summary_stats': stats_path
    }


def main():
    parser = argparse.ArgumentParser(description='Lead Scoring System for LATAM')
    parser.add_argument('--input', type=str, default='data/input/companies_latam.csv')
    parser.add_argument('--output', type=str, default='data/output/lead_scoring')
    parser.add_argument('--no-scraper', action='store_true')
    parser.add_argument('--sample', type=int, default=None)
    
    args = parser.parse_args()
    
    logger.info("=== Lead Scoring System Started ===")
    
    try:
        df = load_companies_data(args.input)
        
        if args.sample:
            df = df.head(args.sample)
        
        df = scrape_employee_data(df, use_scraper=not args.no_scraper)
        results_df = calculate_hpi_scores(df)
        report_paths = generate_report(results_df, args.output)
        
        logger.info("=== Completed Successfully ===")
        for report_type, path in report_paths.items():
            logger.info(f"  {report_type}: {path}")
        
        return 0
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        return 1


if __name__ == '__main__':
    sys.exit(main())
