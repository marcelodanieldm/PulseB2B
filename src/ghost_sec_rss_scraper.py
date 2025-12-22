"""
SEC.gov RSS Feed Scraper - Free US Funding Data
------------------------------------------------
Scrapes the SEC.gov RSS feed for Form D filings to get daily funding data.
Form D is filed when companies raise capital under Regulation D.

This is a FREE alternative to paid funding databases like Crunchbase.
"""

import feedparser
import logging
import requests
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import re
import time
from pathlib import Path
import json

from ghost_supabase_client import SupabaseClient

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class SECRSSFeedScraper:
    """
    Scraper for SEC.gov RSS feeds to get Form D filings.
    
    SEC provides free RSS feeds for various filing types:
    - Form D: Private placement offerings (funding rounds)
    - Form 8-K: Material events
    - Form 10-K: Annual reports
    
    We focus on Form D as it indicates recent fundraising activity.
    """
    
    # SEC RSS feed URLs
    SEC_RSS_FEEDS = {
        'form_d': 'https://www.sec.gov/cgi-bin/browse-edgar?action=getcurrent&type=D&company=&dateb=&owner=include&start=0&count=100&output=atom',
        'form_d_amendments': 'https://www.sec.gov/cgi-bin/browse-edgar?action=getcurrent&type=D/A&company=&dateb=&owner=include&start=0&count=100&output=atom',
    }
    
    # SEC EDGAR base URL
    SEC_EDGAR_BASE = 'https://www.sec.gov'
    
    def __init__(self, supabase_client: Optional[SupabaseClient] = None):
        """
        Initialize SEC RSS scraper.
        
        Args:
            supabase_client: SupabaseClient instance for data storage
        """
        self.supabase = supabase_client or SupabaseClient()
        
        # Set user agent (required by SEC)
        self.headers = {
            'User-Agent': 'PulseB2B Market Intelligence contact@pulseb2b.com',
            'Accept-Encoding': 'gzip, deflate',
            'Host': 'www.sec.gov'
        }
        
        logger.info("Initialized SEC RSS Feed Scraper")
    
    def scrape_form_d_feed(
        self,
        max_items: int = 100,
        days_back: int = 1
    ) -> List[Dict]:
        """
        Scrape the Form D RSS feed.
        
        Args:
            max_items: Maximum number of items to process
            days_back: Only process filings from last N days
        
        Returns:
            List of parsed Form D filings
        """
        filings = []
        cutoff_date = datetime.now() - timedelta(days=days_back)
        
        logger.info(f"Scraping SEC Form D RSS feed (last {days_back} days)")
        
        for feed_name, feed_url in self.SEC_RSS_FEEDS.items():
            logger.info(f"Processing feed: {feed_name}")
            
            try:
                # Parse RSS feed
                feed = feedparser.parse(feed_url)
                
                if not feed.entries:
                    logger.warning(f"No entries found in {feed_name}")
                    continue
                
                logger.info(f"Found {len(feed.entries)} entries in {feed_name}")
                
                # Process each entry
                for entry in feed.entries[:max_items]:
                    try:
                        # Parse filing date
                        filing_date = self._parse_date(entry.get('updated', entry.get('published')))
                        
                        # Skip if too old
                        if filing_date < cutoff_date:
                            continue
                        
                        # Extract filing information
                        filing = self._parse_feed_entry(entry)
                        
                        if filing:
                            filings.append(filing)
                            
                            # Respect SEC rate limit (10 requests per second)
                            time.sleep(0.15)
                        
                    except Exception as e:
                        logger.error(f"Error processing entry: {e}")
                        continue
                
            except Exception as e:
                logger.error(f"Error processing feed {feed_name}: {e}")
        
        logger.info(f"Scraped {len(filings)} Form D filings")
        
        return filings
    
    def _parse_feed_entry(self, entry: Dict) -> Optional[Dict]:
        """
        Parse a single RSS feed entry.
        
        Args:
            entry: feedparser entry dictionary
        
        Returns:
            Parsed filing dictionary or None
        """
        try:
            title = entry.get('title', '')
            link = entry.get('link', '')
            summary = entry.get('summary', '')
            updated = entry.get('updated', entry.get('published', ''))
            
            # Extract company name from title
            # Format: "D - COMPANY NAME (CIK: 0001234567) (Filer)"
            company_match = re.search(r'^[^-]+-\s*(.+?)\s*\((?:CIK|Filer)', title)
            company_name = company_match.group(1).strip() if company_match else None
            
            # Extract CIK (Central Index Key)
            cik_match = re.search(r'CIK:\s*(\d+)', title)
            cik = cik_match.group(1) if cik_match else None
            
            # Extract accession number from link
            accession_match = re.search(r'accession-number=(\d+-\d+-\d+)', link)
            accession_number = accession_match.group(1) if accession_match else None
            
            filing = {
                'form_type': 'D',
                'company_name': company_name,
                'cik': cik,
                'accession_number': accession_number,
                'filing_date': updated,
                'filing_url': link,
                'summary': summary,
                'source': 'sec_rss',
                'scraped_at': datetime.utcnow().isoformat()
            }
            
            # Try to fetch additional details from the filing
            if link:
                details = self._fetch_filing_details(link)
                if details:
                    filing.update(details)
            
            return filing
            
        except Exception as e:
            logger.error(f"Error parsing feed entry: {e}")
            return None
    
    def _fetch_filing_details(self, filing_url: str) -> Optional[Dict]:
        """
        Fetch additional details from the filing page.
        
        Args:
            filing_url: URL to the filing
        
        Returns:
            Dictionary with additional details
        """
        try:
            # This is a simplified version
            # In production, you'd parse the actual XML filing
            
            response = requests.get(filing_url, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            content = response.text
            
            details = {}
            
            # Extract offering amount (simplified regex)
            amount_match = re.search(r'Total Offering Amount.*?(\d[\d,]+)', content, re.IGNORECASE)
            if amount_match:
                amount_str = amount_match.group(1).replace(',', '')
                try:
                    details['offering_amount'] = float(amount_str)
                except ValueError:
                    pass
            
            # Extract industry
            industry_match = re.search(r'Industry Group Description.*?<td[^>]*>([^<]+)</td>', content, re.IGNORECASE)
            if industry_match:
                details['industry'] = industry_match.group(1).strip()
            
            return details
            
        except Exception as e:
            logger.debug(f"Could not fetch filing details: {e}")
            return None
    
    def _parse_date(self, date_str: str) -> datetime:
        """Parse date string to datetime object."""
        try:
            # Try multiple date formats
            formats = [
                '%Y-%m-%dT%H:%M:%S%z',
                '%Y-%m-%d %H:%M:%S',
                '%Y-%m-%d',
            ]
            
            for fmt in formats:
                try:
                    return datetime.strptime(date_str.split('.')[0].replace('Z', '+0000'), fmt)
                except ValueError:
                    continue
            
            # Fallback to current time
            return datetime.now()
            
        except Exception:
            return datetime.now()
    
    def push_to_supabase(self, filings: List[Dict]) -> Dict:
        """
        Push scraped filings to Supabase.
        
        Args:
            filings: List of filing dictionaries
        
        Returns:
            Result dictionary
        """
        if not filings:
            logger.info("No filings to push to Supabase")
            return {'success': True, 'count': 0}
        
        logger.info(f"Pushing {len(filings)} filings to Supabase")
        
        # Prepare data for companies table
        companies = []
        funding_rounds = []
        
        for filing in filings:
            # Company record
            company = {
                'company_name': filing.get('company_name'),
                'industry': filing.get('industry'),
                'country': 'US',  # Form D is US-only
                'sec_cik': filing.get('cik'),
                'data_source': 'sec_form_d'
            }
            companies.append(company)
            
            # Funding round record
            if filing.get('offering_amount'):
                funding_round = {
                    'company_name': filing.get('company_name'),
                    'funding_type': 'Regulation D',
                    'amount_usd': filing.get('offering_amount'),
                    'announced_date': filing.get('filing_date'),
                    'sec_accession_number': filing.get('accession_number'),
                    'source_url': filing.get('filing_url')
                }
                funding_rounds.append(funding_round)
        
        # Insert into Supabase
        results = {}
        
        if companies:
            results['companies'] = self.supabase.insert_companies(companies)
        
        if funding_rounds:
            results['funding_rounds'] = self.supabase.insert_funding_rounds(funding_rounds)
        
        logger.info(f"Successfully pushed data to Supabase: {results}")
        
        return results
    
    def save_to_file(self, filings: List[Dict], output_path: str = None) -> None:
        """
        Save scraped filings to JSON file.
        
        Args:
            filings: List of filing dictionaries
            output_path: Path to output file
        """
        if output_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = f"data/output/sec_rss/form_d_filings_{timestamp}.json"
        
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(filings, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Saved {len(filings)} filings to {output_path}")


# Main execution for GitHub Actions
if __name__ == "__main__":
    logger.info("="*60)
    logger.info("SEC.gov RSS Feed Scraper - Starting")
    logger.info("="*60)
    
    # Initialize scraper
    scraper = SECRSSFeedScraper()
    
    # Scrape Form D filings from last 24 hours
    filings = scraper.scrape_form_d_feed(
        max_items=100,
        days_back=1
    )
    
    logger.info(f"\nScraped {len(filings)} Form D filings")
    
    # Save to file
    scraper.save_to_file(filings)
    
    # Push to Supabase
    if filings:
        result = scraper.push_to_supabase(filings)
        
        # Print summary
        print("\n" + "="*60)
        print("SEC RSS SCRAPING SUMMARY")
        print("="*60)
        print(f"Total Filings Scraped: {len(filings)}")
        print(f"Companies Added: {result.get('companies', {}).get('count', 0)}")
        print(f"Funding Rounds Added: {result.get('funding_rounds', {}).get('count', 0)}")
        print("="*60)
        
        # Print sample filings
        if filings:
            print("\nSample Filings:")
            for i, filing in enumerate(filings[:5], 1):
                print(f"\n{i}. {filing.get('company_name')}")
                print(f"   CIK: {filing.get('cik')}")
                print(f"   Amount: ${filing.get('offering_amount', 0):,.0f}")
                print(f"   Date: {filing.get('filing_date')}")
    
    logger.info("SEC RSS scraper completed successfully")
