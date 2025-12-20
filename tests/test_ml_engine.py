"""
Tests para el Motor ML de Predicción de Contratación
"""

import unittest
import sys
from pathlib import Path
from datetime import datetime, timedelta
import numpy as np
import pandas as pd

# Add src to path
sys.path.append(str(Path(__file__).parent.parent / 'src'))

from feature_engineering import FeatureEngineer, CompanyFeatures
from ml_predictor import HiringProbabilityPredictor


class TestFeatureEngineering(unittest.TestCase):
    """Tests para feature engineering"""
    
    def setUp(self):
        self.engineer = FeatureEngineer()
        
        # Mock data
        self.company_data = {
            'id': 'test-123',
            'name': 'Test Startup',
            'region': 'us',
            'team_size': 100,
            'founded_date': datetime(2020, 1, 1)
        }
        
        self.funding_data = [
            {
                'round_type': 'series-a',
                'amount': 15.0,
                'date': datetime.now() - timedelta(days=60)
            }
        ]
        
        self.jobs_data = [
            {'title': 'Senior Engineer', 'scraped_at': datetime.now()},
            {'title': 'ML Engineer', 'scraped_at': datetime.now() - timedelta(days=2)}
        ]
        
        self.linkedin_data = {
            'current_headcount': 100,
            'departures': [
                {'seniority': 'senior', 'departure_date': datetime.now() - timedelta(days=10)},
                {'seniority': 'mid', 'departure_date': datetime.now() - timedelta(days=20)}
            ]
        }
    
    def test_extract_features(self):
        """Test feature extraction básico"""
        features = self.engineer.extract_features(
            self.company_data,
            self.jobs_data,
            self.funding_data,
            self.linkedin_data
        )
        
        # Verificar que se extraen todas las features
        self.assertIsInstance(features, CompanyFeatures)
        self.assertEqual(features.company_name, 'Test Startup')
        self.assertGreater(features.funding_recency, 0)
        self.assertGreater(features.last_funding_amount, 0)
        self.assertGreater(features.tech_churn, 0)
        self.assertGreater(features.job_post_velocity, 0)
    
    def test_funding_features(self):
        """Test cálculo de features de funding"""
        result = self.engineer._calculate_funding_features(self.funding_data)
        
        self.assertIn('recency', result)
        self.assertIn('amount', result)
        self.assertIn('stage', result)
        
        # Recency debe ser ~60 días
        self.assertAlmostEqual(result['recency'], 60, delta=1)
        self.assertEqual(result['amount'], 15.0)
        self.assertEqual(result['stage'], 'series-a')
    
    def test_churn_features(self):
        """Test cálculo de churn"""
        result = self.engineer._calculate_churn_features(
            self.company_data,
            self.linkedin_data
        )
        
        self.assertIn('churn_rate', result)
        self.assertIn('senior_departures', result)
        
        # Debe detectar 1 senior departure (últimos 30 días)
        self.assertEqual(result['senior_departures'], 1)
        
        # Churn debe ser ~2% (2 departures / 100 headcount)
        self.assertAlmostEqual(result['churn_rate'], 2.0, delta=0.5)
    
    def test_velocity_features(self):
        """Test cálculo de velocity"""
        result = self.engineer._calculate_velocity_features(self.jobs_data)
        
        self.assertIn('velocity', result)
        self.assertIn('current', result)
        self.assertIn('tech_ratio', result)
        
        # Debe contar 2 jobs este mes
        self.assertEqual(result['current'], 2)
        
        # Tech ratio debe ser 100% (ambos son roles tech)
        self.assertGreater(result['tech_ratio'], 80)
    
    def test_region_features(self):
        """Test coeficientes regionales"""
        us_result = self.engineer._calculate_region_features('us')
        sa_result = self.engineer._calculate_region_features('sa')
        eu_result = self.engineer._calculate_region_features('eu')
        
        # Verificar coeficientes
        self.assertEqual(us_result['factor'], 1.15)
        self.assertEqual(sa_result['factor'], 1.25)
        self.assertEqual(eu_result['factor'], 0.85)
    
    def test_features_to_dataframe(self):
        """Test conversión a DataFrame"""
        features = self.engineer.extract_features(
            self.company_data,
            self.jobs_data,
            self.funding_data,
            self.linkedin_data
        )
        
        df = self.engineer.features_to_dataframe(features)
        
        # Verificar estructura
        self.assertIsInstance(df, pd.DataFrame)
        self.assertEqual(len(df), 1)
        
        # Verificar features requeridas
        required_features = [
            'funding_recency',
            'tech_churn',
            'job_post_velocity',
            'region_factor'
        ]
        for feature in required_features:
            self.assertIn(feature, df.columns)
    
    def test_feature_explanations(self):
        """Test generación de explicaciones"""
        features = self.engineer.extract_features(
            self.company_data,
            self.jobs_data,
            self.funding_data,
            self.linkedin_data
        )
        
        explanations = self.engineer.get_feature_importance_explanation(features)
        
        # Verificar estructura
        self.assertIn('funding_signal', explanations)
        self.assertIn('churn_signal', explanations)
        self.assertIn('velocity_signal', explanations)
        self.assertIn('region_signal', explanations)
        
        # Cada señal debe tener explanation y signal
        for signal_name, signal_data in explanations.items():
            self.assertIn('signal', signal_data)
            self.assertIn('explanation', signal_data)


