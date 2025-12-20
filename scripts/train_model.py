"""
Training Script - Entrenamiento del Modelo de Predicción
Genera datos sintéticos para entrenar el modelo XGBoost
"""

import logging
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path
import sys

# Agregar src al path
sys.path.append(str(Path(__file__).parent.parent / 'src'))

from ml_predictor import HiringProbabilityPredictor
from feature_engineering import FeatureEngineer, CompanyFeatures

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SyntheticDataGenerator:
    """Genera datos sintéticos para entrenar el modelo"""
    
    def __init__(self, n_samples: int = 1000):
        self.n_samples = n_samples
        self.feature_engineer = FeatureEngineer()
        
    def generate_training_data(self) -> tuple[pd.DataFrame, np.ndarray]:
        """
        Genera dataset sintético de entrenamiento
        
        Returns:
            (X, y) donde X son features y y son labels
        """
        logger.info(f"Generating {self.n_samples} synthetic training samples...")
        
        features_list = []
        labels = []
        
        for i in range(self.n_samples):
            # Generar features aleatorias con distribuciones realistas
            features, label = self._generate_sample(i)
            features_list.append(features)
            labels.append(label)
        
        # Convertir a DataFrame
        X_list = []
        for features in features_list:
            df = self.feature_engineer.features_to_dataframe(features)
            X_list.append(df)
        
        X = pd.concat(X_list, ignore_index=True)
        y = np.array(labels)
        
        logger.info(f"Generated {len(X)} samples")
        logger.info(f"Positive samples (hired): {y.sum()} ({y.mean()*100:.1f}%)")
        logger.info(f"Negative samples (not hired): {len(y) - y.sum()} ({(1-y.mean())*100:.1f}%)")
        
        return X, y
    
    def _generate_sample(self, idx: int) -> tuple[CompanyFeatures, int]:
        """Genera una muestra individual"""
        
        # Determinar si contrató (con sesgo realista)
        # 30% de las empresas contratan en 3 meses
        did_hire = np.random.random() < 0.3
        
        # Generar features con correlación a hiring
        if did_hire:
            # Alta probabilidad de contratación
            funding_recency = np.random.choice([
                np.random.randint(10, 90),      # 40% muy reciente
                np.random.randint(90, 180),     # 35% reciente
                np.random.randint(180, 365)     # 25% no tan reciente
            ], p=[0.4, 0.35, 0.25])
            
            tech_churn = np.random.choice([
                np.random.uniform(15, 25),      # 30% churn alto
                np.random.uniform(8, 15),       # 40% churn moderado
                np.random.uniform(2, 8)         # 30% churn bajo
            ], p=[0.3, 0.4, 0.3])
            
            senior_departures = np.random.choice([0, 1, 2, 3, 4, 5], p=[0.1, 0.2, 0.25, 0.25, 0.15, 0.05])
            
            job_post_velocity = np.random.choice([
                np.random.uniform(2.0, 4.0),    # 35% surge
                np.random.uniform(1.3, 2.0),    # 40% crecimiento
                np.random.uniform(0.8, 1.3)     # 25% estable
            ], p=[0.35, 0.4, 0.25])
            
            current_month_posts = int(np.random.choice([
                np.random.randint(5, 15),       # 40% muchas vacantes
                np.random.randint(2, 5),        # 35% pocas vacantes
                np.random.randint(0, 2)         # 25% muy pocas
            ], p=[0.4, 0.35, 0.25]))
            
            tech_roles_ratio = np.random.uniform(50, 90)
            
            region = np.random.choice(['us', 'sa', 'eu', 'ap'], p=[0.35, 0.30, 0.20, 0.15])
            
            last_funding_amount = np.random.choice([
                np.random.uniform(5, 20),       # Series A
                np.random.uniform(20, 60),      # Series B
                np.random.uniform(60, 150)      # Series C+
            ], p=[0.4, 0.4, 0.2])
            
            funding_stage = np.random.choice(
                ['series-a', 'series-b', 'series-c'],
                p=[0.4, 0.4, 0.2]
            )
            
        else:
            # Baja probabilidad de contratación
            funding_recency = np.random.choice([
                np.random.randint(10, 90),      # 15% reciente pero no contratan
                np.random.randint(180, 365),    # 40% antiguo
                np.random.randint(365, 730)     # 45% muy antiguo
            ], p=[0.15, 0.4, 0.45])
            
            tech_churn = np.random.uniform(1, 10)  # Churn bajo generalmente
            
            senior_departures = np.random.choice([0, 1, 2], p=[0.6, 0.3, 0.1])
            
            job_post_velocity = np.random.choice([
                np.random.uniform(0.0, 0.5),    # 40% decrecimiento
                np.random.uniform(0.5, 1.0),    # 35% estable bajo
                np.random.uniform(1.0, 1.5)     # 25% ligero crecimiento
            ], p=[0.4, 0.35, 0.25])
            
            current_month_posts = int(np.random.choice([
                0,                              # 30% sin vacantes
                np.random.randint(1, 3),        # 45% pocas
                np.random.randint(3, 8)         # 25% algunas
            ], p=[0.3, 0.45, 0.25]))
            
            tech_roles_ratio = np.random.uniform(20, 60)
            
            region = np.random.choice(['us', 'eu', 'sa', 'ap'], p=[0.25, 0.45, 0.15, 0.15])
            
            last_funding_amount = np.random.uniform(1, 15)
            
            funding_stage = np.random.choice(
                ['seed', 'series-a', 'unknown'],
                p=[0.3, 0.4, 0.3]
            )
        
        # Features comunes
        team_size = int(np.random.choice([
            np.random.randint(10, 50),          # Small
            np.random.randint(50, 150),         # Medium
            np.random.randint(150, 500)         # Large
        ], p=[0.5, 0.35, 0.15]))
        
        engineering_headcount = int(team_size * np.random.uniform(0.3, 0.6))
        
        company_age_days = int(np.random.choice([
            np.random.randint(180, 730),        # <2 años
            np.random.randint(730, 1825),       # 2-5 años
            np.random.randint(1825, 3650)       # 5-10 años
        ], p=[0.3, 0.5, 0.2]))
        
        total_funding = last_funding_amount * np.random.uniform(1.5, 3.0)
        
        previous_month_posts = int(current_month_posts / job_post_velocity) if job_post_velocity > 0 else 0
        
        # Crear CompanyFeatures
        features = CompanyFeatures(
            company_id=f"synthetic-{idx}",
            company_name=f"Company {idx}",
            funding_recency=funding_recency,
            last_funding_amount=last_funding_amount,
            funding_stage=funding_stage,
            tech_churn=tech_churn,
            senior_departures=senior_departures,
            engineering_headcount=engineering_headcount,
            job_post_velocity=job_post_velocity,
            current_month_posts=current_month_posts,
            previous_month_posts=previous_month_posts,
            tech_roles_ratio=tech_roles_ratio,
            region_factor=self.feature_engineer.region_coefficients.get(region, 1.0),
            region=region,
            company_age_days=company_age_days,
            total_funding=total_funding,
            team_size=team_size,
            growth_stage=self.feature_engineer._classify_growth_stage(funding_stage),
            calculated_at=datetime.now().isoformat()
        )
        
        label = 1 if did_hire else 0
        
        return features, label


