"""
Run Predictions - Script para ejecutar predicciones en empresas
Genera informes JSON con probabilidades de contratación
"""

import logging
import json
import sys
from pathlib import Path
from datetime import datetime, timedelta

# Agregar src al path
sys.path.append(str(Path(__file__).parent.parent / 'src'))

from ml_predictor import HiringProbabilityPredictor
from feature_engineering import FeatureEngineer, CompanyFeatures

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def load_companies_from_watchlist() -> list:
    """
    Carga empresas desde la watchlist de Supabase
    En producción, esto se conectaría a la DB real
    """
    # Mock data para demostración
    companies = [
        {
            'id': 'openai',
            'name': 'OpenAI',
            'region': 'us',
            'team_size': 750,
            'founded_date': datetime(2015, 12, 1),
            'funding_data': [
                {
                    'round_type': 'series-c',
                    'amount': 10000.0,  # $10B
                    'date': datetime(2023, 1, 15)
                },
                {
                    'round_type': 'series-b',
                    'amount': 1000.0,
                    'date': datetime(2021, 7, 1)
                }
            ],
            'jobs_data': [
                {'title': 'Senior ML Researcher', 'scraped_at': datetime.now()},
                {'title': 'Research Engineer', 'scraped_at': datetime.now() - timedelta(days=2)},
                {'title': 'Applied AI Engineer', 'scraped_at': datetime.now() - timedelta(days=3)},
                {'title': 'Infrastructure Engineer', 'scraped_at': datetime.now() - timedelta(days=5)},
                {'title': 'Staff Software Engineer', 'scraped_at': datetime.now() - timedelta(days=7)},
                {'title': 'Senior Software Engineer', 'scraped_at': datetime.now() - timedelta(days=10)},
                {'title': 'Data Scientist', 'scraped_at': datetime.now() - timedelta(days=12)},
            ],
            'linkedin_data': {
                'current_headcount': 750,
                'departures': [
                    {'seniority': 'senior', 'departure_date': datetime.now() - timedelta(days=8)},
                    {'seniority': 'mid', 'departure_date': datetime.now() - timedelta(days=15)}
                ]
            }
        },
        {
            'id': 'nubank',
            'name': 'Nubank',
            'region': 'sa',
            'team_size': 5000,
            'founded_date': datetime(2013, 5, 1),
            'funding_data': [
                {
                    'round_type': 'series-g',
                    'amount': 750.0,
                    'date': datetime(2021, 6, 8)
                }
            ],
            'jobs_data': [
                {'title': 'Backend Engineer', 'scraped_at': datetime.now()},
                {'title': 'Android Engineer', 'scraped_at': datetime.now() - timedelta(days=1)},
                {'title': 'iOS Engineer', 'scraped_at': datetime.now() - timedelta(days=2)},
                {'title': 'Data Engineer', 'scraped_at': datetime.now() - timedelta(days=4)},
                {'title': 'Staff Engineer', 'scraped_at': datetime.now() - timedelta(days=6)},
                {'title': 'Security Engineer', 'scraped_at': datetime.now() - timedelta(days=8)},
                {'title': 'DevOps Engineer', 'scraped_at': datetime.now() - timedelta(days=10)},
                {'title': 'Product Manager', 'scraped_at': datetime.now() - timedelta(days=11)},
            ],
            'linkedin_data': {
                'current_headcount': 5000,
                'departures': [
                    {'seniority': 'senior', 'departure_date': datetime.now() - timedelta(days=5)},
                    {'seniority': 'senior', 'departure_date': datetime.now() - timedelta(days=10)},
                    {'seniority': 'staff', 'departure_date': datetime.now() - timedelta(days=12)},
                    {'seniority': 'mid', 'departure_date': datetime.now() - timedelta(days=18)},
                    {'seniority': 'mid', 'departure_date': datetime.now() - timedelta(days=22)}
                ]
            }
        },
        {
            'id': 'stripe',
            'name': 'Stripe',
            'region': 'us',
            'team_size': 8000,
            'founded_date': datetime(2010, 1, 1),
            'funding_data': [
                {
                    'round_type': 'series-i',
                    'amount': 600.0,
                    'date': datetime(2023, 3, 15)
                }
            ],
            'jobs_data': [
                {'title': 'Software Engineer', 'scraped_at': datetime.now()},
                {'title': 'Frontend Engineer', 'scraped_at': datetime.now() - timedelta(days=3)},
                {'title': 'Product Designer', 'scraped_at': datetime.now() - timedelta(days=6)},
            ],
            'linkedin_data': {
                'current_headcount': 8000,
                'departures': [
                    {'seniority': 'mid', 'departure_date': datetime.now() - timedelta(days=25)}
                ]
            }
        },
        {
            'id': 'revolut',
            'name': 'Revolut',
            'region': 'eu',
            'team_size': 7000,
            'founded_date': datetime(2015, 7, 1),
            'funding_data': [
                {
                    'round_type': 'series-e',
                    'amount': 800.0,
                    'date': datetime(2021, 7, 15)
                }
            ],
            'jobs_data': [
                {'title': 'Backend Engineer', 'scraped_at': datetime.now() - timedelta(days=45)},
            ],
            'linkedin_data': {
                'current_headcount': 7000,
                'departures': [
                    {'seniority': 'senior', 'departure_date': datetime.now() - timedelta(days=5)},
                    {'seniority': 'senior', 'departure_date': datetime.now() - timedelta(days=8)},
                    {'seniority': 'senior', 'departure_date': datetime.now() - timedelta(days=12)},
                    {'seniority': 'senior', 'departure_date': datetime.now() - timedelta(days=15)},
                    {'seniority': 'staff', 'departure_date': datetime.now() - timedelta(days=18)}
                ]
            }
        },
        {
            'id': 'workos',
            'name': 'WorkOS',
            'region': 'us',
            'team_size': 85,
            'founded_date': datetime(2019, 10, 1),
            'funding_data': [
                {
                    'round_type': 'series-b',
                    'amount': 80.0,
                    'date': datetime.now() - timedelta(days=40)
                },
                {
                    'round_type': 'series-a',
                    'amount': 15.0,
                    'date': datetime(2021, 3, 1)
                }
            ],
            'jobs_data': [
                {'title': 'Senior Backend Engineer', 'scraped_at': datetime.now()},
                {'title': 'Staff Engineer', 'scraped_at': datetime.now() - timedelta(days=1)},
                {'title': 'Senior Frontend Engineer', 'scraped_at': datetime.now() - timedelta(days=2)},
                {'title': 'Engineering Manager', 'scraped_at': datetime.now() - timedelta(days=3)},
                {'title': 'Senior DevOps Engineer', 'scraped_at': datetime.now() - timedelta(days=4)},
                {'title': 'Product Manager', 'scraped_at': datetime.now() - timedelta(days=6)},
            ],
            'linkedin_data': {
                'current_headcount': 85,
                'departures': [
                    {'seniority': 'senior', 'departure_date': datetime.now() - timedelta(days=7)},
                    {'seniority': 'senior', 'departure_date': datetime.now() - timedelta(days=14)},
                    {'seniority': 'staff', 'departure_date': datetime.now() - timedelta(days=18)}
                ]
            }
        }
    ]
    
    return companies


