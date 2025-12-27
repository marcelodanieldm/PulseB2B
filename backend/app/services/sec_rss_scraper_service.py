import feedparser
import logging
import requests
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import re
import time
from pathlib import Path
import json
from app.services.ghost_supabase_client_service import SupabaseClient

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class SECRSSFeedScraper:
    SEC_RSS_FEEDS = {
        'form_d': 'https://www.sec.gov/cgi-bin/browse-edgar?action=getcurrent&type=D&company=&dateb=&owner=include&start=0&count=100&output=atom',
        'form_d_amendments': 'https://www.sec.gov/cgi-bin/browse-edgar?action=getcurrent&type=D/A&company=&dateb=&owner=include&start=0&count=100&output=atom',
    }
    SEC_EDGAR_BASE = 'https://www.sec.gov'
    def __init__(self, supabase_client: Optional[SupabaseClient] = None):
        self.supabase = supabase_client or SupabaseClient()
        self.headers = {
            'User-Agent': 'PulseB2B Market Intelligence contact@pulseb2b.com',
            'Accept-Encoding': 'gzip, deflate',
            'Host': 'www.sec.gov'
        }
        logger.info("Initialized SEC RSS Feed Scraper")
    def scrape_form_d_feed(self, max_items: int = 100, days_back: int = 1) -> List[Dict]:
        filings = []
        cutoff_date = datetime.now() - timedelta(days=days_back)
        logger.info(f"Scraping SEC Form D RSS feed (last {days_back} days)")
        for feed_name, feed_url in self.SEC_RSS_FEEDS.items():
            logger.info(f"Processing feed: {feed_name}")
            try:
                feed = feedparser.parse(feed_url)
                if not feed.entries:
                    logger.warning(f"No entries found in {feed_name}")
                    continue
                logger.info(f"Found {len(feed.entries)} entries in {feed_name}")
                for entry in feed.entries[:max_items]:
                    try:
                        filing_date = self._parse_date(entry.get('updated', entry.get('published')))
                        if filing_date < cutoff_date:
                            continue
                        filing = self._parse_feed_entry(entry)
                        if filing:
                            filings.append(filing)
                            time.sleep(0.15)
                    except Exception as e:
                        logger.error(f"Error processing entry: {e}")
                        continue
            except Exception as e:
                logger.error(f"Error processing feed {feed_name}: {e}")
        logger.info(f"Scraped {len(filings)} Form D filings")
        return filings
    def _parse_feed_entry(self, entry: Dict) -> Optional[Dict]:
        try:
            title = entry.get('title', '')
            link = entry.get('link', '')
            summary = entry.get('summary', '')
            updated = entry.get('updated', entry.get('published', ''))
            company_match = re.search(r'^[^-]+-\s*(.+?)\s*\((?:CIK|Filer)', title)
            company_name = company_match.group(1).strip() if company_match else None
            cik_match = re.search(r'CIK:\s*(\d+)', title)
            cik = cik_match.group(1) if cik_match else None
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
            if link:
                details = self._fetch_filing_details(link)
                if details:
                    filing.update(details)
            return filing
        except Exception as e:
            logger.error(f"Error parsing feed entry: {e}")
            return None
    def _fetch_filing_details(self, filing_url: str) -> Optional[Dict]:
        try:
            response = requests.get(filing_url, headers=self.headers, timeout=10)
            response.raise_for_status()
            content = response.text
            details = {}
            amount_match = re.search(r'Total Offering Amount.*?(\d[\d,]+)', content, re.IGNORECASE)
            if amount_match:
                amount_str = amount_match.group(1).replace(',', '')
                try:
                    details['offering_amount'] = float(amount_str)
                except ValueError:
                    pass
            industry_match = re.search(r'Industry Group Description.*?<td[^>]*>([^<]+)</td>', content, re.IGNORECASE)
            if industry_match:
                details['industry'] = industry_match.group(1).strip()
            return details
        except Exception as e:
            logger.debug(f"Could not fetch filing details: {e}")
            return None
    def _parse_date(self, date_str: str) -> datetime:
        try:
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
            return datetime.now()
        except Exception:
            return datetime.now()
    def push_to_supabase(self, filings: List[Dict]) -> Dict:
        if not filings:
            logger.info("No filings to push to Supabase")
            return {'success': True, 'count': 0}
        logger.info(f"Pushing {len(filings)} filings to Supabase")
        companies = []
        funding_rounds = []
        for filing in filings:
            company = {
                'company_name': filing.get('company_name'),
                'industry': filing.get('industry'),
                'country': 'US',
                'sec_cik': filing.get('cik'),
                'data_source': 'sec_form_d'
            }
            companies.append(company)
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
        results = {}
        if companies:
            results['companies'] = self.supabase.insert_companies(companies)
        if funding_rounds:
            results['funding_rounds'] = self.supabase.insert_funding_rounds(funding_rounds)
        logger.info(f"Successfully pushed data to Supabase: {results}")
        return results
    def save_to_file(self, filings: List[Dict], output_path: str = None) -> None:
        if output_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = f"data/output/sec_rss/form_d_filings_{timestamp}.json"
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(filings, f, indent=2, ensure_ascii=False)
        logger.info(f"Saved {len(filings)} filings to {output_path}")
