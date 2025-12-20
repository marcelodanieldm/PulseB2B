"""
Feature Engineering Module
Extrae y calcula features para predicción de contratación IT
"""

import logging
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import numpy as np
import pandas as pd
from dataclasses import dataclass

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class CompanyFeatures:
    """Features de una empresa para predicción"""
    company_id: str
    company_name: str
    
    # Feature 1: Funding Recency
    funding_recency: float  # Días desde último funding
    last_funding_amount: float  # Millones USD
    funding_stage: str  # seed, series-a, series-b, etc.
    
    # Feature 2: Tech Churn
    tech_churn: float  # Rotación de devs (%)
    senior_departures: int  # Número de seniors que salieron
    engineering_headcount: int  # Total de ingenieros
    
    # Feature 3: Job Post Velocity
    job_post_velocity: float  # Ratio vs. mes anterior
    current_month_posts: int
    previous_month_posts: int
    tech_roles_ratio: float  # % de vacantes tech vs. total
    
    # Feature 4: Region Factor
    region_factor: float  # Coeficiente económico regional
    region: str  # us, eu, sa, ap
    
    # Features adicionales
    company_age_days: int
    total_funding: float
    team_size: int
    growth_stage: str
    
    # Metadata
    calculated_at: str


class FeatureEngineer:
    """Ingeniero de features para predicción de contratación"""
    
    def __init__(self):
        # Coeficientes regionales (basados en datos del mercado 2025)
        self.region_coefficients = {
            'us': 1.15,      # Tech boom continúa
            'eu': 0.85,      # Estancamiento post-Brexit
            'sa': 1.25,      # Brasil tech boom explosivo
            'ap': 1.10,      # Asia-Pacífico crecimiento sólido
            'default': 1.0
        }
        
        # Pesos de funding stage (probabilidad base de contratar)
        self.funding_stage_weights = {
            'pre-seed': 0.3,
            'seed': 0.5,
            'series-a': 0.8,
            'series-b': 0.9,
            'series-c': 0.85,
            'series-d': 0.75,
            'series-e+': 0.6,
            'unknown': 0.4
        }
        
        # Umbrales críticos
        self.thresholds = {
            'high_churn': 15.0,        # % mensual
            'recent_funding_days': 180,  # 6 meses
            'velocity_surge': 2.0,     # 2x más vacantes
            'senior_exodus': 3         # 3+ seniors en 30 días
        }
    
    def extract_features(
        self,
        company_data: Dict,
        jobs_data: List[Dict],
        funding_data: List[Dict],
        linkedin_data: Optional[Dict] = None
    ) -> CompanyFeatures:
        """
        Extrae todas las features de una empresa
        
        Args:
            company_data: Datos básicos de la empresa
            jobs_data: Historial de vacantes
            funding_data: Historial de funding
            linkedin_data: Datos de LinkedIn (opcional)
            
        Returns:
            CompanyFeatures con todos los valores calculados
        """
        logger.info(f"Extracting features for {company_data.get('name', 'Unknown')}")
        
        # Feature 1: Funding Recency
        funding_features = self._calculate_funding_features(funding_data)
        
        # Feature 2: Tech Churn
        churn_features = self._calculate_churn_features(
            company_data,
            linkedin_data or {}
        )
        
        # Feature 3: Job Post Velocity
        velocity_features = self._calculate_velocity_features(jobs_data)
        
        # Feature 4: Region Factor
        region_features = self._calculate_region_features(
            company_data.get('region', 'us')
        )
        
        # Features adicionales
        company_age = self._calculate_company_age(
            company_data.get('founded_date')
        )
        
        return CompanyFeatures(
            company_id=company_data.get('id', ''),
            company_name=company_data.get('name', ''),
            
            # Funding
            funding_recency=funding_features['recency'],
            last_funding_amount=funding_features['amount'],
            funding_stage=funding_features['stage'],
            
            # Churn
            tech_churn=churn_features['churn_rate'],
            senior_departures=churn_features['senior_departures'],
            engineering_headcount=churn_features['headcount'],
            
            # Velocity
            job_post_velocity=velocity_features['velocity'],
            current_month_posts=velocity_features['current'],
            previous_month_posts=velocity_features['previous'],
            tech_roles_ratio=velocity_features['tech_ratio'],
            
            # Region
            region_factor=region_features['factor'],
            region=region_features['region'],
            
            # Adicionales
            company_age_days=company_age,
            total_funding=funding_features['total'],
            team_size=company_data.get('team_size', 0),
            growth_stage=self._classify_growth_stage(funding_features['stage']),
            
            calculated_at=datetime.now().isoformat()
        )
    
    def _calculate_funding_features(self, funding_data: List[Dict]) -> Dict:
        """Calcula features relacionadas con funding"""
        if not funding_data:
            return {
                'recency': 999,  # Sin funding = muy antiguo
                'amount': 0,
                'stage': 'unknown',
                'total': 0
            }
        
        # Ordenar por fecha
        sorted_funding = sorted(
            funding_data,
            key=lambda x: x.get('date', datetime.min),
            reverse=True
        )
        
        last_round = sorted_funding[0]
        last_date = last_round.get('date', datetime.now())
        
        if isinstance(last_date, str):
            last_date = datetime.fromisoformat(last_date.replace('Z', '+00:00'))
        
        # Días desde último funding
        recency = (datetime.now() - last_date).days
        
        # Total funding
        total = sum(r.get('amount', 0) for r in funding_data)
        
        return {
            'recency': recency,
            'amount': last_round.get('amount', 0),
            'stage': last_round.get('round_type', 'unknown'),
            'total': total
        }
    
    def _calculate_churn_features(
        self,
        company_data: Dict,
        linkedin_data: Dict
    ) -> Dict:
        """Calcula features de rotación de personal"""
        
        # Si no hay datos de LinkedIn, estimar basándose en otros indicadores
        if not linkedin_data or 'departures' not in linkedin_data:
            # Estimación basada en industria
            team_size = company_data.get('team_size', 50)
            
            # Churn promedio tech industry: ~13% anual = ~1.1% mensual
            estimated_churn = 1.1
            
            return {
                'churn_rate': estimated_churn,
                'senior_departures': 0,
                'headcount': team_size,
                'is_estimated': True
            }
        
        # Datos reales de LinkedIn
        departures = linkedin_data.get('departures', [])
        current_headcount = linkedin_data.get('current_headcount', 
                                             company_data.get('team_size', 50))
        
        # Filtrar últimos 30 días
        recent_departures = [
            d for d in departures
            if self._is_recent(d.get('departure_date'), days=30)
        ]
        
        # Contar senior departures
        senior_departures = len([
            d for d in recent_departures
            if d.get('seniority', '').lower() in ['senior', 'staff', 'principal', 'lead']
        ])
        
        # Calcular churn rate mensual
        if current_headcount > 0:
            churn_rate = (len(recent_departures) / current_headcount) * 100
        else:
            churn_rate = 0
        
        return {
            'churn_rate': round(churn_rate, 2),
            'senior_departures': senior_departures,
            'headcount': current_headcount,
            'is_estimated': False
        }
    
    def _calculate_velocity_features(self, jobs_data: List[Dict]) -> Dict:
        """Calcula velocidad de publicación de vacantes"""
        if not jobs_data:
            return {
                'velocity': 0,
                'current': 0,
                'previous': 0,
                'tech_ratio': 0
            }
        
        now = datetime.now()
        current_month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        previous_month_start = (current_month_start - timedelta(days=1)).replace(day=1)
        
        # Contar vacantes por período
        current_month_jobs = []
        previous_month_jobs = []
        
        for job in jobs_data:
            scraped_at = job.get('scraped_at', '')
            if isinstance(scraped_at, str):
                try:
                    scraped_at = datetime.fromisoformat(scraped_at.replace('Z', '+00:00'))
                except:
                    continue
            
            if scraped_at >= current_month_start:
                current_month_jobs.append(job)
            elif scraped_at >= previous_month_start and scraped_at < current_month_start:
                previous_month_jobs.append(job)
        
        current_count = len(current_month_jobs)
        previous_count = len(previous_month_jobs)
        
        # Calcular velocity (ratio mes actual vs. anterior)
        if previous_count > 0:
            velocity = current_count / previous_count
        elif current_count > 0:
            velocity = 2.0  # Si no había antes y ahora sí = surge
        else:
            velocity = 0
        
        # Calcular ratio de roles tech
        tech_keywords = [
            'engineer', 'developer', 'software', 'devops', 'architect',
            'data scientist', 'machine learning', 'ml', 'ai', 'backend',
            'frontend', 'full stack', 'fullstack', 'sre', 'platform'
        ]
        
        tech_jobs = [
            job for job in current_month_jobs
            if any(kw in job.get('title', '').lower() for kw in tech_keywords)
        ]
        
        tech_ratio = (len(tech_jobs) / current_count * 100) if current_count > 0 else 0
        
        return {
            'velocity': round(velocity, 2),
            'current': current_count,
            'previous': previous_count,
            'tech_ratio': round(tech_ratio, 1)
        }
    
    def _calculate_region_features(self, region: str) -> Dict:
        """Calcula coeficiente regional"""
        region_clean = region.lower().strip()
        factor = self.region_coefficients.get(region_clean, 
                                              self.region_coefficients['default'])
        
        return {
            'factor': factor,
            'region': region_clean
        }
    
    def _calculate_company_age(self, founded_date) -> int:
        """Calcula edad de la empresa en días"""
        if not founded_date:
            return 1825  # ~5 años por defecto
        
        if isinstance(founded_date, str):
            try:
                founded_date = datetime.fromisoformat(founded_date.replace('Z', '+00:00'))
            except:
                return 1825
        
        return (datetime.now() - founded_date).days
    
    def _classify_growth_stage(self, funding_stage: str) -> str:
        """Clasifica etapa de crecimiento"""
        stage_mapping = {
            'pre-seed': 'early',
            'seed': 'early',
            'series-a': 'growth',
            'series-b': 'growth',
            'series-c': 'scale',
            'series-d': 'scale',
            'series-e+': 'mature',
            'unknown': 'unknown'
        }
        return stage_mapping.get(funding_stage.lower(), 'unknown')
    
    def _is_recent(self, date, days: int = 30) -> bool:
        """Verifica si una fecha es reciente"""
        if not date:
            return False
        
        if isinstance(date, str):
            try:
                date = datetime.fromisoformat(date.replace('Z', '+00:00'))
            except:
                return False
        
        cutoff = datetime.now() - timedelta(days=days)
        return date >= cutoff
    
    def features_to_dataframe(self, features: CompanyFeatures) -> pd.DataFrame:
        """Convierte features a DataFrame para el modelo"""
        return pd.DataFrame([{
            'funding_recency': features.funding_recency,
            'last_funding_amount': features.last_funding_amount,
            'tech_churn': features.tech_churn,
            'senior_departures': features.senior_departures,
            'job_post_velocity': features.job_post_velocity,
            'tech_roles_ratio': features.tech_roles_ratio,
            'region_factor': features.region_factor,
            'company_age_days': features.company_age_days,
            'total_funding': features.total_funding,
            'team_size': features.team_size,
            'engineering_headcount': features.engineering_headcount,
            'current_month_posts': features.current_month_posts,
            
            # Encoding de categorías
            'funding_stage_weight': self.funding_stage_weights.get(
                features.funding_stage.lower(),
                self.funding_stage_weights['unknown']
            ),
            
            # Features derivadas
            'funding_per_employee': (
                features.total_funding / features.team_size 
                if features.team_size > 0 else 0
            ),
            'is_recent_funding': int(features.funding_recency < self.thresholds['recent_funding_days']),
            'has_high_churn': int(features.tech_churn > self.thresholds['high_churn']),
            'has_velocity_surge': int(features.job_post_velocity > self.thresholds['velocity_surge']),
            'has_senior_exodus': int(features.senior_departures >= self.thresholds['senior_exodus'])
        }])
    
    def get_feature_importance_explanation(self, features: CompanyFeatures) -> Dict:
        """Genera explicación de features para interpretabilidad"""
        explanations = {
            'funding_signal': self._explain_funding(features),
            'churn_signal': self._explain_churn(features),
            'velocity_signal': self._explain_velocity(features),
            'region_signal': self._explain_region(features)
        }
        
        return explanations
    
    def _explain_funding(self, features: CompanyFeatures) -> Dict:
        """Explica señal de funding"""
        recency = features.funding_recency
        
        if recency < 90:
            signal = 'strong_positive'
            explanation = f"Funding muy reciente ({recency} días). Alta probabilidad de expansión."
        elif recency < 180:
            signal = 'moderate_positive'
            explanation = f"Funding reciente ({recency} días). Probable contratación activa."
        elif recency < 365:
            signal = 'neutral'
            explanation = f"Funding hace {recency} días. Señal neutral."
        else:
            signal = 'negative'
            explanation = f"Funding antiguo ({recency} días). Puede indicar dificultad para levantar capital."
        
        return {
            'signal': signal,
            'explanation': explanation,
            'value': recency,
            'stage': features.funding_stage,
            'amount': features.last_funding_amount
        }
    
    def _explain_churn(self, features: CompanyFeatures) -> Dict:
        """Explica señal de churn"""
        churn = features.tech_churn
        senior_exits = features.senior_departures
        
        if senior_exits >= 3:
            signal = 'strong_positive'
            explanation = f"{senior_exits} seniors salieron recientemente. Necesidad urgente de reemplazos."
        elif churn > 15:
            signal = 'moderate_positive'
            explanation = f"Churn alto ({churn}%). Probables contrataciones de reemplazo."
        elif churn > 8:
            signal = 'slight_positive'
            explanation = f"Churn moderado ({churn}%). Contratación normal."
        else:
            signal = 'neutral'
            explanation = f"Churn bajo ({churn}%). Equipo estable."
        
        return {
            'signal': signal,
            'explanation': explanation,
            'churn_rate': churn,
            'senior_departures': senior_exits
        }
    
    def _explain_velocity(self, features: CompanyFeatures) -> Dict:
        """Explica señal de velocity"""
        velocity = features.job_post_velocity
        tech_ratio = features.tech_roles_ratio
        
        if velocity > 2.5:
            signal = 'strong_positive'
            explanation = f"Surge de vacantes ({velocity:.1f}x vs. mes anterior). Expansión agresiva."
        elif velocity > 1.5:
            signal = 'moderate_positive'
            explanation = f"Aumento de vacantes ({velocity:.1f}x). Crecimiento activo."
        elif velocity > 0.8:
            signal = 'neutral'
            explanation = f"Publicación constante de vacantes ({velocity:.1f}x)."
        else:
            signal = 'negative'
            explanation = f"Disminución de vacantes ({velocity:.1f}x). Posible contracción."
        
        if tech_ratio > 70:
            explanation += f" {tech_ratio:.0f}% son roles tech."
        
        return {
            'signal': signal,
            'explanation': explanation,
            'velocity': velocity,
            'tech_ratio': tech_ratio,
            'current_posts': features.current_month_posts
        }
    
    def _explain_region(self, features: CompanyFeatures) -> Dict:
        """Explica factor regional"""
        factor = features.region_factor
        region = features.region
        
        region_descriptions = {
            'us': 'Estados Unidos mantiene boom tecnológico',
            'eu': 'Europa con estancamiento post-crisis',
            'sa': 'Latinoamérica (Brasil) con explosión tech',
            'ap': 'Asia-Pacífico con crecimiento sólido'
        }
        
        explanation = region_descriptions.get(region, 'Región desconocida')
        
        if factor > 1.1:
            signal = 'positive'
            explanation += f". Factor {factor:.2f} favorece contratación."
        elif factor < 0.9:
            signal = 'negative'
            explanation += f". Factor {factor:.2f} limita contratación."
        else:
            signal = 'neutral'
            explanation += f". Factor {factor:.2f} neutral."
        
        return {
            'signal': signal,
            'explanation': explanation,
            'factor': factor,
            'region': region
        }