def main():
    """Script principal de predicción"""
    
    print("\n" + "="*80)
    print("🎯 HIRING PROBABILITY PREDICTIONS")
    print("="*80 + "\n")
    
    # Cargar modelo
    print("Loading ML model...")
    predictor = HiringProbabilityPredictor(
        model_path='models/hiring_predictor_xgboost.pkl',
        model_type='xgboost'
    )
    
    # Verificar que el modelo esté cargado
    if predictor.model is None:
        print("\n❌ ERROR: Model not found!")
        print("Please run: python scripts/train_model.py")
        return
    
    print("✅ Model loaded successfully\n")
    
    # Cargar empresas
    print("Loading companies...")
    companies = load_companies_from_watchlist()
    print(f"✅ Loaded {len(companies)} companies\n")
    
    # Feature engineering
    print("Extracting features...")
    engineer = FeatureEngineer()
    features_list = []
    
    for company in companies:
        features = engineer.extract_features(
            company_data=company,
            jobs_data=company.get('jobs_data', []),
            funding_data=company.get('funding_data', []),
            linkedin_data=company.get('linkedin_data')
        )
        features_list.append(features)
    
    print(f"✅ Features extracted for {len(features_list)} companies\n")
    
    # Ejecutar predicciones
    print("="*80)
    print("Running predictions...")
    print("="*80 + "\n")
    
    predictions = predictor.predict_batch(
        features_list,
        output_file='data/predictions.json'
    )
    
    # Mostrar resultados
    print("\n" + "="*80)
    print("RESULTS")
    print("="*80 + "\n")
    
    for i, pred in enumerate(predictions, 1):
        prob = pred['prediction']['probability']
        label = pred['prediction']['label']
        
        # Emoji según probabilidad
        if prob >= 70:
            emoji = "🔥"
        elif prob >= 40:
            emoji = "⚡"
        else:
            emoji = "❄️"
        
        print(f"{emoji} {i}. {pred['company_name']}")
        print(f"   Probability: {prob}% ({label})")
        print(f"   Confidence: {pred['prediction']['confidence']}")
        print(f"\n   Key Features:")
        print(f"   • Funding: ${pred['features']['last_funding_amount']:.1f}M hace "
              f"{pred['features']['funding_recency']} días")
        print(f"   • Churn: {pred['features']['tech_churn']:.1f}% "
              f"({pred['features']['senior_departures']} seniors salieron)")
        print(f"   • Velocity: {pred['features']['job_post_velocity']:.1f}x "
              f"({pred['features']['current_month_posts']} vacantes este mes)")
        print(f"   • Region: {pred['features']['region_factor']:.2f}")
        
        print(f"\n   Reasons:")
        for j, reason in enumerate(pred['reasons'], 1):
            print(f"   {j}. {reason}")
        
        print("\n" + "-"*80 + "\n")
    
    # Generar reporte completo
    print("Generating comprehensive report...")
    report = predictor.generate_prediction_report(
        predictions,
        output_file='data/prediction_report.json'
    )
    
    # Mostrar estadísticas
    print("\n" + "="*80)
    print("SUMMARY STATISTICS")
    print("="*80)
    
    summary = report['summary']
    print(f"\nTotal Companies: {summary['total_companies']}")
    print(f"Average Probability: {summary['average_probability']:.1f}%")
    print(f"\nDistribution:")
    print(f"  🔥 High Probability (≥70%):   {summary['high_probability']} companies")
    print(f"  ⚡ Medium Probability (40-70%): {summary['medium_probability']} companies")
    print(f"  ❄️ Low Probability (<40%):     {summary['low_probability']} companies")
    
    # Top candidates
    print("\n" + "="*80)
    print("TOP 3 HIRING CANDIDATES")
    print("="*80 + "\n")
    
    for i, pred in enumerate(report['top_candidates'][:3], 1):
        print(f"{i}. {pred['company_name']}")
        print(f"   Probability: {pred['prediction']['probability']}%")
        print(f"   Top Reason: {pred['reasons'][0]}")
        print()
    
    # Archivos generados
    print("="*80)
    print("FILES GENERATED")
    print("="*80)
    print("\n✅ data/predictions.json")
    print("   - Individual predictions for each company")
    print("\n✅ data/prediction_report.json")
    print("   - Comprehensive report with statistics and top candidates")
    
    print("\n" + "="*80)
    print("✅ PREDICTIONS COMPLETE!")
    print("="*80 + "\n")


if __name__ == "__main__":
    main()
