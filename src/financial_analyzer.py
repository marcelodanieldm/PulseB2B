"""
Financial Analyzer Module
Calcula el Financial Health Score de empresas basándose en datos de funding,
tamaño de equipo y análisis de noticias
"""

import logging
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass
import math

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class FundingRound:
    """Información de una ronda de financiamiento"""
    round_type: str  # seed, series-a, series-b, etc.
    amount: float  # en millones USD
    date: datetime
    investors: List[str]
    valuation: Optional[float] = None  # en millones USD


@dataclass
class CompanyData:
    """Datos de una empresa"""
    name: str
    team_size: int
    funding_rounds: List[FundingRound]
    founded_date: Optional[datetime] = None
    industry: Optional[str] = None
    location: Optional[str] = None


class FinancialHealthCalculator:
    """Calcula el Financial Health Score de empresas"""
    
    def __init__(self):
        # Parámetros para el cálculo del score
        self.weights = {
            'funding_recency': 0.25,    # Qué tan reciente fue la última ronda
            'funding_amount': 0.20,      # Cantidad total recaudada
            'team_efficiency': 0.20,     # Relación funding/empleado
            'growth_trajectory': 0.15,   # Tendencia de crecimiento
            'funding_velocity': 0.10,    # Frecuencia de rondas
            'news_sentiment': 0.10       # Sentimiento de noticias recientes
        }
        
        # Benchmarks de industria (valores en millones USD)
        self.benchmarks = {
            'seed_amount': 2.0,
            'series_a_amount': 10.0,
            'series_b_amount': 25.0,
            'series_c_amount': 50.0,
            'funding_per_employee': 0.5,  # millones por empleado (promedio)
            'optimal_months_between_rounds': 18
        }
    
    def calculate_health_score(
        self,
        company: CompanyData,
        news_sentiment: Optional[Dict] = None
    ) -> Dict:
        """
        Calcula el Financial Health Score completo
        
        Args:
            company: Datos de la empresa
            news_sentiment: Análisis de sentimiento de noticias recientes
            
        Returns:
            Diccionario con score y desglose de componentes
        """
        if not company.funding_rounds:
            return {
                'overall_score': 0,
                'health_status': 'unknown',
                'message': 'No hay información de funding disponible',
                'components': {}
            }
        
        # Calcular cada componente
        components = {
            'funding_recency': self._calculate_funding_recency(company),
            'funding_amount': self._calculate_funding_amount(company),
            'team_efficiency': self._calculate_team_efficiency(company),
            'growth_trajectory': self._calculate_growth_trajectory(company),
            'funding_velocity': self._calculate_funding_velocity(company),
            'news_sentiment': self._calculate_news_sentiment_score(news_sentiment)
        }
        
        # Calcular score ponderado total (0-100)
        overall_score = sum(
            components[key]['score'] * self.weights[key] * 100
            for key in self.weights.keys()
        )
        
        # Clasificar salud financiera
        health_status = self._classify_health_status(overall_score)
        
        # Generar insights
        insights = self._generate_insights(company, components, overall_score)
        
        # Calcular burn rate estimado (si es posible)
        burn_rate = self._estimate_burn_rate(company)
        runway_months = self._calculate_runway(company, burn_rate)
        
        return {
            'overall_score': round(overall_score, 2),
            'health_status': health_status,
            'components': components,
            'insights': insights,
            'metrics': {
                'total_funding': sum(r.amount for r in company.funding_rounds),
                'last_funding_amount': company.funding_rounds[-1].amount,
                'last_funding_date': company.funding_rounds[-1].date.isoformat(),
                'team_size': company.team_size,
                'estimated_burn_rate': burn_rate,
                'estimated_runway_months': runway_months
            },
            'calculated_at': datetime.now().isoformat()
        }
    
    def _calculate_funding_recency(self, company: CompanyData) -> Dict:
        """Calcula score basado en qué tan reciente fue la última ronda"""
        last_round = company.funding_rounds[-1]
        months_since = (datetime.now() - last_round.date).days / 30.44
        
        # Score decay: 100 a los 0 meses, 50 a los 24 meses, 0 a los 48+ meses
        if months_since <= 12:
            score = 1.0
        elif months_since <= 24:
            score = 1.0 - ((months_since - 12) / 12) * 0.4
        elif months_since <= 48:
            score = 0.6 - ((months_since - 24) / 24) * 0.6
        else:
            score = 0.0
        
        status = 'recent' if months_since <= 18 else 'dated' if months_since <= 36 else 'stale'
        
        return {
            'score': round(score, 3),
            'months_since_last_round': round(months_since, 1),
            'last_round_type': last_round.round_type,
            'status': status
        }
    
    def _calculate_funding_amount(self, company: CompanyData) -> Dict:
        """Calcula score basado en la cantidad total de funding"""
        total_funding = sum(r.amount for r in company.funding_rounds)
        last_round = company.funding_rounds[-1]
        
        # Comparar con benchmarks según el tipo de ronda
        benchmark_key = f"{last_round.round_type.lower().replace('-', '_')}_amount"
        benchmark = self.benchmarks.get(benchmark_key, self.benchmarks['series_a_amount'])
        
        # Score relativo al benchmark (0.5 = en benchmark, más = mejor)
        if total_funding >= benchmark * 2:
            score = 1.0
        elif total_funding >= benchmark:
            score = 0.5 + (total_funding / benchmark - 1) * 0.5
        else:
            score = 0.5 * (total_funding / benchmark)
        
        return {
            'score': round(min(score, 1.0), 3),
            'total_funding_millions': round(total_funding, 2),
            'last_round_amount_millions': round(last_round.amount, 2),
            'benchmark_millions': benchmark,
            'vs_benchmark': round(total_funding / benchmark, 2)
        }
    
    def _calculate_team_efficiency(self, company: CompanyData) -> Dict:
        """Calcula score basado en la eficiencia del equipo (funding por empleado)"""
        if company.team_size == 0:
            return {'score': 0.5, 'status': 'unknown', 'funding_per_employee': 0}
        
        total_funding = sum(r.amount for r in company.funding_rounds)
        funding_per_employee = total_funding / company.team_size
        
        benchmark = self.benchmarks['funding_per_employee']
        
        # Score óptimo en el rango 0.3-0.7 M por empleado
        # Muy poco funding por empleado = mal (no pueden escalar)
        # Demasiado funding por empleado = mal (ineficiencia)
        optimal_low = benchmark * 0.6
        optimal_high = benchmark * 1.4
        
        if optimal_low <= funding_per_employee <= optimal_high:
            score = 1.0
        elif funding_per_employee < optimal_low:
            score = funding_per_employee / optimal_low
        else:  # funding_per_employee > optimal_high
            score = max(0.3, 1.0 - (funding_per_employee - optimal_high) / (benchmark * 2))
        
        # Determinar status
        if funding_per_employee < optimal_low:
            status = 'underfunded'
        elif funding_per_employee > optimal_high:
            status = 'overfunded'
        else:
            status = 'optimal'
        
        return {
            'score': round(score, 3),
            'funding_per_employee_millions': round(funding_per_employee, 3),
            'status': status,
            'optimal_range': [optimal_low, optimal_high]
        }
    
    def _calculate_growth_trajectory(self, company: CompanyData) -> Dict:
        """Calcula score basado en la trayectoria de crecimiento de funding"""
        if len(company.funding_rounds) < 2:
            return {'score': 0.5, 'status': 'insufficient_data'}
        
        # Analizar progresión de rondas
        round_progression = []
        for i, round in enumerate(company.funding_rounds):
            round_progression.append({
                'round': round.round_type,
                'amount': round.amount,
                'date': round.date
            })
        
        # Verificar si cada ronda es mayor que la anterior
        increasing_amounts = True
        growth_rates = []
        
        for i in range(1, len(company.funding_rounds)):
            prev_amount = company.funding_rounds[i-1].amount
            curr_amount = company.funding_rounds[i].amount
            
            if curr_amount <= prev_amount:
                increasing_amounts = False
            
            if prev_amount > 0:
                growth_rate = (curr_amount - prev_amount) / prev_amount
                growth_rates.append(growth_rate)
        
        # Calcular score
        if not growth_rates:
            score = 0.5
            status = 'flat'
        else:
            avg_growth = sum(growth_rates) / len(growth_rates)
            
            if avg_growth >= 2.0:  # 200%+ growth entre rondas
                score = 1.0
                status = 'strong_growth'
            elif avg_growth >= 1.0:  # 100%+ growth
                score = 0.8
                status = 'healthy_growth'
            elif avg_growth >= 0.5:  # 50%+ growth
                score = 0.6
                status = 'moderate_growth'
            elif avg_growth > 0:
                score = 0.4
                status = 'slow_growth'
            else:
                score = 0.2
                status = 'declining'
        
        return {
            'score': round(score, 3),
            'status': status,
            'avg_growth_rate': round(sum(growth_rates) / len(growth_rates) if growth_rates else 0, 2),
            'increasing_amounts': increasing_amounts,
            'num_rounds': len(company.funding_rounds)
        }
    
    def _calculate_funding_velocity(self, company: CompanyData) -> Dict:
        """Calcula score basado en la velocidad/frecuencia de rondas de funding"""
        if len(company.funding_rounds) < 2:
            return {'score': 0.5, 'status': 'single_round'}
        
        # Calcular tiempo promedio entre rondas
        time_deltas = []
        for i in range(1, len(company.funding_rounds)):
            delta_days = (company.funding_rounds[i].date - company.funding_rounds[i-1].date).days
            delta_months = delta_days / 30.44
            time_deltas.append(delta_months)
        
        avg_months_between = sum(time_deltas) / len(time_deltas)
        
        # Score óptimo alrededor de 18 meses entre rondas
        optimal = self.benchmarks['optimal_months_between_rounds']
        
        if 12 <= avg_months_between <= 24:
            score = 1.0
            status = 'optimal'
        elif avg_months_between < 12:
            # Demasiado rápido puede indicar problemas de cash
            score = max(0.3, avg_months_between / 12)
            status = 'too_frequent'
        else:
            # Demasiado lento puede indicar dificultad para recaudar
            score = max(0.3, 1.0 - (avg_months_between - 24) / 36)
            status = 'too_slow'
        
        return {
            'score': round(score, 3),
            'avg_months_between_rounds': round(avg_months_between, 1),
            'status': status,
            'optimal_range': [12, 24]
        }
    
    def _calculate_news_sentiment_score(self, news_sentiment: Optional[Dict]) -> Dict:
        """Convierte análisis de sentimiento de noticias en un score"""
        if not news_sentiment:
            return {'score': 0.5, 'status': 'no_data'}
        
        # Extraer stability score si está disponible
        if 'stability_analysis' in news_sentiment:
            stability = news_sentiment['stability_analysis']
            stability_score = stability.get('stability_score', 50) / 100.0
            
            return {
                'score': round(stability_score, 3),
                'stability_label': stability.get('stability_label', 'unknown'),
                'sentiment': stability.get('sentiment', {}).get('sentiment', 'neutral')
            }
        
        # Usar sentimiento general
        sentiment = news_sentiment.get('sentiment', 'neutral')
        confidence = news_sentiment.get('confidence', 0.5)
        
        if sentiment == 'positive':
            score = 0.5 + (confidence * 0.5)
        elif sentiment == 'negative':
            score = 0.5 - (confidence * 0.5)
        else:
            score = 0.5
        
        return {
            'score': round(score, 3),
            'sentiment': sentiment,
            'confidence': confidence
        }
    
    def _classify_health_status(self, overall_score: float) -> str:
        """Clasifica el estado de salud financiera basándose en el score"""
        if overall_score >= 80:
            return 'excellent'
        elif overall_score >= 65:
            return 'good'
        elif overall_score >= 50:
            return 'moderate'
        elif overall_score >= 35:
            return 'concerning'
        else:
            return 'poor'
    
    def _estimate_burn_rate(self, company: CompanyData) -> float:
        """Estima el burn rate mensual (en millones USD)"""
        if company.team_size == 0:
            return 0.0
        
        # Estimación simple: ~$10K USD por empleado por mes (incluye salarios, overhead, etc.)
        # Esto es un promedio muy aproximado para startups tech
        burn_per_employee = 0.010  # 10K en millones
        
        return company.team_size * burn_per_employee
    
    def _calculate_runway(self, company: CompanyData, burn_rate: float) -> Optional[float]:
        """Calcula el runway estimado en meses"""
        if not company.funding_rounds or burn_rate == 0:
            return None
        
        # Asumir que tienen el 60% de la última ronda disponible (estimación conservadora)
        last_round = company.funding_rounds[-1]
        months_since = (datetime.now() - last_round.date).days / 30.44
        
        # Cash disponible estimado
        available_cash = last_round.amount * 0.6 - (burn_rate * months_since)
        
        if available_cash <= 0:
            return 0.0
        
        runway = available_cash / burn_rate
        return round(runway, 1)
    
    def _generate_insights(self, company: CompanyData, components: Dict, overall_score: float) -> List[str]:
        """Genera insights accionables basados en el análisis"""
        insights = []
        
        # Insight sobre funding recency
        recency = components['funding_recency']
        if recency['months_since_last_round'] > 24:
            insights.append(f"⚠️ Última ronda hace {recency['months_since_last_round']:.1f} meses. Considerar nueva ronda pronto.")
        elif recency['months_since_last_round'] < 6:
            insights.append(f"✓ Financiamiento muy reciente ({recency['months_since_last_round']:.1f} meses).")
        
        # Insight sobre eficiencia del equipo
        efficiency = components['team_efficiency']
        if efficiency['status'] == 'underfunded':
            insights.append(f"⚠️ Capital limitado por empleado (${efficiency['funding_per_employee_millions']:.2f}M). Puede limitar crecimiento.")
        elif efficiency['status'] == 'overfunded':
            insights.append(f"⚠️ Alto capital por empleado (${efficiency['funding_per_employee_millions']:.2f}M). Revisar eficiencia operativa.")
        
        # Insight sobre trayectoria
        growth = components['growth_trajectory']
        if growth['status'] == 'strong_growth':
            insights.append("✓ Trayectoria de crecimiento fuerte entre rondas.")
        elif growth['status'] == 'declining':
            insights.append("⚠️ Montos de rondas decrecientes. Señal de alerta.")
        
        # Insight sobre runway
        if 'estimated_runway_months' in components:
            runway = components['estimated_runway_months']
            if runway and runway < 12:
                insights.append(f"🚨 Runway estimado de solo {runway:.1f} meses. Urgente recaudar.")
            elif runway and runway < 18:
                insights.append(f"⚠️ Runway estimado de {runway:.1f} meses. Comenzar proceso de fundraising.")
        
        # Insight sobre score general
        if overall_score >= 70:
            insights.append("✓ Salud financiera sólida en general.")
        elif overall_score < 50:
            insights.append("⚠️ Salud financiera preocupante. Requiere atención.")
        
        return insights


