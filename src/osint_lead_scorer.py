"""
OSINT Lead Scoring Model - Free Tech Market Intelligence
---------------------------------------------------------
This module uses Open Source Intelligence (OSINT) to score companies based on
news analysis, detecting growth signals and hiring opportunities without any
paid API dependencies.

Uses:
- pygooglenews: Free news scraping
- TextBlob/NLTK: Free sentiment analysis
- Heuristic scoring: Rule-based lead qualification
"""

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

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class OSINTLeadScorer:
    """
    Open Source Intelligence Lead Scoring System.
    
    Analyzes tech news to identify companies with:
    - High growth signals (funding, expansion)
    - Hiring potential (team building, office expansion)
    - Risk signals (layoffs, financial trouble)
    """
    
    # Heuristic scoring rules
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
    
    # Outsourcing intent keywords (from original requirements)
    OUTSOURCING_SIGNALS = {
        'remote': ['remote-friendly', 'remote work', 'remote first', 'work from anywhere'],
        'global': ['global team', 'international team', 'worldwide team', 'distributed team'],
        'timezone': ['latam timezone', 'emea timezone', 'asia timezone', 'multiple timezones'],
        'offshore': ['offshore', 'nearshore', 'offshore development', 'global talent'],
    }
    
    def __init__(self, use_nltk: bool = True):
        """
        Initialize the OSINT Lead Scorer.
        
        Args:
            use_nltk: If True, use NLTK VADER for sentiment. Otherwise use TextBlob.
        """
        self.use_nltk = use_nltk and nltk is not None
        
        if self.use_nltk:
            try:
                # Download VADER lexicon if not already present
                nltk.download('vader_lexicon', quiet=True)
                self.sentiment_analyzer = SentimentIntensityAnalyzer()
                logger.info("Using NLTK VADER for sentiment analysis")
            except Exception as e:
                logger.warning(f"Failed to initialize NLTK: {e}. Falling back to TextBlob")
                self.use_nltk = False
                self.sentiment_analyzer = None
        
        if not self.use_nltk and TextBlob is None:
            logger.error("Neither NLTK nor TextBlob is available. Sentiment analysis will be limited.")
    
    def scrape_tech_news(
        self,
        query: str = "tech startup funding OR hiring",
        region: str = "US",
        period: str = "7d",
        max_results: int = 50
    ) -> List[Dict]:
        """
        Scrape tech news using GoogleNews.
        
        Args:
            query: Search query for news
            region: Region code (US, EU, UK, etc.)
            period: Time period (7d = 7 days, 1m = 1 month)
            max_results: Maximum number of results to return
        
        Returns:
            List of news articles with metadata
        """
        articles = []
        
        if GoogleNews is None:
            logger.error("GoogleNews library not installed. Install with: pip install GoogleNews")
            return articles
        
        try:
            # Initialize GoogleNews
            googlenews = GoogleNews(lang='en', region=region)
            googlenews.set_time_range(period, period)
            googlenews.set_encode('utf-8')
            
            logger.info(f"Scraping news for query: '{query}' in region: {region}")
            
            # Search for news
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
        """
        Analyze sentiment of text using NLTK VADER or TextBlob.
        
        Args:
            text: Text to analyze
        
        Returns:
            Dictionary with sentiment scores
        """
        if self.use_nltk and self.sentiment_analyzer:
            # Use NLTK VADER
            scores = self.sentiment_analyzer.polarity_scores(text)
            return {
                'polarity': scores['compound'],
                'positive': scores['pos'],
                'negative': scores['neg'],
                'neutral': scores['neu'],
                'method': 'nltk_vader'
            }
        elif TextBlob:
            # Use TextBlob
            blob = TextBlob(text)
            return {
                'polarity': blob.sentiment.polarity,
                'subjectivity': blob.sentiment.subjectivity,
                'method': 'textblob'
            }
        else:
            # No sentiment analysis available
            return {
                'polarity': 0.0,
                'method': 'none'
            }
    
    def extract_company_name(self, text: str) -> Optional[str]:
        """
        Extract company name from article title/description.
        
        This is a simple heuristic. For better results, use NER (Named Entity Recognition).
        
        Args:
            text: Article text
        
        Returns:
            Extracted company name or None
        """
        # Simple patterns to detect company names
        # Look for capitalized words before common keywords
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
        
        # Fallback: return first capitalized phrase (up to 3 words)
        words = text.split()
        company_words = []
        for word in words[:10]:  # Only check first 10 words
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
        """
        Calculate heuristic score based on keyword matching.
        
        Args:
            text: Article text (title + description)
        
        Returns:
            Tuple of (total_score, matched_signals, signal_details)
        """
        text_lower = text.lower()
        total_score = 0
        matched_signals = []
        signal_details = defaultdict(list)
        
        # Check positive keywords
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
                    break  # Only count each signal once
        
        # Check negative keywords
        for signal_name, signal_data in self.NEGATIVE_KEYWORDS.items():
            for keyword in signal_data['keywords']:
                if keyword in text_lower:
                    total_score += signal_data['score']  # Note: score is negative
                    matched_signals.append(f"-{signal_name}")
                    signal_details['negative'].append({
                        'signal': signal_name,
                        'keyword': keyword,
                        'score': signal_data['score']
                    })
                    break
        
        # Check outsourcing signals
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
        """
        Predict hiring window based on score and signals.
        
        Args:
            score: Total heuristic score
            signals: List of matched signals
            article_date: Date of the article
        
        Returns:
            Predicted hiring window as string
        """
        # High urgency signals
        urgent_signals = ['series_a', 'series_b', 'series_c', 'expansion', 'hiring']
        has_urgent = any(signal.lstrip('+-') in urgent_signals for signal in signals)
        
        # Funding rounds typically trigger hiring within 1-3 months
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
        """
        Score a single article for lead potential.
        
        Args:
            article: Article dictionary with title, description, etc.
        
        Returns:
            Scored lead dictionary
        """
        # Combine title and description for analysis
        text = f"{article.get('title', '')} {article.get('description', '')}"
        
        # Extract company name
        company_name = self.extract_company_name(article.get('title', ''))
        
        # Calculate heuristic score
        heuristic_score, signals, signal_details = self.calculate_heuristic_score(text)
        
        # Analyze sentiment
        sentiment = self.analyze_sentiment(text)
        
        # Adjust score based on sentiment
        sentiment_boost = int(sentiment.get('polarity', 0) * 20)
        total_score = heuristic_score + sentiment_boost
        
        # Predict hiring window
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
    
    def score_news_batch(
        self,
        query: str = "tech startup funding OR expansion OR hiring",
        regions: List[str] = ["US"],
        period: str = "7d",
        max_results_per_region: int = 50,
        min_score: int = 20
    ) -> List[Dict]:
        """
        Scrape and score a batch of news articles.
        
        Args:
            query: Search query
            regions: List of region codes to scrape
            period: Time period for news
            max_results_per_region: Max results per region
            min_score: Minimum score to include in results
        
        Returns:
            List of scored leads, sorted by score
        """
        all_scored_leads = []
        
        for region in regions:
            logger.info(f"Processing region: {region}")
            
            # Scrape news
            articles = self.scrape_tech_news(
                query=query,
                region=region,
                period=period,
                max_results=max_results_per_region
            )
            
            # Score each article
            for article in articles:
                try:
                    scored_lead = self.score_article(article)
                    
                    # Only include leads above minimum score
                    if scored_lead['growth_score'] >= min_score:
                        all_scored_leads.append(scored_lead)
                        
                except Exception as e:
                    logger.error(f"Error scoring article: {e}")
        
        # Sort by score (descending)
        all_scored_leads.sort(key=lambda x: x['growth_score'], reverse=True)
        
        # Deduplicate by company name
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
    
    def save_scored_leads(
        self,
        scored_leads: List[Dict],
        output_path: str = "data/output/osint_leads/scored_leads.json"
    ) -> None:
        """
        Save scored leads to JSON file.
        
        Args:
            scored_leads: List of scored lead dictionaries
            output_path: Path to output JSON file
        """
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Prepare output with metadata
        output_data = {
            'metadata': {
                'generated_at': datetime.now().isoformat(),
                'total_leads': len(scored_leads),
                'high_priority_leads': len([l for l in scored_leads if l['growth_score'] >= 100]),
                'medium_priority_leads': len([l for l in scored_leads if 50 <= l['growth_score'] < 100]),
                'low_priority_leads': len([l for l in scored_leads if 20 <= l['growth_score'] < 50]),
            },
            'leads': scored_leads
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Saved {len(scored_leads)} scored leads to {output_path}")
        
        # Also create a summary CSV for easy viewing
        self._save_summary_csv(scored_leads, output_path.replace('.json', '_summary.csv'))
    
    def _save_summary_csv(self, scored_leads: List[Dict], csv_path: str) -> None:
        """
        Save a summary CSV of scored leads.
        
        Args:
            scored_leads: List of scored lead dictionaries
            csv_path: Path to output CSV file
        """
        import csv
        
        with open(csv_path, 'w', newline='', encoding='utf-8') as f:
            if not scored_leads:
                return
            
            fieldnames = [
                'company_name', 'growth_score', 'predicted_hiring_window',
                'outsourcing_potential', 'source_url', 'article_date'
            ]
            
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            
            for lead in scored_leads:
                writer.writerow({
                    'company_name': lead['company_name'],
                    'growth_score': lead['growth_score'],
                    'predicted_hiring_window': lead['predicted_hiring_window'],
                    'outsourcing_potential': lead['outsourcing_potential'],
                    'source_url': lead['source_url'],
                    'article_date': lead.get('article_date', 'N/A')
                })
        
        logger.info(f"Saved summary CSV to {csv_path}")


# Main execution
if __name__ == "__main__":
    # Initialize scorer
    scorer = OSINTLeadScorer(use_nltk=True)
    
    # Define search queries for different lead types
    queries = [
        "tech startup series A OR series B funding",
        "tech company expansion OR hiring",
        "software company raises funding",
    ]
    
    # Target regions
    regions = ["US"]  # Can add "GB" for UK, etc.
    
    all_leads = []
    
    # Process each query
    for query in queries:
        logger.info(f"\n{'='*60}")
        logger.info(f"Processing query: {query}")
        logger.info(f"{'='*60}\n")
        
        leads = scorer.score_news_batch(
            query=query,
            regions=regions,
            period="7d",  # Last 7 days
            max_results_per_region=30,
            min_score=20  # Only include leads with score >= 20
        )
        
        all_leads.extend(leads)
    
    # Deduplicate across all queries
    seen_urls = set()
    unique_all_leads = []
    for lead in all_leads:
        url = lead['source_url']
        if url not in seen_urls:
            seen_urls.add(url)
            unique_all_leads.append(lead)
    
    # Sort by score
    unique_all_leads.sort(key=lambda x: x['growth_score'], reverse=True)
    
    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = f"data/output/osint_leads/scored_leads_{timestamp}.json"
    
    scorer.save_scored_leads(unique_all_leads, output_path)
    
    # Print summary
    print("\n" + "="*60)
    print("OSINT LEAD SCORING SUMMARY")
    print("="*60)
    print(f"Total Qualified Leads: {len(unique_all_leads)}")
    print(f"\nTop 10 Leads:")
    print("-"*60)
    
    for i, lead in enumerate(unique_all_leads[:10], 1):
        print(f"\n{i}. {lead['company_name']}")
        print(f"   Score: {lead['growth_score']}")
        print(f"   Hiring Window: {lead['predicted_hiring_window']}")
        print(f"   Signals: {', '.join(lead['matched_signals'][:5])}")
        print(f"   Source: {lead['source_site']}")
    
    print("\n" + "="*60)
    print(f"Full results saved to: {output_path}")
    print("="*60)
