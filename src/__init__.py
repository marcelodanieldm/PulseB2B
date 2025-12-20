"""
PulseB2B - Market Intelligence Pipeline
Monitoreo de noticias, clasificación y análisis financiero de empresas
"""

__version__ = "1.0.0"
__author__ = "PulseB2B Team"

from .news_scraper import NewsMonitor, GoogleNewsSource, RSSFeedSource, ArticleExtractor
from .news_classifier import NewsClassifier, KeywordClassifier, SentimentAnalyzer
from .financial_analyzer import (
    FinancialHealthCalculator,
    CompanyData,
    FundingRound,
    CompanyPortfolioAnalyzer
)

__all__ = [
    'NewsMonitor',
    'GoogleNewsSource',
    'RSSFeedSource',
    'ArticleExtractor',
    'NewsClassifier',
    'KeywordClassifier',
    'SentimentAnalyzer',
    'FinancialHealthCalculator',
    'CompanyData',
    'FundingRound',
    'CompanyPortfolioAnalyzer'
]