class CompanyPortfolioAnalyzer:
    """Analiza un portafolio de empresas y genera rankings"""
    
    def __init__(self):
        self.calculator = FinancialHealthCalculator()
    
    def analyze_portfolio(
        self,
        companies: List[CompanyData],
        news_data: Optional[Dict[str, Dict]] = None
    ) -> Dict:
        """
        Analiza un portafolio completo de empresas
        
        Args:
            companies: Lista de empresas a analizar
            news_data: Diccionario {company_name: news_sentiment_data}
            
        Returns:
            Análisis completo del portafolio
        """
        if not news_data:
            news_data = {}
        
        results = []
        
        for company in companies:
            news_sentiment = news_data.get(company.name)
            health_score = self.calculator.calculate_health_score(company, news_sentiment)
            
            results.append({
                'company_name': company.name,
                'health_score': health_score
            })
        
        # Ordenar por score
        results.sort(key=lambda x: x['health_score']['overall_score'], reverse=True)
        
        # Calcular estadísticas del portafolio
        scores = [r['health_score']['overall_score'] for r in results]
        
        portfolio_stats = {
            'total_companies': len(companies),
            'avg_health_score': round(sum(scores) / len(scores), 2) if scores else 0,
            'median_health_score': round(sorted(scores)[len(scores) // 2], 2) if scores else 0,
            'top_performers': results[:5],
            'concerning_companies': [r for r in results if r['health_score']['overall_score'] < 50],
            'health_distribution': {
                'excellent': len([s for s in scores if s >= 80]),
                'good': len([s for s in scores if 65 <= s < 80]),
                'moderate': len([s for s in scores if 50 <= s < 65]),
                'concerning': len([s for s in scores if 35 <= s < 50]),
                'poor': len([s for s in scores if s < 35])
            }
        }
        
        return {
            'portfolio_stats': portfolio_stats,
            'company_results': results,
            'analyzed_at': datetime.now().isoformat()
        }


if __name__ == "__main__":
    # Test del analizador
    calculator = FinancialHealthCalculator()
    
    # Empresa de prueba
    test_company = CompanyData(
        name="TechStartup",
        team_size=50,
        funding_rounds=[
            FundingRound("seed", 2.5, datetime(2023, 1, 15), ["Angel Investors"]),
            FundingRound("series-a", 12.0, datetime(2024, 6, 1), ["Sequoia Capital"], 60.0)
        ],
        founded_date=datetime(2022, 6, 1),
        industry="AI/ML"
    )
    
    score = calculator.calculate_health_score(test_company)
    
    print("\n=== Financial Health Score ===")
    print(f"Empresa: {test_company.name}")
    print(f"Score General: {score['overall_score']}/100")
    print(f"Estado: {score['health_status'].upper()}")
    print(f"\nMétricas:")
    print(f"  - Funding Total: ${score['metrics']['total_funding']}M")
    print(f"  - Tamaño de Equipo: {score['metrics']['team_size']}")
    print(f"  - Burn Rate Estimado: ${score['metrics']['estimated_burn_rate']}M/mes")
    print(f"  - Runway Estimado: {score['metrics']['estimated_runway_months']} meses")
    print(f"\nInsights:")
    for insight in score['insights']:
        print(f"  {insight}")
