"""
Ejemplo de Uso del Motor ML
Demostración del flujo completo de predicción
"""

from datetime import datetime, timedelta
import json

# Importar componentes
from src.feature_engineering import FeatureEngineer, CompanyFeatures
from src.ml_predictor import HiringProbabilityPredictor


def ejemplo_simple():
    """Ejemplo más simple: predicción para una empresa"""
    
    print("\n" + "="*80)
    print("📊 EJEMPLO 1: Predicción Simple")
    print("="*80 + "\n")
    
    # 1. Cargar modelo entrenado
    print("1️⃣ Cargando modelo ML...")
    predictor = HiringProbabilityPredictor(
        model_path='models/hiring_predictor_xgboost.pkl',
        model_type='xgboost'
    )
    
    if predictor.model is None:
        print("❌ ERROR: Modelo no encontrado. Ejecuta primero:")
        print("   python scripts/train_model.py")
        return
    
    print("✅ Modelo cargado\n")
    
    # 2. Definir datos de la empresa
    print("2️⃣ Definiendo datos de empresa...")
    
    company_data = {
        'id': 'anthropic',
        'name': 'Anthropic',
        'region': 'us',
        'team_size': 150,
        'founded_date': datetime(2021, 1, 1)
    }
    
    # Funding reciente (Serie C hace 2 meses)
    funding_data = [
        {
            'round_type': 'series-c',
            'amount': 450.0,  # $450M
            'date': datetime.now() - timedelta(days=60)
        },
        {
            'round_type': 'series-b',
            'amount': 124.0,
            'date': datetime(2022, 5, 1)
        }
    ]
    
    # Vacantes recientes (surge de hiring)
    jobs_data = [
        {'title': 'Senior ML Research Scientist', 'scraped_at': datetime.now()},
        {'title': 'Research Engineer', 'scraped_at': datetime.now() - timedelta(days=1)},
        {'title': 'Software Engineer, Infrastructure', 'scraped_at': datetime.now() - timedelta(days=2)},
        {'title': 'Applied AI Engineer', 'scraped_at': datetime.now() - timedelta(days=3)},
        {'title': 'Staff Software Engineer', 'scraped_at': datetime.now() - timedelta(days=5)},
        {'title': 'Product Manager', 'scraped_at': datetime.now() - timedelta(days=7)},
    ]
    
    # Datos de LinkedIn (rotación moderada)
    linkedin_data = {
        'current_headcount': 150,
        'departures': [
            {'seniority': 'senior', 'departure_date': datetime.now() - timedelta(days=10)},
            {'seniority': 'mid', 'departure_date': datetime.now() - timedelta(days=15)},
            {'seniority': 'mid', 'departure_date': datetime.now() - timedelta(days=22)}
        ]
    }
    
    print("✅ Datos definidos\n")
    
    # 3. Feature Engineering
    print("3️⃣ Extrayendo features...")
    engineer = FeatureEngineer()
    
    features = engineer.extract_features(
        company_data=company_data,
        jobs_data=jobs_data,
        funding_data=funding_data,
        linkedin_data=linkedin_data
    )
    
    print(f"✅ Features extraídas para {features.company_name}\n")
    
    # Mostrar features clave
    print("   📊 Features Principales:")
    print(f"      • Funding Recency: {features.funding_recency} días")
    print(f"      • Last Funding: ${features.last_funding_amount}M ({features.funding_stage})")
    print(f"      • Tech Churn: {features.tech_churn}%")
    print(f"      • Senior Departures: {features.senior_departures}")
    print(f"      • Job Velocity: {features.job_post_velocity}x")
    print(f"      • Current Posts: {features.current_month_posts}")
    print(f"      • Tech Roles: {features.tech_roles_ratio}%")
    print(f"      • Region Factor: {features.region_factor}")
    print()
    
    # 4. Predicción
    print("4️⃣ Ejecutando predicción ML...")
    prediction = predictor.predict(features, explain=True)
    
    print("✅ Predicción completada\n")
    
    # 5. Mostrar resultados
    print("="*80)
    print("🎯 RESULTADO")
    print("="*80 + "\n")
    
    prob = prediction['prediction']['probability']
    label = prediction['prediction']['label']
    confidence = prediction['prediction']['confidence']
    
    # Emoji según probabilidad
    if prob >= 70:
        emoji = "🔥"
    elif prob >= 40:
        emoji = "⚡"
    else:
        emoji = "❄️"
    
    print(f"{emoji} {prediction['company_name']}")
    print(f"\n📊 Probabilidad de Contratación IT (próximos 3 meses):")
    print(f"   {prob}% - {label}")
    print(f"   Confianza: {confidence}")
    
    print(f"\n💡 Razones:")
    for i, reason in enumerate(prediction['reasons'], 1):
        print(f"   {i}. {reason}")
    
    # SHAP explanation
    if prediction.get('shap_explanation'):
        print(f"\n🔍 Top Features Impactantes (SHAP):")
        for item in prediction['shap_explanation'][:3]:
            impact_sign = "+" if item['impact'] > 0 else "-"
            print(f"   {impact_sign} {item['feature']}: {item['value']} (impact: {item['impact']:.3f})")
    
    print("\n" + "="*80 + "\n")


