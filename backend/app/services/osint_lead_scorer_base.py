# Extracted from src/osint_lead_scorer.py for FastAPI service use
import os
import json
import re
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from pathlib import Path
from collections import defaultdict

try:
    from GoogleNews import GoogleNews
except ImportError:
    GoogleNews = None
    logging.warning("GoogleNews not available. Install with: pip install GoogleNews")

try:
    from textblob import TextBlob
except ImportError:
    TextBlob = None
    logging.warning("TextBlob not available. Install with: pip install textblob")

try:
    import nltk
    from nltk.sentiment import SentimentIntensityAnalyzer
except ImportError:
    nltk = None
    SentimentIntensityAnalyzer = None
    logging.warning("NLTK not available. Install with: pip install nltk")

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class OSINTLeadScorer:
    # Full implementation copied from src/osint_lead_scorer.py (excluding __main__ block)
    POSITIVE_KEYWORDS = {
        'series_a': {'keywords': ['series a', 'series-a', 'series a funding'], 'score': 50},
        'series_b': {'keywords': ['series b', 'series-b', 'series b funding'], 'score': 60},
        'series_c': {'keywords': ['series c', 'series-c', 'series c funding'], 'score': 70},
        'expansion': {'keywords': ['expansion', 'expanding', 'expand operations', 'new office', 'opening office'], 'score': 50},
        'hiring': {'keywords': ['hiring', 'recruiting', 'talent acquisition', 'join our team', 'we are hiring'], 'score': 40},
        'growth': {'keywords': ['rapid growth', 'fast growing', 'scaling up', 'scale operations'], 'score': 30},
        'funding': {'keywords': ['raised funding', 'secured funding', 'closes funding', 'funding round'], 'score': 45},
        'acquisition': {'keywords': ['acquired', 'acquisition', 'acquires'], 'score': 35},
        'ipo': {'keywords': ['ipo', 'initial public offering', 'going public'], 'score': 80},
        'product_launch': {'keywords': ['launches new product', 'product launch', 'new product'], 'score': 25},
        'partnership': {'keywords': ['partnership', 'partners with', 'strategic partnership'], 'score': 20},
        'revenue_growth': {'keywords': ['revenue growth', 'revenue up', 'sales growth'], 'score': 30},
    }
    NEGATIVE_KEYWORDS = {
        'layoffs': {'keywords': ['layoffs', 'lay off', 'layoff', 'job cuts', 'cutting jobs'], 'score': -100},
        'bankruptcy': {'keywords': ['bankruptcy', 'bankrupt', 'chapter 11', 'insolvent'], 'score': -150},
        'shutdown': {'keywords': ['shutting down', 'shutdown', 'closing down', 'cease operations'], 'score': -120},
        'downsizing': {'keywords': ['downsizing', 'downsize', 'reducing workforce'], 'score': -80},
        'financial_trouble': {'keywords': ['financial trouble', 'cash flow problems', 'financial difficulties'], 'score': -70},
        'lawsuit': {'keywords': ['lawsuit', 'legal action', 'sued'], 'score': -40},
        'scandal': {'keywords': ['scandal', 'controversy', 'investigation'], 'score': -50},
    }
    OUTSOURCING_SIGNALS = {
        'remote': ['remote-friendly', 'remote work', 'remote first', 'work from anywhere'],
        'global': ['global team', 'international team', 'worldwide team', 'distributed team'],
        'timezone': ['latam timezone', 'emea timezone', 'asia timezone', 'multiple timezones'],
        'offshore': ['offshore', 'nearshore', 'offshore development', 'global talent'],
    }
    def __init__(self, use_nltk: bool = True):
        self.use_nltk = use_nltk and nltk is not None
        if self.use_nltk:
            try:
                nltk.download('vader_lexicon', quiet=True)
                self.sentiment_analyzer = SentimentIntensityAnalyzer()
                logger.info("Using NLTK VADER for sentiment analysis")
            except Exception as e:
                logger.warning(f"Failed to initialize NLTK: {e}. Falling back to TextBlob")
                self.use_nltk = False
                self.sentiment_analyzer = None
        if not self.use_nltk and TextBlob is None:
            logger.error("Neither NLTK nor TextBlob is available. Sentiment analysis will be limited.")
    def scrape_tech_news(self, query: str = "tech startup funding OR hiring", region: str = "US", period: str = "7d", max_results: int = 50) -> List[Dict]:
        articles = []
        if GoogleNews is None:
            logger.error("GoogleNews library not installed. Install with: pip install GoogleNews")
            return articles
        try:
            googlenews = GoogleNews(lang='en', region=region)
            googlenews.set_time_range(period, period)
            googlenews.set_encode('utf-8')
            logger.info(f"Scraping news for query: '{query}' in region: {region}")
            googlenews.search(query)
            results = googlenews.results(sort=True)
            for idx, article in enumerate(results[:max_results]):
                articles.append({
                    'title': article.get('title', ''),
                    'description': article.get('desc', ''),
                    'date': article.get('date', ''),
                    'link': article.get('link', ''),
                    'source': article.get('site', ''),
                    'scraped_at': datetime.now().isoformat()
                })
            logger.info(f"Scraped {len(articles)} articles")
        except Exception as e:
            logger.error(f"Error scraping news: {e}")
        return articles
    def analyze_sentiment(self, text: str) -> Dict:
        if self.use_nltk and self.sentiment_analyzer:
            scores = self.sentiment_analyzer.polarity_scores(text)
            return {
                'polarity': scores['compound'],
                'positive': scores['pos'],
                'negative': scores['neg'],
                'neutral': scores['neu'],
                'method': 'nltk_vader'
            }
        elif TextBlob:
            blob = TextBlob(text)
            return {
                'polarity': blob.sentiment.polarity,
                'subjectivity': blob.sentiment.subjectivity,
                'method': 'textblob'
            }
        else:
            return {
                'polarity': 0.0,
                'method': 'none'
            }
    def extract_company_name(self, text: str) -> Optional[str]:
        patterns = [
            r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+(?:raises|secures|announces|launches|hires)',
            r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+(?:raises|gets|closes)\s+\$',
            r'^([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*):',
            r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+\(?(?:Inc|Corp|Ltd|LLC|Co)\)?',
        ]
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(1).strip()
        words = text.split()
        company_words = []
        for word in words[:10]:
            if word[0].isupper() and len(word) > 2:
                company_words.append(word)
                if len(company_words) == 3:
                    break
            elif company_words:
                break
        if company_words:
            return ' '.join(company_words)
        return None
    def calculate_heuristic_score(self, text: str) -> Tuple[int, List[str], Dict]:
        text_lower = text.lower()
        total_score = 0
        matched_signals = []
        signal_details = defaultdict(list)
        for signal_name, signal_data in self.POSITIVE_KEYWORDS.items():
            for keyword in signal_data['keywords']:
                if keyword in text_lower:
                    total_score += signal_data['score']
                    matched_signals.append(f"+{signal_name}")
                    signal_details['positive'].append({
                        'signal': signal_name,
                        'keyword': keyword,
                        'score': signal_data['score']
                    })
                    break
        for signal_name, signal_data in self.NEGATIVE_KEYWORDS.items():
            for keyword in signal_data['keywords']:
                if keyword in text_lower:
                    total_score += signal_data['score']
                    matched_signals.append(f"-{signal_name}")
                    signal_details['negative'].append({
                        'signal': signal_name,
                        'keyword': keyword,
                        'score': signal_data['score']
                    })
                    break
        outsourcing_score = 0
        for intent_type, keywords in self.OUTSOURCING_SIGNALS.items():
            for keyword in keywords:
                if keyword in text_lower:
                    outsourcing_score += 15
                    signal_details['outsourcing'].append({
                        'intent': intent_type,
                        'keyword': keyword,
                        'score': 15
                    })
                    break
        total_score += outsourcing_score
        return total_score, matched_signals, dict(signal_details)
    def predict_hiring_window(self, score: int, signals: List[str], article_date: str) -> str:
        urgent_signals = ['series_a', 'series_b', 'series_c', 'expansion', 'hiring']
        has_urgent = any(signal.lstrip('+-') in urgent_signals for signal in signals)
        if score >= 100 and has_urgent:
            return "Next 1-2 months (High Priority)"
        elif score >= 70 and has_urgent:
            return "Next 2-3 months (High Potential)"
        elif score >= 50:
            return "Next 3-6 months (Medium Potential)"
        elif score >= 20:
            return "Next 6-12 months (Low-Medium Potential)"
        elif score > 0:
            return "Next 12+ months (Monitor)"
        elif score == 0:
            return "Insufficient data"
        else:
            return "Not recommended (Negative signals)"
    def score_article(self, article: Dict) -> Dict:
        text = f"{article.get('title', '')} {article.get('description', '')}"
        company_name = self.extract_company_name(article.get('title', ''))
        heuristic_score, signals, signal_details = self.calculate_heuristic_score(text)
        sentiment = self.analyze_sentiment(text)
        sentiment_boost = int(sentiment.get('polarity', 0) * 20)
        total_score = heuristic_score + sentiment_boost
        hiring_window = self.predict_hiring_window(
            total_score,
            signals,
            article.get('date', '')
        )
        return {
            'company_name': company_name or 'Unknown Company',
            'article_title': article.get('title', ''),
            'source_url': article.get('link', ''),
            'source_site': article.get('source', ''),
            'article_date': article.get('date', ''),
            'growth_score': total_score,
            'heuristic_score': heuristic_score,
            'sentiment_score': sentiment_boost,
            'sentiment_polarity': sentiment.get('polarity', 0),
            'matched_signals': signals,
            'signal_details': signal_details,
            'predicted_hiring_window': hiring_window,
            'outsourcing_potential': len(signal_details.get('outsourcing', [])) > 0,
            'analyzed_at': datetime.now().isoformat()
        }
    def score_news_batch(self, query: str = "tech startup funding OR expansion OR hiring", regions: List[str] = ["US"], period: str = "7d", max_results_per_region: int = 50, min_score: int = 20) -> List[Dict]:
        all_scored_leads = []
        for region in regions:
            logger.info(f"Processing region: {region}")
            articles = self.scrape_tech_news(
                query=query,
                region=region,
                period=period,
                max_results=max_results_per_region
            )
            for article in articles:
                try:
                    scored_lead = self.score_article(article)
                    if scored_lead['growth_score'] >= min_score:
                        all_scored_leads.append(scored_lead)
                except Exception as e:
                    logger.error(f"Error scoring article: {e}")
        all_scored_leads.sort(key=lambda x: x['growth_score'], reverse=True)
        seen_companies = set()
        unique_leads = []
        for lead in all_scored_leads:
            company = lead['company_name'].lower()
            if company not in seen_companies and company != 'unknown company':
                seen_companies.add(company)
                unique_leads.append(lead)
        logger.info(
            f"Scored {len(all_scored_leads)} articles, "
            f"found {len(unique_leads)} unique qualified leads"
        )
        return unique_leads
