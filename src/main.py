"""
PulseB2B - Pipeline Principal de Inteligencia de Mercados
Monitorea noticias, clasifica eventos y calcula Financial Health Scores
"""

import logging
import json
import argparse
from datetime import datetime
from pathlib import Path
from typing import Dict, List
import yaml

from news_scraper import NewsMonitor
from news_classifier import NewsClassifier
from financial_analyzer import (
    FinancialHealthCalculator,
    CompanyData,
    FundingRound,
    CompanyPortfolioAnalyzer
)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class PulseB2BPipeline:
    """Pipeline principal que integra todos los componentes"""
    
    def __init__(self, config_path: str = None):
        """
        Inicializa el pipeline
        
        Args:
            config_path: Ruta al archivo de configuración YAML
        """
        self.config = self._load_config(config_path)
        
        # Crear directorios necesarios
        self.data_dir = Path(self.config['paths']['data_dir'])
        self.data_dir.mkdir(exist_ok=True)
        
        # Inicializar componentes
        logger.info("Inicializando componentes del pipeline...")
        self.news_monitor = NewsMonitor()
        self.classifier = NewsClassifier(
            load_sentiment_model=self.config['analysis']['use_sentiment_analysis']
        )
        self.financial_calculator = FinancialHealthCalculator()
        
        logger.info("Pipeline inicializado correctamente")
    
    def _load_config(self, config_path: str = None) -> Dict:
        """Carga la configuración desde archivo YAML o usa valores por defecto"""
        default_config = {
            'monitoring': {
                'search_queries': [
                    'startup funding',
                    'Series A',
                    'Series B',
                    'venture capital',
                    'layoffs tech',
                    'company expansion',
                    'tech acquisitions'
                ],
                'days_lookback': 7,
                'extract_full_content': True
            },
            'analysis': {
                'use_sentiment_analysis': True,
                'extract_companies': True,
                'min_relevance_score': 1.0
            },
            'paths': {
                'data_dir': './data',
                'output_dir': './data/output'
            }
        }
        
        if config_path and Path(config_path).exists():
            logger.info(f"Cargando configuración desde {config_path}")
            with open(config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
                # Merge con valores por defecto
                return {**default_config, **config}
        else:
            logger.info("Usando configuración por defecto")
            return default_config
    
    def run_news_monitoring(self) -> List[Dict]:
        """
        Ejecuta el monitoreo de noticias
        
        Returns:
            Lista de artículos obtenidos
        """
        logger.info("=== INICIANDO MONITOREO DE NOTICIAS ===")
        
        queries = self.config['monitoring']['search_queries']
        days = self.config['monitoring']['days_lookback']
        extract_content = self.config['monitoring']['extract_full_content']
        
        articles = self.news_monitor.fetch_all_news(
            queries=queries,
            days=days,
            extract_content=extract_content
        )
        
        # Guardar artículos raw
        raw_path = self.data_dir / f"raw_articles_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(raw_path, 'w', encoding='utf-8') as f:
            json.dump(articles, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Artículos guardados en {raw_path}")
        logger.info(f"Total de artículos obtenidos: {len(articles)}")
        
        return articles
    
    def run_classification(self, articles: List[Dict]) -> List[Dict]:
        """
        Ejecuta la clasificación de artículos
        
        Args:
            articles: Lista de artículos a clasificar
            
        Returns:
            Lista de artículos clasificados
        """
        logger.info("=== INICIANDO CLASIFICACIÓN DE NOTICIAS ===")
        
        classified = self.classifier.classify_batch(articles)
        
        # Filtrar por relevancia mínima
        min_score = self.config['analysis']['min_relevance_score']
        relevant = [a for a in classified if a['primary_score'] >= min_score]
        
        logger.info(f"Artículos relevantes (score >= {min_score}): {len(relevant)}/{len(classified)}")
        
        # Guardar resultados clasificados
        classified_path = self.data_dir / f"classified_articles_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(classified_path, 'w', encoding='utf-8') as f:
            json.dump(relevant, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Artículos clasificados guardados en {classified_path}")
        
        # Estadísticas por categoría
        category_stats = {}
        for article in relevant:
            cat = article['primary_category']
            category_stats[cat] = category_stats.get(cat, 0) + 1
        
        logger.info("Distribución por categoría:")
        for cat, count in sorted(category_stats.items(), key=lambda x: x[1], reverse=True):
            logger.info(f"  - {cat}: {count}")
        
        return relevant
    
    def extract_company_insights(self, classified_articles: List[Dict]) -> Dict[str, Dict]:
        """
        Extrae insights por empresa de los artículos clasificados
        
        Args:
            classified_articles: Artículos clasificados
            
        Returns:
            Diccionario {company_name: insights}
        """
        logger.info("=== EXTRAYENDO INSIGHTS POR EMPRESA ===")
        
        company_insights = {}
        
        for article in classified_articles:
            companies = article.get('companies_mentioned', [])
            
            for company_name in companies:
                if company_name not in company_insights:
                    company_insights[company_name] = {
                        'name': company_name,
                        'articles': [],
                        'categories': {},
                        'sentiment_scores': []
                    }
                
                # Agregar artículo
                company_insights[company_name]['articles'].append({
                    'title': article['title'],
                    'url': article['url'],
                    'published': article['published'],
                    'category': article['primary_category'],
                    'score': article['primary_score']
                })
                
                # Contar categorías
                cat = article['primary_category']
                company_insights[company_name]['categories'][cat] = \
                    company_insights[company_name]['categories'].get(cat, 0) + 1
                
                # Agregar sentimiento si está disponible
                if article.get('sentiment'):
                    company_insights[company_name]['sentiment_scores'].append(
                        article['sentiment']
                    )
        
        # Calcular sentimiento promedio por empresa
        for company_name, data in company_insights.items():
            if data['sentiment_scores']:
                avg_positive = sum(s['scores']['positive'] for s in data['sentiment_scores']) / len(data['sentiment_scores'])
                avg_negative = sum(s['scores']['negative'] for s in data['sentiment_scores']) / len(data['sentiment_scores'])
                
                data['avg_sentiment'] = {
                    'positive': round(avg_positive, 3),
                    'negative': round(avg_negative, 3),
                    'overall': 'positive' if avg_positive > avg_negative else 'negative'
                }
        
        logger.info(f"Insights extraídos para {len(company_insights)} empresas")
        
        # Guardar insights
        insights_path = self.data_dir / f"company_insights_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(insights_path, 'w', encoding='utf-8') as f:
            json.dump(company_insights, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Insights guardados en {insights_path}")
        
        return company_insights
    
    def calculate_financial_health(
        self,
        company_data: List[CompanyData],
        news_insights: Dict[str, Dict] = None
    ) -> Dict:
        """
        Calcula Financial Health Scores para empresas
        
        Args:
            company_data: Lista de datos de empresas
            news_insights: Insights extraídos de noticias
            
        Returns:
            Resultados del análisis financiero
        """
        logger.info("=== CALCULANDO FINANCIAL HEALTH SCORES ===")
        
        if not news_insights:
            news_insights = {}
        
        results = []
        
        for company in company_data:
            logger.info(f"Analizando {company.name}...")
            
            # Obtener sentimiento de noticias
            news_sentiment = None
            if company.name in news_insights and news_insights[company.name].get('avg_sentiment'):
                news_sentiment = {
                    'sentiment': news_insights[company.name]['avg_sentiment']['overall'],
                    'confidence': abs(
                        news_insights[company.name]['avg_sentiment']['positive'] -
                        news_insights[company.name]['avg_sentiment']['negative']
                    )
                }
            
            # Calcular score
            health_score = self.financial_calculator.calculate_health_score(
                company,
                news_sentiment
            )
            
            results.append({
                'company': company.name,
                'health_score': health_score
            })
        
        # Guardar resultados
        scores_path = self.data_dir / f"financial_scores_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(scores_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False, default=str)
        
        logger.info(f"Scores financieros guardados en {scores_path}")
        
        return results
    
    def generate_report(
        self,
        articles: List[Dict],
        classified: List[Dict],
        company_insights: Dict[str, Dict],
        financial_scores: List[Dict] = None
    ) -> str:
        """
        Genera un reporte consolidado en formato Markdown
        
        Returns:
            Ruta al archivo de reporte generado
        """
        logger.info("=== GENERANDO REPORTE ===")
        
        report_lines = [
            "# PulseB2B - Reporte de Inteligencia de Mercados",
            f"\n**Fecha:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"\n## Resumen Ejecutivo\n",
            f"- **Artículos Monitoreados:** {len(articles)}",
            f"- **Artículos Relevantes:** {len(classified)}",
            f"- **Empresas Detectadas:** {len(company_insights)}",
            "\n---\n"
        ]
        
        # Distribución por categoría
        report_lines.append("## Distribución por Categoría\n")
        category_stats = {}
        for article in classified:
            cat = article['primary_category']
            category_stats[cat] = category_stats.get(cat, 0) + 1
        
        for cat, count in sorted(category_stats.items(), key=lambda x: x[1], reverse=True):
            report_lines.append(f"- **{cat}:** {count} artículos")
        
        # Top empresas por menciones
        report_lines.append("\n## Top Empresas por Menciones\n")
        top_companies = sorted(
            company_insights.items(),
            key=lambda x: len(x[1]['articles']),
            reverse=True
        )[:10]
        
        for i, (company, data) in enumerate(top_companies, 1):
            sentiment = data.get('avg_sentiment', {}).get('overall', 'unknown')
            report_lines.append(
                f"{i}. **{company}** - {len(data['articles'])} artículos "
                f"(Sentimiento: {sentiment})"
            )
        
        # Financial Health Scores (si están disponibles)
        if financial_scores:
            report_lines.append("\n## Financial Health Scores\n")
            sorted_scores = sorted(
                financial_scores,
                key=lambda x: x['health_score']['overall_score'],
                reverse=True
            )
            
            for result in sorted_scores[:10]:
                company = result['company']
                score = result['health_score']
                report_lines.append(
                    f"- **{company}:** {score['overall_score']:.1f}/100 "
                    f"({score['health_status']})"
                )
        
        # Artículos destacados
        report_lines.append("\n## Artículos Destacados\n")
        top_articles = sorted(
            classified,
            key=lambda x: x['primary_score'],
            reverse=True
        )[:15]
        
        for article in top_articles:
            report_lines.append(
                f"\n### [{article['title']}]({article['url']})\n"
                f"- **Fuente:** {article['source']}\n"
                f"- **Categoría:** {article['primary_category']} (Score: {article['primary_score']})\n"
                f"- **Publicado:** {article['published']}\n"
            )
            if article.get('companies_mentioned'):
                report_lines.append(f"- **Empresas:** {', '.join(article['companies_mentioned'])}\n")
        
        # Guardar reporte
        report_content = '\n'.join(report_lines)
        report_path = self.data_dir / f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        logger.info(f"Reporte generado en {report_path}")
        
        return str(report_path)
    
    def run_full_pipeline(self, company_data: List[CompanyData] = None):
        """
        Ejecuta el pipeline completo
        
        Args:
            company_data: Lista opcional de empresas para análisis financiero
        """
        logger.info("\n" + "="*60)
        logger.info("INICIANDO PIPELINE PULSEB2B")
        logger.info("="*60 + "\n")
        
        try:
            # 1. Monitoreo de noticias
            articles = self.run_news_monitoring()
            
            if not articles:
                logger.warning("No se obtuvieron artículos. Finalizando pipeline.")
                return
            
            # 2. Clasificación
            classified = self.run_classification(articles)
            
            if not classified:
                logger.warning("No se encontraron artículos relevantes.")
                return
            
            # 3. Extracción de insights por empresa
            company_insights = self.extract_company_insights(classified)
            
            # 4. Análisis financiero (si se proporcionan datos de empresas)
            financial_scores = None
            if company_data:
                financial_scores = self.calculate_financial_health(
                    company_data,
                    company_insights
                )
            
            # 5. Generar reporte
            report_path = self.generate_report(
                articles,
                classified,
                company_insights,
                financial_scores
            )
            
            logger.info("\n" + "="*60)
            logger.info("PIPELINE COMPLETADO EXITOSAMENTE")
            logger.info(f"Reporte disponible en: {report_path}")
            logger.info("="*60 + "\n")
            
        except Exception as e:
            logger.error(f"Error en el pipeline: {e}", exc_info=True)
            raise


def main():
    """Función principal"""
    parser = argparse.ArgumentParser(
        description='PulseB2B - Pipeline de Inteligencia de Mercados'
    )
    parser.add_argument(
        '--config',
        type=str,
        help='Ruta al archivo de configuración YAML',
        default='config/config.yaml'
    )
    parser.add_argument(
        '--days',
        type=int,
        help='Días hacia atrás para buscar noticias',
        default=None
    )
    parser.add_argument(
        '--no-sentiment',
        action='store_true',
        help='Desactivar análisis de sentimiento'
    )
    
    args = parser.parse_args()
    
    # Crear pipeline
    pipeline = PulseB2BPipeline(config_path=args.config)
    
    # Override config con argumentos CLI
    if args.days:
        pipeline.config['monitoring']['days_lookback'] = args.days
    if args.no_sentiment:
        pipeline.config['analysis']['use_sentiment_analysis'] = False
    
    # Datos de ejemplo de empresas (normalmente vendrían de una base de datos)
    example_companies = [
        CompanyData(
            name="Anthropic",
            team_size=150,
            funding_rounds=[
                FundingRound("seed", 124.0, datetime(2021, 5, 28), ["Various"]),
                FundingRound("series-a", 580.0, datetime(2022, 5, 12), ["Various"]),
                FundingRound("series-b", 450.0, datetime(2023, 5, 23), ["Spark Capital", "Google"]),
            ],
            industry="AI"
        ),
        # Agregar más empresas según sea necesario
    ]
    
    # Ejecutar pipeline
    pipeline.run_full_pipeline(company_data=example_companies)


if __name__ == "__main__":
    main()
