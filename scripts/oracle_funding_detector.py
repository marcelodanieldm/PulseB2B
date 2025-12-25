"""
Oracle Funding Detector & Hiring Predictor
==========================================
Parses SEC EDGAR RSS Feed for Form D filings, enriches with web scraping,
and predicts hiring probability using ML without any paid APIs.

Author: PulseB2B Ghost Infrastructure
Date: December 2025
"""

import feedparser
import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from sklearn.preprocessing import MinMaxScaler
from datetime import datetime, timedelta
import time
import json
import os
from typing import Dict, List, Tuple, Optional
import logging
from urllib.parse import urljoin, urlparse
import warnings

warnings.filterwarnings('ignore')

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt', quiet=True)
    
try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords', quiet=True)


class OracleFundingDetector:
    """
    The Oracle: Detects funding rounds from SEC filings and predicts hiring needs.
    """
    
    # SEC EDGAR RSS Feed URLs
    SEC_RSS_FEEDS = {
        'recent': 'https://www.sec.gov/cgi-bin/browse-edgar?action=getcurrent&CIK=&type=D&company=&dateb=&owner=exclude&start=0&count=100&output=atom',
        'daily': 'https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&type=D&dateb=&owner=exclude&start=0&count=100&output=atom'
    }
    
    # Tech Stack Keywords (High-Priority Technologies)
    TECH_STACK_KEYWORDS = {
        'languages': [
            'python', 'javascript', 'typescript', 'java', 'go', 'rust', 
            'ruby', 'php', 'c++', 'c#', 'swift', 'kotlin', 'scala'
        ],
        'frontend': [
            'react', 'vue', 'angular', 'next.js', 'svelte', 'tailwind',
            'webpack', 'vite', 'redux', 'graphql'
        ],
        'backend': [
            'node.js', 'express', 'django', 'flask', 'fastapi', 'spring',
            'rails', 'laravel', '.net', 'asp.net'
        ],
        'cloud': [
            'aws', 'azure', 'gcp', 'kubernetes', 'docker', 'terraform',
            'cloudflare', 'vercel', 'heroku', 'digitalocean'
        ],
        'database': [
            'postgresql', 'mysql', 'mongodb', 'redis', 'elasticsearch',
            'cassandra', 'dynamodb', 'firestore', 'supabase'
        ],
        'ml_ai': [
            'tensorflow', 'pytorch', 'scikit-learn', 'opencv', 'nlp',
            'machine learning', 'deep learning', 'ai', 'llm', 'gpt'
        ]
    }
    
    # Hiring Signal Keywords (Indicators of growth)
    HIRING_SIGNALS = {
        'strong': [
            'hiring', 'recruiting', 'we are looking for', 'join our team',
            'careers', 'job opening', 'expanding team', 'growing team',
            'talent acquisition', 'now hiring'
        ],
        'medium': [
            'team', 'engineers', 'developers', 'talented', 'passionate',
            'innovative', 'scaling', 'growth', 'expanding', 'building'
        ],
        'weak': [
            'startup', 'venture', 'funded', 'series a', 'series b',
            'investment', 'raised', 'round'
        ]
    }
    
    # Funding Amount Patterns (for extraction)
    FUNDING_PATTERNS = [
        r'\$\s*(\d+(?:\.\d+)?)\s*(million|m|mm)',
        r'\$\s*(\d+(?:\.\d+)?)\s*(billion|b)',
        r'(\d+(?:\.\d+)?)\s*(million|m|mm)\s*(?:dollars?|usd|\$)',
        r'raised\s+\$\s*(\d+(?:\.\d+)?)\s*(million|m|mm)',
        r'funding\s+of\s+\$\s*(\d+(?:\.\d+)?)\s*(million|m|mm)'
    ]
    
    def __init__(self, output_dir: str = '../data/output/oracle', use_google_cache: bool = True):
        """Initialize the Oracle detector."""
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        
        self.use_google_cache = use_google_cache  # Bypass bot detection
        
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        })
        
        self.stop_words = set(stopwords.words('english'))
        self.scaler = MinMaxScaler(feature_range=(0, 100))
        
        logger.info(f"🔮 Oracle Funding Detector initialized (Google Cache: {use_google_cache})")
    
    def fetch_sec_filings(self, feed_type: str = 'recent', max_items: int = 50, max_retries: int = 3, retry_delay: int = 60) -> List[Dict]:
        """
        Fetch recent Form D filings from SEC EDGAR RSS feed with retry logic.
        
        Args:
            feed_type: Type of feed ('recent' or 'daily')
            max_items: Maximum number of filings to fetch
            max_retries: Maximum number of retry attempts
            retry_delay: Delay between retries in seconds
            
        Returns:
            List of filing dictionaries with company info
        """
        logger.info(f"📥 Fetching SEC Form D filings ({feed_type})...")
        
        for attempt in range(max_retries):
            try:
                feed_url = self.SEC_RSS_FEEDS.get(feed_type, self.SEC_RSS_FEEDS['recent'])
                logger.info(f"   Attempt {attempt + 1}/{max_retries}: {feed_url}")
                
                # Parse RSS feed
                feed = feedparser.parse(feed_url)
                
                # Check for feed errors
                if hasattr(feed, 'bozo') and feed.bozo:
                    logger.warning(f"⚠️ Feed parsing issue: {getattr(feed, 'bozo_exception', 'Unknown error')}")
                
                # Check if feed has entries
                if not hasattr(feed, 'entries') or len(feed.entries) == 0:
                    logger.warning(f"⚠️ No entries found in feed (Attempt {attempt + 1}/{max_retries})")
                    
                    if attempt < max_retries - 1:
                        logger.info(f"   Retrying in {retry_delay} seconds...")
                        time.sleep(retry_delay)
                        continue
                    else:
                        logger.error(f"❌ No entries found after {max_retries} attempts")
                        logger.error(f"   Feed status: {getattr(feed, 'status', 'unknown')}")
                        logger.error(f"   Feed info: {getattr(feed.feed, 'title', 'No title')}")
                        return []
                
                filings = []
                for entry in feed.entries[:max_items]:
                    filing = {
                        'company_name': entry.get('title', 'Unknown'),
                        'filing_date': entry.get('updated', ''),
                        'filing_url': entry.get('link', ''),
                        'summary': entry.get('summary', ''),
                        'cik': self._extract_cik(entry.get('link', ''))
                    }
                    
                    # Clean company name (remove form type)
                    filing['company_name'] = re.sub(r'\s*-\s*Form D.*$', '', filing['company_name']).strip()
                    
                    filings.append(filing)
                    logger.info(f"  ✓ Found: {filing['company_name']}")
                
                if len(filings) > 0:
                    logger.info(f"✅ Fetched {len(filings)} Form D filings")
                    return filings
                else:
                    logger.warning(f"⚠️ Feed parsed but no valid filings extracted (Attempt {attempt + 1}/{max_retries})")
                    if attempt < max_retries - 1:
                        logger.info(f"   Retrying in {retry_delay} seconds...")
                        time.sleep(retry_delay)
                
            except requests.exceptions.RequestException as e:
                logger.error(f"❌ Network error fetching SEC filings (Attempt {attempt + 1}/{max_retries}): {e}")
                if attempt < max_retries - 1:
                    logger.info(f"   Retrying in {retry_delay} seconds...")
                    time.sleep(retry_delay)
                else:
                    logger.error(f"❌ Failed after {max_retries} network error attempts")
                    return []
                    
            except Exception as e:
                logger.error(f"❌ Unexpected error fetching SEC filings (Attempt {attempt + 1}/{max_retries}): {type(e).__name__}: {e}")
                if attempt < max_retries - 1:
                    logger.info(f"   Retrying in {retry_delay} seconds...")
                    time.sleep(retry_delay)
                else:
                    logger.error(f"❌ Failed after {max_retries} attempts")
                    return []
        
        logger.error("❌ All retry attempts exhausted")
        return []
    
    def _extract_cik(self, url: str) -> str:
        """Extract CIK number from SEC filing URL."""
        match = re.search(r'CIK=(\d+)', url)
        return match.group(1) if match else ''
    
    def scrape_company_info(self, company_name: str) -> Dict:
        """
        Scrape company information from web search + company website.
        
        Args:
            company_name: Name of the company
            
        Returns:
            Dictionary with company info (website, description, tech stack)
        """
        logger.info(f"🔍 Scraping info for: {company_name}")
        
        company_info = {
            'website': '',
            'description': '',
            'about_us': '',
            'tech_stack': [],
            'hiring_signals': 0
        }
        
        try:
            # Step 1: Find company website via search simulation
            website = self._find_company_website(company_name)
            if website:
                company_info['website'] = website
                
                # Step 2: Scrape company website
                website_data = self._scrape_website(website)
                company_info.update(website_data)
                
            time.sleep(2)  # Respectful crawling
            
        except Exception as e:
            logger.warning(f"⚠️  Could not scrape {company_name}: {e}")
        
        return company_info
    
    def _find_company_website(self, company_name: str) -> Optional[str]:
        """
        Find company website using DuckDuckGo HTML search (no API needed).
        
        Args:
            company_name: Company name to search
            
        Returns:
            Company website URL or None
        """
        try:
            # Use DuckDuckGo HTML search (no API key needed)
            search_url = f"https://html.duckduckgo.com/html/?q={company_name}+official+website"
            
            response = self.session.get(search_url, timeout=10)
            if response.status_code != 200:
                return None
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find first result link
            result = soup.find('a', {'class': 'result__a'})
            if result:
                website = result.get('href', '')
                # Clean URL
                if website.startswith('//duckduckgo.com/l/?uddg='):
                    # Extract actual URL from DuckDuckGo redirect
                    website = requests.utils.unquote(website.split('uddg=')[1].split('&')[0])
                return website
            
        except Exception as e:
            logger.debug(f"Could not find website for {company_name}: {e}")
        
        return None
    
    def _scrape_website(self, url: str) -> Dict:
        """
        Scrape company website for About Us, tech stack, and hiring signals.
        Uses Google Cache to bypass bot detection if enabled.
        
        Args:
            url: Company website URL
            
        Returns:
            Dictionary with scraped data
        """
        data = {
            'description': '',
            'about_us': '',
            'tech_stack': [],
            'hiring_signals': 0
        }
        
        try:
            # Try Google Cache first to bypass bot detection
            if self.use_google_cache:
                cache_url = f"https://webcache.googleusercontent.com/search?q=cache:{url}"
                logger.debug(f"Trying Google Cache: {cache_url}")
                
                try:
                    response = self.session.get(cache_url, timeout=10)
                    if response.status_code == 200 and len(response.text) > 500:
                        logger.debug(f"✅ Using Google Cache for {url}")
                        soup = BeautifulSoup(response.text, 'html.parser')
                    else:
                        # Fallback to direct scraping
                        logger.debug(f"⚠️  Cache failed, trying direct: {url}")
                        response = self.session.get(url, timeout=10)
                        if response.status_code != 200:
                            return data
                        soup = BeautifulSoup(response.text, 'html.parser')
                except:
                    # Fallback to direct scraping
                    logger.debug(f"⚠️  Cache error, trying direct: {url}")
                    response = self.session.get(url, timeout=10)
                    if response.status_code != 200:
                        return data
                    soup = BeautifulSoup(response.text, 'html.parser')
            else:
                # Direct scraping (no cache)
                response = self.session.get(url, timeout=10)
                if response.status_code != 200:
                    return data
                soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract meta description
            meta_desc = soup.find('meta', {'name': 'description'}) or \
                       soup.find('meta', {'property': 'og:description'})
            if meta_desc:
                data['description'] = meta_desc.get('content', '')
            
            # Find About Us page
            about_links = soup.find_all('a', href=True)
            about_url = None
            for link in about_links:
                href = link.get('href', '').lower()
                text = link.get_text().lower()
                if any(keyword in href or keyword in text for keyword in ['about', 'company', 'who-we-are']):
                    about_url = urljoin(url, link['href'])
                    break
            
            # Scrape About Us page
            if about_url:
                try:
                    about_response = self.session.get(about_url, timeout=10)
                    about_soup = BeautifulSoup(about_response.text, 'html.parser')
                    
                    # Extract text content
                    paragraphs = about_soup.find_all('p')
                    data['about_us'] = ' '.join([p.get_text() for p in paragraphs[:5]])
                    
                except Exception:
                    pass
            
            # If no About page, use homepage content
            if not data['about_us']:
                paragraphs = soup.find_all('p')
                data['about_us'] = ' '.join([p.get_text() for p in paragraphs[:5]])
            
            # Detect tech stack from page content
            page_text = soup.get_text().lower()
            data['tech_stack'] = self._detect_tech_stack(page_text)
            
            # Count hiring signals
            data['hiring_signals'] = self._count_hiring_signals(page_text)
            
        except Exception as e:
            logger.debug(f"Error scraping {url}: {e}")
        
        return data
    
    def _detect_tech_stack(self, text: str) -> List[str]:
        """
        Detect tech stack keywords from text using keyword matching.
        
        Args:
            text: Text content to analyze
            
        Returns:
            List of detected technologies
        """
        detected_tech = []
        text_lower = text.lower()
        
        for category, keywords in self.TECH_STACK_KEYWORDS.items():
            for keyword in keywords:
                # Use word boundaries for accurate matching
                pattern = r'\b' + re.escape(keyword.lower()) + r'\b'
                if re.search(pattern, text_lower):
                    detected_tech.append(keyword)
        
        return list(set(detected_tech))  # Remove duplicates
    
    def _count_hiring_signals(self, text: str) -> int:
        """
        Count hiring signals in text (weighted by strength).
        
        Args:
            text: Text content to analyze
            
        Returns:
            Weighted hiring signal score
        """
        text_lower = text.lower()
        score = 0
        
        for keyword in self.HIRING_SIGNALS['strong']:
            if keyword in text_lower:
                score += 3
        
        for keyword in self.HIRING_SIGNALS['medium']:
            if keyword in text_lower:
                score += 2
        
        for keyword in self.HIRING_SIGNALS['weak']:
            if keyword in text_lower:
                score += 1
        
        return score
    
    def extract_funding_amount(self, text: str) -> Tuple[float, str]:
        """
        Extract funding amount from text using regex patterns.
        
        Args:
            text: Text containing funding information
            
        Returns:
            Tuple of (amount in millions, source text)
        """
        for pattern in self.FUNDING_PATTERNS:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                amount = float(match.group(1))
                unit = match.group(2).lower()
                
                # Convert to millions
                if unit.startswith('b'):
                    amount *= 1000  # Billion to million
                
                return amount, match.group(0)
        
        return 0.0, 'Not disclosed'
    
    def calculate_hiring_probability(self, 
                                     funding_amount: float,
                                     tech_stack_count: int,
                                     hiring_signals: int,
                                     days_since_filing: int) -> float:
        """
        Calculate hiring probability score using ML-based scoring.
        
        Args:
            funding_amount: Funding amount in millions
            tech_stack_count: Number of detected technologies
            hiring_signals: Weighted hiring signal count
            days_since_filing: Days since Form D filing
            
        Returns:
            Hiring probability score (0-100%)
        """
        # Feature engineering
        features = {
            'funding_score': min(funding_amount / 100, 10),  # Cap at 10
            'tech_diversity': min(tech_stack_count, 10),
            'hiring_intent': min(hiring_signals, 10),
            'recency': max(0, 10 - (days_since_filing / 30))  # Decay over 30 days
        }
        
        # Weighted scoring model
        weights = {
            'funding_score': 0.35,      # 35% weight (more funding = more hiring)
            'tech_diversity': 0.25,     # 25% weight (more tech = more roles)
            'hiring_intent': 0.30,      # 30% weight (explicit signals)
            'recency': 0.10             # 10% weight (recent = more likely)
        }
        
        # Calculate weighted score
        score = sum(features[key] * weights[key] * 10 for key in features)
        
        # Normalize to 0-100 scale
        score = min(max(score, 0), 100)
        
        return round(score, 2)
    
    def process_filings(self, filings: List[Dict]) -> pd.DataFrame:
        """
        Process all filings with enrichment and scoring.
        
        Args:
            filings: List of SEC filing dictionaries
            
        Returns:
            DataFrame with enriched data and scores
        """
        logger.info("🔮 Processing filings with Oracle AI...")
        
        results = []
        
        for idx, filing in enumerate(filings, 1):
            logger.info(f"\n📊 Processing {idx}/{len(filings)}: {filing['company_name']}")
            
            # Parse filing date
            try:
                filing_date = datetime.strptime(filing['filing_date'][:10], '%Y-%m-%d')
                days_since = (datetime.now() - filing_date).days
            except:
                filing_date = datetime.now()
                days_since = 0
            
            # Scrape company info
            company_info = self.scrape_company_info(filing['company_name'])
            
            # Extract funding amount
            combined_text = f"{filing['summary']} {company_info['description']} {company_info['about_us']}"
            funding_amount, funding_source = self.extract_funding_amount(combined_text)
            
            # Calculate hiring probability
            hiring_prob = self.calculate_hiring_probability(
                funding_amount=funding_amount,
                tech_stack_count=len(company_info['tech_stack']),
                hiring_signals=company_info['hiring_signals'],
                days_since_filing=days_since
            )
            
            # Build result
            result = {
                'Company Name': filing['company_name'],
                'Funding Date': filing_date.strftime('%Y-%m-%d'),
                'Days Since Filing': days_since,
                'Estimated Amount (M)': f'${funding_amount:.1f}M' if funding_amount > 0 else 'Not disclosed',
                'Funding Source': funding_source,
                'Tech Stack': ', '.join(company_info['tech_stack'][:10]) if company_info['tech_stack'] else 'Not detected',
                'Tech Count': len(company_info['tech_stack']),
                'Hiring Signals': company_info['hiring_signals'],
                'Hiring Probability (%)': hiring_prob,
                'Website': company_info['website'],
                'Description': company_info['description'][:200] if company_info['description'] else '',
                'CIK': filing['cik'],
                'Filing URL': filing['filing_url']
            }
            
            results.append(result)
            logger.info(f"  ✓ Score: {hiring_prob}% | Tech: {result['Tech Count']} | Signals: {result['Hiring Signals']}")
            
            # Rate limiting
            time.sleep(3)
        
        df = pd.DataFrame(results)
        
        # Sort by hiring probability (descending)
        df = df.sort_values('Hiring Probability (%)', ascending=False)
        
        return df
    
    def export_results(self, df: pd.DataFrame, filename: str = None) -> str:
        """
        Export results to CSV with timestamp.
        
        Args:
            df: Results DataFrame
            filename: Optional custom filename
            
        Returns:
            Path to exported file
        """
        if filename is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'oracle_predictions_{timestamp}.csv'
        
        filepath = os.path.join(self.output_dir, filename)
        df.to_csv(filepath, index=False, encoding='utf-8')
        
        logger.info(f"💾 Results exported to: {filepath}")
        return filepath
    
    def generate_summary_report(self, df: pd.DataFrame) -> Dict:
        """
        Generate summary statistics and insights.
        
        Args:
            df: Results DataFrame
            
        Returns:
            Summary dictionary
        """
        summary = {
            'total_companies': len(df),
            'high_probability_count': len(df[df['Hiring Probability (%)'] >= 70]),
            'medium_probability_count': len(df[(df['Hiring Probability (%)'] >= 40) & (df['Hiring Probability (%)'] < 70)]),
            'low_probability_count': len(df[df['Hiring Probability (%)'] < 40]),
            'avg_hiring_probability': df['Hiring Probability (%)'].mean(),
            'total_funding_disclosed': df[df['Estimated Amount (M)'] != 'Not disclosed'].shape[0],
            'avg_tech_count': df['Tech Count'].mean(),
            'top_5_opportunities': df.head(5)[['Company Name', 'Hiring Probability (%)']].to_dict('records')
        }
        
        logger.info("\n" + "="*60)
        logger.info("📊 ORACLE SUMMARY REPORT")
        logger.info("="*60)
        logger.info(f"Total Companies Analyzed: {summary['total_companies']}")
        logger.info(f"High Probability (70%+): {summary['high_probability_count']}")
        logger.info(f"Medium Probability (40-70%): {summary['medium_probability_count']}")
        logger.info(f"Low Probability (<40%): {summary['low_probability_count']}")
        logger.info(f"Average Hiring Probability: {summary['avg_hiring_probability']:.1f}%")
        logger.info(f"Companies with Disclosed Funding: {summary['total_funding_disclosed']}")
        logger.info(f"Average Tech Stack Size: {summary['avg_tech_count']:.1f}")
        logger.info("\n🏆 TOP 5 HIRING OPPORTUNITIES:")
        for idx, opp in enumerate(summary['top_5_opportunities'], 1):
            logger.info(f"  {idx}. {opp['Company Name']} - {opp['Hiring Probability (%)']}%")
        logger.info("="*60 + "\n")
        
        return summary