class TestMLPredictor(unittest.TestCase):
    """Tests para el predictor ML"""
    
    def setUp(self):
        self.engineer = FeatureEngineer()
        
        # Crear features de prueba
        self.features = CompanyFeatures(
            company_id='test-123',
            company_name='Test Startup',
            funding_recency=60,
            last_funding_amount=15.0,
            funding_stage='series-a',
            tech_churn=10.0,
            senior_departures=2,
            engineering_headcount=50,
            job_post_velocity=2.0,
            current_month_posts=5,
            previous_month_posts=2,
            tech_roles_ratio=80.0,
            region_factor=1.15,
            region='us',
            company_age_days=1000,
            total_funding=25.0,
            team_size=100,
            growth_stage='growth',
            calculated_at=datetime.now().isoformat()
        )
    
    def test_features_to_dataframe(self):
        """Test conversión de features a DataFrame"""
        df = self.engineer.features_to_dataframe(self.features)
        
        self.assertIsInstance(df, pd.DataFrame)
        self.assertEqual(len(df), 1)
        
        # Verificar que contiene las features esperadas
        self.assertEqual(df['funding_recency'].iloc[0], 60)
        self.assertEqual(df['tech_churn'].iloc[0], 10.0)
        self.assertEqual(df['job_post_velocity'].iloc[0], 2.0)
    
    def test_model_initialization(self):
        """Test inicialización del predictor"""
        predictor = HiringProbabilityPredictor(model_type='xgboost')
        
        self.assertEqual(predictor.model_type, 'xgboost')
        self.assertIsNotNone(predictor.feature_names)
        self.assertEqual(len(predictor.feature_names), 18)
    
    def test_prediction_requires_trained_model(self):
        """Test que predicción requiere modelo entrenado"""
        predictor = HiringProbabilityPredictor()
        predictor.model = None
        
        with self.assertRaises(ValueError):
            predictor.predict(self.features)
    
    def test_generate_reasons(self):
        """Test generación de razones"""
        predictor = HiringProbabilityPredictor()
        
        # Mock DataFrame
        X = self.engineer.features_to_dataframe(self.features)
        
        reasons = predictor._generate_reasons(self.features, X, 75.0)
        
        # Debe generar exactamente 3 razones
        self.assertEqual(len(reasons), 3)
        
        # Todas deben ser strings no vacíos
        for reason in reasons:
            self.assertIsInstance(reason, str)
            self.assertGreater(len(reason), 10)
    
    def test_confidence_calculation(self):
        """Test cálculo de confianza"""
        predictor = HiringProbabilityPredictor()
        
        # Alta probabilidad = alta confianza
        self.assertEqual(predictor._calculate_confidence(95), 'Very High')
        self.assertEqual(predictor._calculate_confidence(75), 'High')
        
        # Media
        self.assertEqual(predictor._calculate_confidence(60), 'Medium')
        
        # Baja probabilidad = alta confianza también
        self.assertEqual(predictor._calculate_confidence(15), 'Very High')


class TestDataIntegrity(unittest.TestCase):
    """Tests de integridad de datos"""
    
    def test_feature_values_in_valid_ranges(self):
        """Test que features están en rangos válidos"""
        engineer = FeatureEngineer()
        
        company_data = {
            'id': 'test',
            'name': 'Test',
            'region': 'us',
            'team_size': 100,
            'founded_date': datetime(2020, 1, 1)
        }
        
        funding_data = [
            {'round_type': 'series-a', 'amount': 10.0, 
             'date': datetime.now() - timedelta(days=30)}
        ]
        
        jobs_data = [
            {'title': 'Engineer', 'scraped_at': datetime.now()}
        ]
        
        features = engineer.extract_features(
            company_data, jobs_data, funding_data, {}
        )
        
        # Funding recency debe ser positivo
        self.assertGreater(features.funding_recency, 0)
        
        # Churn debe estar entre 0-100
        self.assertGreaterEqual(features.tech_churn, 0)
        self.assertLessEqual(features.tech_churn, 100)
        
        # Region factor debe ser razonable
        self.assertGreater(features.region_factor, 0.5)
        self.assertLess(features.region_factor, 2.0)
        
        # Velocity debe ser no-negativo
        self.assertGreaterEqual(features.job_post_velocity, 0)


def run_tests():
    """Ejecutar todos los tests"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Agregar tests
    suite.addTests(loader.loadTestsFromTestCase(TestFeatureEngineering))
    suite.addTests(loader.loadTestsFromTestCase(TestMLPredictor))
    suite.addTests(loader.loadTestsFromTestCase(TestDataIntegrity))
    
    # Ejecutar
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == '__main__':
    print("\n" + "="*80)
    print("🧪 TESTING ML ENGINE")
    print("="*80 + "\n")
    
    success = run_tests()
    
    print("\n" + "="*80)
    if success:
        print("✅ ALL TESTS PASSED!")
    else:
        print("❌ SOME TESTS FAILED")
    print("="*80 + "\n")
    
    sys.exit(0 if success else 1)
