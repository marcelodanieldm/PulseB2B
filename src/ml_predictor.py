"""
ML Predictor - Predicción de Probabilidad de Contratación IT
Modelo XGBoost con explicabilidad integrada
"""

import logging
import json
import pickle
from typing import Dict, List, Tuple
from datetime import datetime
from pathlib import Path
import numpy as np
import pandas as pd

try:
    import xgboost as xgb
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.model_selection import train_test_split, cross_val_score
    from sklearn.metrics import classification_report, roc_auc_score
    import shap
except ImportError as e:
    logging.warning(f"ML libraries not installed: {e}")

from feature_engineering import FeatureEngineer, CompanyFeatures

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class HiringProbabilityPredictor:
    """
    Motor de IA para predicción de contratación IT
    Usa XGBoost con explicabilidad SHAP
    """
    
    def __init__(self, model_path: str = None, model_type: str = 'xgboost'):
        """
        Args:
            model_path: Ruta al modelo entrenado
            model_type: 'xgboost' o 'random_forest'
        """
        self.model_type = model_type
        self.model = None
        self.feature_engineer = FeatureEngineer()
        self.model_path = model_path or 'models/hiring_predictor.pkl'
        self.explainer = None
        
        # Feature names esperadas
        self.feature_names = [
            'funding_recency',
            'last_funding_amount',
            'tech_churn',
            'senior_departures',
            'job_post_velocity',
            'tech_roles_ratio',
            'region_factor',
            'company_age_days',
            'total_funding',
            'team_size',
            'engineering_headcount',
            'current_month_posts',
            'funding_stage_weight',
            'funding_per_employee',
            'is_recent_funding',
            'has_high_churn',
            'has_velocity_surge',
            'has_senior_exodus'
        ]
        
        # Cargar modelo si existe
        if Path(self.model_path).exists():
            self.load_model()
    
    def train(
        self,
        training_data: pd.DataFrame,
        labels: np.ndarray,
        test_size: float = 0.2,
        **model_params
    ):
        """
        Entrena el modelo predictivo
        
        Args:
            training_data: DataFrame con features
            labels: Array de labels (0 o 1, donde 1 = contrató en próximos 3 meses)
            test_size: Proporción para test set
            **model_params: Parámetros adicionales para el modelo
        """
        logger.info(f"Training {self.model_type} model with {len(training_data)} samples")
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            training_data[self.feature_names],
            labels,
            test_size=test_size,
            random_state=42,
            stratify=labels
        )
        
        # Inicializar modelo
        if self.model_type == 'xgboost':
            default_params = {
                'max_depth': 6,
                'learning_rate': 0.1,
                'n_estimators': 200,
                'objective': 'binary:logistic',
                'eval_metric': 'logloss',
                'use_label_encoder': False,
                'random_state': 42
            }
            default_params.update(model_params)
            
            self.model = xgb.XGBClassifier(**default_params)
            
        elif self.model_type == 'random_forest':
            default_params = {
                'n_estimators': 200,
                'max_depth': 10,
                'min_samples_split': 5,
                'random_state': 42,
                'n_jobs': -1
            }
            default_params.update(model_params)
            
            self.model = RandomForestClassifier(**default_params)
        
        # Entrenar
        self.model.fit(X_train, y_train)
        
        # Evaluar
        train_score = self.model.score(X_train, y_train)
        test_score = self.model.score(X_test, y_test)
        
        y_pred_proba = self.model.predict_proba(X_test)[:, 1]
        roc_auc = roc_auc_score(y_test, y_pred_proba)
        
        logger.info(f"Training accuracy: {train_score:.3f}")
        logger.info(f"Test accuracy: {test_score:.3f}")
        logger.info(f"ROC AUC: {roc_auc:.3f}")
        
        # Cross-validation
        cv_scores = cross_val_score(self.model, X_train, y_train, cv=5)
        logger.info(f"CV scores: {cv_scores.mean():.3f} (+/- {cv_scores.std() * 2:.3f})")
        
        # Inicializar SHAP explainer
        try:
            if self.model_type == 'xgboost':
                self.explainer = shap.TreeExplainer(self.model)
            else:
                self.explainer = shap.TreeExplainer(self.model)
            logger.info("SHAP explainer initialized")
        except Exception as e:
            logger.warning(f"Could not initialize SHAP: {e}")
        
        # Guardar modelo
        self.save_model()
        
        return {
            'train_accuracy': train_score,
            'test_accuracy': test_score,
            'roc_auc': roc_auc,
            'cv_mean': cv_scores.mean(),
            'cv_std': cv_scores.std()
        }
    
    def predict(
        self,
        features: CompanyFeatures,
        explain: bool = True
    ) -> Dict:
        """
        Predice probabilidad de contratación para una empresa
        
        Args:
            features: CompanyFeatures object
            explain: Si True, incluye explicación SHAP
            
        Returns:
            Dict con predicción, probabilidad y razones
        """
        if self.model is None:
            raise ValueError("Model not loaded. Train or load a model first.")
        
        logger.info(f"Predicting for {features.company_name}")
        
        # Convertir features a DataFrame
        X = self.feature_engineer.features_to_dataframe(features)
        
        # Asegurar orden correcto de features
        X = X[self.feature_names]
        
        # Predicción
        probability = self.model.predict_proba(X)[0, 1] * 100  # Convertir a porcentaje
        prediction_class = int(probability >= 50)
        
        # Generar razones
        reasons = self._generate_reasons(features, X, probability)
        
        # Explicación SHAP
        shap_explanation = None
        if explain and self.explainer is not None:
            try:
                shap_values = self.explainer.shap_values(X)
                if isinstance(shap_values, list):
                    shap_values = shap_values[1]  # Para clasificación binaria
                
                # Top 5 features por impacto
                feature_impacts = []
                for i, feature_name in enumerate(self.feature_names):
                    feature_impacts.append({
                        'feature': feature_name,
                        'value': float(X[feature_name].iloc[0]),
                        'impact': float(shap_values[0][i])
                    })
                
                # Ordenar por impacto absoluto
                feature_impacts.sort(key=lambda x: abs(x['impact']), reverse=True)
                shap_explanation = feature_impacts[:5]
                
            except Exception as e:
                logger.warning(f"Could not generate SHAP explanation: {e}")
        
        # Feature importance del modelo
        feature_importance = self._get_feature_importance()
        
        return {
            'company_id': features.company_id,
            'company_name': features.company_name,
            'prediction': {
                'probability': round(probability, 2),
                'class': prediction_class,
                'label': 'Alta Probabilidad' if probability >= 70 else 
                        'Probabilidad Media' if probability >= 40 else 
                        'Baja Probabilidad',
                'confidence': self._calculate_confidence(probability)
            },
            'reasons': reasons,
            'features': {
                'funding_recency': features.funding_recency,
                'tech_churn': features.tech_churn,
                'job_post_velocity': features.job_post_velocity,
                'region_factor': features.region_factor,
                'senior_departures': features.senior_departures,
                'current_month_posts': features.current_month_posts,
                'tech_roles_ratio': features.tech_roles_ratio
            },
            'shap_explanation': shap_explanation,
            'feature_importance': feature_importance,
            'metadata': {
                'model_type': self.model_type,
                'predicted_at': datetime.now().isoformat(),
                'prediction_horizon': '3 months'
            }
        }
    
    def _generate_reasons(
        self,
        features: CompanyFeatures,
        X: pd.DataFrame,
        probability: float
    ) -> List[str]:
        """
        Genera 3 razones justificando la predicción
        Basadas en lógica de negocio + feature importance
        """
        reasons = []
        
        # Obtener explicaciones de features
        feature_explanations = self.feature_engineer.get_feature_importance_explanation(features)
        
        # Razón 1: Funding + Churn
        funding_signal = feature_explanations['funding_signal']
        churn_signal = feature_explanations['churn_signal']
        
        if features.funding_recency < 90 and features.senior_departures >= 3:
            reasons.append(
                f"🔥 Reciente {features.funding_stage.upper()} (${features.last_funding_amount}M hace "
                f"{features.funding_recency} días) + {features.senior_departures} bajas de seniors en 1 mes "
                f"= Alta probabilidad de búsqueda inmediata para reemplazos"
            )
        elif features.funding_recency < 180 and features.tech_churn > 10:
            reasons.append(
                f"⚡ Funding reciente ({features.funding_recency} días) con churn elevado "
                f"({features.tech_churn}%) indica necesidad de reforzar equipo técnico"
            )
        elif features.funding_recency < 90:
            reasons.append(
                f"💰 {funding_signal['explanation']}. "
                f"Típicamente empresas contratan 30-90 días post-funding."
            )
        elif features.senior_departures >= 3:
            reasons.append(
                f"👥 {churn_signal['explanation']}. "
                f"Necesidad crítica de reemplazar expertise perdido."
            )
        else:
            reasons.append(
                f"📊 {funding_signal['explanation']}"
            )
        
        # Razón 2: Velocity + Tech Ratio
        velocity_signal = feature_explanations['velocity_signal']
        
        if features.job_post_velocity > 2.0 and features.tech_roles_ratio > 60:
            reasons.append(
                f"🚀 Surge de vacantes tech ({features.job_post_velocity:.1f}x vs. mes anterior) con "
                f"{features.tech_roles_ratio:.0f}% de roles técnicos. Expansión agresiva del equipo de ingeniería."
            )
        elif features.job_post_velocity > 1.5:
            reasons.append(
                f"📈 {velocity_signal['explanation']}. "
                f"Patrón consistente de crecimiento de headcount."
            )
        elif features.current_month_posts > 5:
            reasons.append(
                f"📍 {features.current_month_posts} vacantes activas este mes "
                f"({features.tech_roles_ratio:.0f}% tech). Hiring activo."
            )
        else:
            reasons.append(
                f"⏸️ Velocity baja ({features.job_post_velocity:.1f}x). "
                f"Contratación selectiva o pausa en expansión."
            )
        
        # Razón 3: Regional + Stage
        region_signal = feature_explanations['region_signal']
        
        region_names = {
            'us': 'Estados Unidos',
            'eu': 'Europa',
            'sa': 'Latinoamérica',
            'ap': 'Asia-Pacífico'
        }
        
        region_name = region_names.get(features.region, features.region.upper())
        
        if features.region == 'sa' and features.funding_recency < 180:
            reasons.append(
                f"🌎 {region_name} experimenta boom tech (factor {features.region_factor}). "
                f"Empresas post-funding en región están contratando agresivamente."
            )
        elif features.region == 'us' and features.growth_stage in ['growth', 'scale']:
            reasons.append(
                f"🇺🇸 {region_name} + stage {features.growth_stage.capitalize()} = "
                f"Mercado competitivo requiere hiring continuo (factor {features.region_factor})."
            )
        elif features.region_factor < 0.9:
            reasons.append(
                f"⚠️ {region_signal['explanation']}. "
                f"Macro económico puede limitar expansión de headcount."
            )
        else:
            reasons.append(
                f"🌍 {region_signal['explanation']}"
            )
        
        return reasons[:3]  # Asegurar solo 3 razones
    
    def _calculate_confidence(self, probability: float) -> str:
        """Calcula nivel de confianza en la predicción"""
        if probability >= 80 or probability <= 20:
            return 'Very High'
        elif probability >= 65 or probability <= 35:
            return 'High'
        elif probability >= 55 or probability <= 45:
            return 'Medium'
        else:
            return 'Low'
    
    def _get_feature_importance(self) -> List[Dict]:
        """Obtiene feature importance del modelo"""
        if self.model is None:
            return []
        
        try:
            if self.model_type == 'xgboost':
                importance_dict = self.model.get_booster().get_score(importance_type='gain')
                
                # Convertir a lista ordenada
                importance_list = []
                for feature_name in self.feature_names:
                    # XGBoost usa f0, f1, etc.
                    feature_idx = f"f{self.feature_names.index(feature_name)}"
                    importance = importance_dict.get(feature_idx, 0)
                    
                    if importance > 0:
                        importance_list.append({
                            'feature': feature_name,
                            'importance': float(importance)
                        })
                
            else:  # Random Forest
                importance_list = []
                for feature_name, importance in zip(
                    self.feature_names,
                    self.model.feature_importances_
                ):
                    if importance > 0:
                        importance_list.append({
                            'feature': feature_name,
                            'importance': float(importance)
                        })
            
            # Ordenar por importancia
            importance_list.sort(key=lambda x: x['importance'], reverse=True)
            
            # Normalizar a porcentajes
            total_importance = sum(x['importance'] for x in importance_list)
            if total_importance > 0:
                for item in importance_list:
                    item['importance_pct'] = round(
                        (item['importance'] / total_importance) * 100, 2
                    )
            
            return importance_list[:10]  # Top 10
            
        except Exception as e:
            logger.warning(f"Could not get feature importance: {e}")
            return []
    
    def predict_batch(
        self,
        features_list: List[CompanyFeatures],
        output_file: str = None
    ) -> List[Dict]:
        """
        Predice probabilidad para múltiples empresas
        
        Args:
            features_list: Lista de CompanyFeatures
            output_file: Ruta para guardar resultados en JSON
            
        Returns:
            Lista de predicciones
        """
        logger.info(f"Predicting for {len(features_list)} companies")
        
        predictions = []
        for features in features_list:
            try:
                prediction = self.predict(features, explain=False)
                predictions.append(prediction)
            except Exception as e:
                logger.error(f"Error predicting for {features.company_name}: {e}")
                continue
        
        # Ordenar por probabilidad
        predictions.sort(key=lambda x: x['prediction']['probability'], reverse=True)
        
        # Guardar a archivo si se especifica
        if output_file:
            output_path = Path(output_file)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(predictions, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Predictions saved to {output_file}")
        
        return predictions
    
    def save_model(self, path: str = None):
        """Guarda el modelo entrenado"""
        save_path = path or self.model_path
        save_path = Path(save_path)
        save_path.parent.mkdir(parents=True, exist_ok=True)
        
        model_data = {
            'model': self.model,
            'model_type': self.model_type,
            'feature_names': self.feature_names,
            'trained_at': datetime.now().isoformat()
        }
        
        with open(save_path, 'wb') as f:
            pickle.dump(model_data, f)
        
        logger.info(f"Model saved to {save_path}")
    
    def load_model(self, path: str = None):
        """Carga un modelo entrenado"""
        load_path = path or self.model_path
        
        if not Path(load_path).exists():
            logger.warning(f"Model file not found: {load_path}")
            return False
        
        try:
            with open(load_path, 'rb') as f:
                model_data = pickle.load(f)
            
            self.model = model_data['model']
            self.model_type = model_data['model_type']
            self.feature_names = model_data['feature_names']
            
            # Reinicializar explainer
            try:
                self.explainer = shap.TreeExplainer(self.model)
            except:
                self.explainer = None
            
            logger.info(f"Model loaded from {load_path}")
            logger.info(f"Model trained at: {model_data.get('trained_at', 'Unknown')}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error loading model: {e}")
            return False
    
    def generate_prediction_report(
        self,
        predictions: List[Dict],
        output_file: str = 'data/prediction_report.json'
    ):
        """
        Genera reporte completo de predicciones
        
        Args:
            predictions: Lista de predicciones
            output_file: Archivo de salida
        """
        # Estadísticas generales
        total = len(predictions)
        high_prob = len([p for p in predictions if p['prediction']['probability'] >= 70])
        medium_prob = len([p for p in predictions if 40 <= p['prediction']['probability'] < 70])
        low_prob = len([p for p in predictions if p['prediction']['probability'] < 40])
        
        avg_probability = np.mean([p['prediction']['probability'] for p in predictions])
        
        report = {
            'summary': {
                'total_companies': total,
                'high_probability': high_prob,
                'medium_probability': medium_prob,
                'low_probability': low_prob,
                'average_probability': round(avg_probability, 2),
                'generated_at': datetime.now().isoformat()
            },
            'predictions': predictions,
            'top_candidates': predictions[:10],  # Top 10 por probabilidad
            'model_info': {
                'type': self.model_type,
                'prediction_horizon': '3 months'
            }
        }
        
        # Guardar reporte
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Prediction report saved to {output_file}")
        logger.info(f"High probability: {high_prob}/{total} ({high_prob/total*100:.1f}%)")
        
        return report


if __name__ == "__main__":
    # Ejemplo de uso del predictor
    from datetime import timedelta
    
    # Crear predictor
    predictor = HiringProbabilityPredictor(model_type='xgboost')
    
    # Crear features de ejemplo
    engineer = FeatureEngineer()
    
    company_data = {
        'id': 'test-ai-startup',
        'name': 'AI Startup Brasil',
        'region': 'sa',
        'team_size': 120,
        'founded_date': datetime(2021, 3, 1)
    }
    
    funding_data = [
        {
            'round_type': 'series-b',
            'amount': 45.0,
            'date': datetime.now() - timedelta(days=60)
        },
        {
            'round_type': 'series-a',
            'amount': 12.0,
            'date': datetime.now() - timedelta(days=450)
        }
    ]
    
    jobs_data = [
        {'title': 'Senior ML Engineer', 'scraped_at': datetime.now()},
        {'title': 'Backend Engineer', 'scraped_at': datetime.now() - timedelta(days=2)},
        {'title': 'DevOps Engineer', 'scraped_at': datetime.now() - timedelta(days=5)},
        {'title': 'Product Manager', 'scraped_at': datetime.now() - timedelta(days=7)},
        {'title': 'Data Scientist', 'scraped_at': datetime.now() - timedelta(days=10)}
    ]
    
    linkedin_data = {
        'current_headcount': 120,
        'departures': [
            {'seniority': 'senior', 'departure_date': datetime.now() - timedelta(days=8)},
            {'seniority': 'senior', 'departure_date': datetime.now() - timedelta(days=12)},
            {'seniority': 'staff', 'departure_date': datetime.now() - timedelta(days=15)},
            {'seniority': 'mid', 'departure_date': datetime.now() - timedelta(days=20)}
        ]
    }
    
    # Extraer features
    features = engineer.extract_features(
        company_data,
        jobs_data,
        funding_data,
        linkedin_data
    )
    
    print("\n" + "="*80)
    print("DEMO: ML Predictor (Sin modelo entrenado)")
    print("="*80)
    print(f"\nCompany: {features.company_name}")
    print(f"Region: {features.region.upper()} (Factor: {features.region_factor})")
    print(f"\nFeatures:")
    print(f"  - Funding Recency: {features.funding_recency} days")
    print(f"  - Last Funding: ${features.last_funding_amount}M ({features.funding_stage})")
    print(f"  - Tech Churn: {features.tech_churn}%")
    print(f"  - Senior Departures: {features.senior_departures}")
    print(f"  - Job Velocity: {features.job_post_velocity}x")
    print(f"  - Current Posts: {features.current_month_posts}")
    print(f"  - Tech Roles: {features.tech_roles_ratio}%")
    
    print("\n" + "="*80)
    print("Para usar el predictor:")
    print("1. Ejecuta train_model.py para entrenar el modelo con datos históricos")
    print("2. Luego ejecuta: python src/ml_predictor.py")
    print("="*80)