def main():
    """Main execution function."""
    print("\n" + "="*60)
    print("🔮 ORACLE FUNDING DETECTOR & HIRING PREDICTOR")
    print("="*60)
    print("📡 Parsing SEC EDGAR for Form D filings...")
    print("🧠 Predicting hiring needs with ML (No API costs!)")
    print("="*60 + "\n")
    
    # Initialize Oracle
    oracle = OracleFundingDetector()
    
    # Get max companies from environment variable (default 20)
    max_companies = int(os.environ.get('MAX_COMPANIES', 20))
    logger.info(f"🎯 Target: {max_companies} companies")
    
    # Fetch SEC filings with retry logic
    logger.info("🔄 Attempting to fetch SEC filings with retry logic...")
    filings = oracle.fetch_sec_filings(
        feed_type='recent', 
        max_items=max_companies,
        max_retries=3,
        retry_delay=60
    )
    
    if not filings:
        logger.error("❌ No filings found after all retry attempts.")
        logger.error("📋 Possible reasons:")
        logger.error("   1. SEC EDGAR RSS feed is temporarily unavailable")
        logger.error("   2. Network connectivity issues")
        logger.error("   3. SEC website maintenance or rate limiting")
        logger.error("   4. No new Form D filings in the current period")
        logger.error("")
        logger.error("💡 Recommendations:")
        logger.error("   - Check SEC EDGAR status: https://www.sec.gov/edgar/search-and-access")
        logger.error("   - Verify network connectivity")
        logger.error("   - Try again in 30-60 minutes")
        logger.error("   - Check if IP is rate-limited by SEC")
        
        # Create empty results file to indicate run completed but no data
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        empty_result = {
            'status': 'no_data',
            'message': 'No SEC Form D filings found',
            'timestamp': timestamp,
            'attempts': 3
        }
        
        output_dir = '../data/output/oracle'
        os.makedirs(output_dir, exist_ok=True)
        status_file = os.path.join(output_dir, f'oracle_status_{timestamp}.json')
        
        with open(status_file, 'w') as f:
            json.dump(empty_result, f, indent=2)
        
        logger.info(f"📄 Status file created: {status_file}")
        logger.warning("⚠️ Exiting without data - This is a soft failure")
        
        # Exit with code 0 (success) since this is not a script error
        # but a data availability issue
        return
    
    logger.info(f"✅ Successfully fetched {len(filings)} filings")
    
    # Process filings with enrichment
    try:
        results_df = oracle.process_filings(filings)
        
        if results_df.empty:
            logger.warning("⚠️ Processing completed but no valid results")
            return
        
    except Exception as e:
        logger.error(f"❌ Error processing filings: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return
    
    # Export to CSV
    try:
        output_file = oracle.export_results(results_df)
        logger.info(f"✅ Results exported: {output_file}")
    except Exception as e:
        logger.error(f"❌ Error exporting results: {e}")
        return
    
    # Generate summary
    try:
        summary = oracle.generate_summary_report(results_df)
        
        # Save summary as JSON
        summary_file = output_file.replace('.csv', '_summary.json')
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2)
        
        logger.info(f"✅ Summary generated: {summary_file}")
    except Exception as e:
        logger.error(f"❌ Error generating summary: {e}")
    
    print("\n✅ Oracle analysis complete!")
    print(f"📄 Results: {output_file}")
    print(f"📊 Summary: {summary_file}")
    print("\n🎯 Next Steps:")
    print("  1. Review high-probability companies (70%+)")
    print("  2. Cross-reference with LinkedIn for open positions")
    print("  3. Reach out to HR/Talent teams")
    print("\n")


if __name__ == '__main__':
    main()