def main():
    """Script principal de entrenamiento"""
    
    print("\n" + "="*80)
    print("🤖 TRAINING ML MODEL - Probabilidad de Contratación IT")
    print("="*80 + "\n")
    
    # Generar datos sintéticos
    generator = SyntheticDataGenerator(n_samples=2000)
    X, y = generator.generate_training_data()
    
    print("\n" + "-"*80)
    print("Dataset Statistics:")
    print("-"*80)
    print(X.describe())
    
    # Entrenar modelo XGBoost
    print("\n" + "="*80)
    print("Training XGBoost Model...")
    print("="*80 + "\n")
    
    predictor_xgb = HiringProbabilityPredictor(
        model_path='models/hiring_predictor_xgboost.pkl',
        model_type='xgboost'
    )
    
    metrics_xgb = predictor_xgb.train(
        X, y,
        test_size=0.2,
        max_depth=6,
        learning_rate=0.1,
        n_estimators=200
    )
    
    print("\n📊 XGBoost Results:")
    print(f"  Train Accuracy: {metrics_xgb['train_accuracy']:.3f}")
    print(f"  Test Accuracy: {metrics_xgb['test_accuracy']:.3f}")
    print(f"  ROC AUC: {metrics_xgb['roc_auc']:.3f}")
    print(f"  CV Score: {metrics_xgb['cv_mean']:.3f} (+/- {metrics_xgb['cv_std']:.3f})")
    
    # Entrenar modelo Random Forest
    print("\n" + "="*80)
    print("Training Random Forest Model...")
    print("="*80 + "\n")
    
    predictor_rf = HiringProbabilityPredictor(
        model_path='models/hiring_predictor_rf.pkl',
        model_type='random_forest'
    )
    
    metrics_rf = predictor_rf.train(
        X, y,
        test_size=0.2,
        n_estimators=200,
        max_depth=10
    )
    
    print("\n📊 Random Forest Results:")
    print(f"  Train Accuracy: {metrics_rf['train_accuracy']:.3f}")
    print(f"  Test Accuracy: {metrics_rf['test_accuracy']:.3f}")
    print(f"  ROC AUC: {metrics_rf['roc_auc']:.3f}")
    print(f"  CV Score: {metrics_rf['cv_mean']:.3f} (+/- {metrics_rf['cv_std']:.3f})")
    
    # Comparar modelos
    print("\n" + "="*80)
    print("Model Comparison:")
    print("="*80)
    print(f"\n{'Metric':<20} {'XGBoost':<15} {'Random Forest':<15}")
    print("-"*50)
    print(f"{'Test Accuracy':<20} {metrics_xgb['test_accuracy']:<15.3f} {metrics_rf['test_accuracy']:<15.3f}")
    print(f"{'ROC AUC':<20} {metrics_xgb['roc_auc']:<15.3f} {metrics_rf['roc_auc']:<15.3f}")
    print(f"{'CV Score':<20} {metrics_xgb['cv_mean']:<15.3f} {metrics_rf['cv_mean']:<15.3f}")
    
    # Determinar mejor modelo
    best_model = 'XGBoost' if metrics_xgb['roc_auc'] > metrics_rf['roc_auc'] else 'Random Forest'
    print(f"\n🏆 Best Model: {best_model}")
    
    # Test de predicción
    print("\n" + "="*80)
    print("Testing Predictions:")
    print("="*80 + "\n")
    
    # Crear empresa de prueba con alta probabilidad
    test_features_high = CompanyFeatures(
        company_id='test-high',
        company_name='High Probability Startup',
        funding_recency=45,
        last_funding_amount=35.0,
        funding_stage='series-b',
        tech_churn=18.5,
        senior_departures=4,
        engineering_headcount=80,
        job_post_velocity=3.2,
        current_month_posts=12,
        previous_month_posts=4,
        tech_roles_ratio=75.0,
        region_factor=1.25,
        region='sa',
        company_age_days=1100,
        total_funding=50.0,
        team_size=140,
        growth_stage='growth',
        calculated_at=datetime.now().isoformat()
    )
    
    # Predecir con mejor modelo
    best_predictor = predictor_xgb if best_model == 'XGBoost' else predictor_rf
    prediction = best_predictor.predict(test_features_high, explain=True)
    
    print(f"Company: {prediction['company_name']}")
    print(f"Probability: {prediction['prediction']['probability']}%")
    print(f"Label: {prediction['prediction']['label']}")
    print(f"Confidence: {prediction['prediction']['confidence']}")
    print("\nReasons:")
    for i, reason in enumerate(prediction['reasons'], 1):
        print(f"{i}. {reason}")
    
    print("\n" + "="*80)
    print("✅ Training Complete!")
    print("="*80)
    print(f"\nModels saved:")
    print(f"  - models/hiring_predictor_xgboost.pkl")
    print(f"  - models/hiring_predictor_rf.pkl")
    print(f"\nRecommended model: {best_model}")
    print("\nNext steps:")
    print("  1. Run predictions: python src/run_predictions.py")
    print("  2. Integrate with pipeline: python src/main.py --ml-predict")
    print("="*80 + "\n")


if __name__ == "__main__":
    main()