def ejemplo_batch():
    """Ejemplo de predicción para múltiples empresas"""
    
    print("\n" + "="*80)
    print("📊 EJEMPLO 2: Predicción Batch (Múltiples Empresas)")
    print("="*80 + "\n")
    
    # Cargar modelo
    predictor = HiringProbabilityPredictor(
        model_path='models/hiring_predictor_xgboost.pkl'
    )
    
    if predictor.model is None:
        print("❌ ERROR: Modelo no encontrado")
        return
    
    print("✅ Modelo cargado")
    
    # Feature engineer
    engineer = FeatureEngineer()
    
    # Definir múltiples empresas
    companies = [
        {
            'data': {
                'id': 'workos',
                'name': 'WorkOS',
                'region': 'us',
                'team_size': 85,
                'founded_date': datetime(2019, 10, 1)
            },
            'funding': [
                {'round_type': 'series-b', 'amount': 80.0, 
                 'date': datetime.now() - timedelta(days=40)}
            ],
            'jobs': [
                {'title': 'Senior Backend Engineer', 'scraped_at': datetime.now()},
                {'title': 'Staff Engineer', 'scraped_at': datetime.now() - timedelta(days=1)},
                {'title': 'Senior Frontend Engineer', 'scraped_at': datetime.now() - timedelta(days=2)},
            ],
            'linkedin': {
                'current_headcount': 85,
                'departures': [
                    {'seniority': 'senior', 'departure_date': datetime.now() - timedelta(days=7)},
                    {'seniority': 'senior', 'departure_date': datetime.now() - timedelta(days=14)},
                    {'seniority': 'staff', 'departure_date': datetime.now() - timedelta(days=18)}
                ]
            }
        },
        {
            'data': {
                'id': 'nubank',
                'name': 'Nubank',
                'region': 'sa',
                'team_size': 5000,
                'founded_date': datetime(2013, 5, 1)
            },
            'funding': [
                {'round_type': 'series-g', 'amount': 750.0, 
                 'date': datetime(2021, 6, 8)}
            ],
            'jobs': [
                {'title': 'Backend Engineer', 'scraped_at': datetime.now()},
                {'title': 'Android Engineer', 'scraped_at': datetime.now() - timedelta(days=1)},
            ],
            'linkedin': {
                'current_headcount': 5000,
                'departures': [
                    {'seniority': 'senior', 'departure_date': datetime.now() - timedelta(days=5)},
                ]
            }
        },
        {
            'data': {
                'id': 'revolut',
                'name': 'Revolut',
                'region': 'eu',
                'team_size': 7000,
                'founded_date': datetime(2015, 7, 1)
            },
            'funding': [
                {'round_type': 'series-e', 'amount': 800.0, 
                 'date': datetime(2021, 7, 15)}
            ],
            'jobs': [],  # Sin vacantes recientes
            'linkedin': {
                'current_headcount': 7000,
                'departures': [
                    {'seniority': 'senior', 'departure_date': datetime.now() - timedelta(days=5)},
                    {'seniority': 'senior', 'departure_date': datetime.now() - timedelta(days=8)},
                    {'seniority': 'senior', 'departure_date': datetime.now() - timedelta(days=12)},
                    {'seniority': 'senior', 'departure_date': datetime.now() - timedelta(days=15)},
                ]
            }
        }
    ]
    
    # Extraer features para todas
    print(f"\n📥 Extrayendo features para {len(companies)} empresas...")
    features_list = []
    
    for company in companies:
        features = engineer.extract_features(
            company_data=company['data'],
            jobs_data=company['jobs'],
            funding_data=company['funding'],
            linkedin_data=company['linkedin']
        )
        features_list.append(features)
    
    print("✅ Features extraídas")
    
    # Ejecutar predicciones batch
    print("\n🚀 Ejecutando predicciones batch...")
    predictions = predictor.predict_batch(
        features_list,
        output_file='data/example_predictions.json'
    )
    
    print("✅ Predicciones completadas")
    
    # Mostrar resultados
    print("\n" + "="*80)
    print("🎯 RESULTADOS")
    print("="*80 + "\n")
    
    for i, pred in enumerate(predictions, 1):
        prob = pred['prediction']['probability']
        
        if prob >= 70:
            emoji = "🔥"
        elif prob >= 40:
            emoji = "⚡"
        else:
            emoji = "❄️"
        
        print(f"{emoji} {i}. {pred['company_name']}")
        print(f"   Probabilidad: {prob}% ({pred['prediction']['label']})")
        print(f"   Top Reason: {pred['reasons'][0]}")
        print()
    
    # Generar reporte
    print("📄 Generando reporte completo...")
    report = predictor.generate_prediction_report(
        predictions,
        output_file='data/example_report.json'
    )
    
    # Mostrar estadísticas
    print("\n" + "="*80)
    print("📊 ESTADÍSTICAS")
    print("="*80)
    
    summary = report['summary']
    print(f"\nTotal Empresas: {summary['total_companies']}")
    print(f"Probabilidad Promedio: {summary['average_probability']:.1f}%")
    print(f"\nDistribución:")
    print(f"  🔥 Alta (≥70%):   {summary['high_probability']}")
    print(f"  ⚡ Media (40-70%): {summary['medium_probability']}")
    print(f"  ❄️ Baja (<40%):    {summary['low_probability']}")
    
    print("\n✅ Archivos generados:")
    print("   • data/example_predictions.json")
    print("   • data/example_report.json")
    
    print("\n" + "="*80 + "\n")