if __name__ == "__main__":
    # Test del feature engineer
    engineer = FeatureEngineer()
    
    # Datos de prueba
    company_data = {
        'id': 'test-123',
        'name': 'TestStartup',
        'region': 'sa',
        'team_size': 75,
        'founded_date': datetime(2020, 1, 1)
    }
    
    funding_data = [
        {
            'round_type': 'series-a',
            'amount': 15.0,
            'date': datetime.now() - timedelta(days=45)
        }
    ]
    
    jobs_data = [
        {
            'title': 'Senior Software Engineer',
            'scraped_at': datetime.now()
        },
        {
            'title': 'ML Engineer',
            'scraped_at': datetime.now() - timedelta(days=5)
        }
    ]
    
    linkedin_data = {
        'current_headcount': 75,
        'departures': [
            {'seniority': 'senior', 'departure_date': datetime.now() - timedelta(days=10)},
            {'seniority': 'senior', 'departure_date': datetime.now() - timedelta(days=15)},
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
    
    print("\n=== Company Features ===")
    print(f"Company: {features.company_name}")
    print(f"Funding Recency: {features.funding_recency} days")
    print(f"Tech Churn: {features.tech_churn}%")
    print(f"Job Velocity: {features.job_post_velocity}x")
    print(f"Region Factor: {features.region_factor}")
    
    # Convertir a DataFrame
    df = engineer.features_to_dataframe(features)
    print("\n=== DataFrame ===")
    print(df.T)
    
    # Explicaciones
    explanations = engineer.get_feature_importance_explanation(features)
    print("\n=== Feature Explanations ===")
    for key, value in explanations.items():
        print(f"\n{key}:")
        print(f"  Signal: {value['signal']}")
        print(f"  {value['explanation']}")