def ejemplo_integracion():
    """Ejemplo de integración con pipeline existente"""
    
    print("\n" + "="*80)
    print("🔗 EJEMPLO 3: Integración con Pipeline Existente")
    print("="*80 + "\n")
    
    print("💡 Para integrar el motor ML con el pipeline de noticias:")
    print()
    print("```python")
    print("from src.main import PulseB2BPipeline")
    print("from src.ml_predictor import HiringProbabilityPredictor")
    print("from src.feature_engineering import FeatureEngineer")
    print()
    print("# 1. Ejecutar pipeline de noticias")
    print("pipeline = PulseB2BPipeline()")
    print("results = pipeline.run_full_pipeline()")
    print()
    print("# 2. Para cada empresa con datos suficientes")
    print("predictor = HiringProbabilityPredictor()")
    print("engineer = FeatureEngineer()")
    print()
    print("for company in results['companies']:")
    print("    # Extraer features")
    print("    features = engineer.extract_features(")
    print("        company_data=company['data'],")
    print("        jobs_data=company['jobs'],  # Desde Supabase")
    print("        funding_data=company['funding'],")
    print("        linkedin_data=company['linkedin']")
    print("    )")
    print("    ")
    print("    # Predecir")
    print("    prediction = predictor.predict(features)")
    print("    ")
    print("    # Guardar en Supabase")
    print("    supabase.from('hiring_predictions').insert({")
    print("        'company_id': company['id'],")
    print("        'probability': prediction['prediction']['probability'],")
    print("        'reasons': prediction['reasons'],")
    print("        'predicted_at': datetime.now()")
    print("    })")
    print("```")
    print()
    print("=" * 80 + "\n")


if __name__ == "__main__":
    print("\n" + "🤖 " * 30)
    print("MOTOR ML - EJEMPLOS DE USO")
    print("🤖 " * 30)
    
    # Ejecutar ejemplos
    ejemplo_simple()
    
    input("\n⏸️  Presiona Enter para continuar con el Ejemplo 2...")
    ejemplo_batch()
    
    input("\n⏸️  Presiona Enter para ver el Ejemplo 3...")
    ejemplo_integracion()
    
    print("\n✅ Ejemplos completados!")
    print("\n📚 Para más información, ver: docs/ML_ENGINE.md")
    print("="*80 + "\n")
