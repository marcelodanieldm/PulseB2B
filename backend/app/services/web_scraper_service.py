import requests
from bs4 import BeautifulSoup
import time
import re
import logging
from typing import Dict, Optional, List
from urllib.parse import quote_plus
import random

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LinkedInScraper:
    def __init__(self, delay_range: tuple = (2, 5)):
        self.delay_range = delay_range
        self.session = requests.Session()
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5'
        }
    def _random_delay(self):
        time.sleep(random.uniform(*self.delay_range))
    def search_company_linkedin(self, company_name: str, country: str = None) -> Optional[str]:
        try:
            query = f'site:linkedin.com/company/{company_name} employees'
            if country:
                query += f' {country}'
            search_url = f'https://www.google.com/search?q={quote_plus(query)}'
            self._random_delay()
            response = self.session.get(search_url, headers=self.headers, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            for link in soup.find_all('a', href=True):
                href = link['href']
                if 'linkedin.com/company/' in href and '/url?q=' in href:
                    linkedin_url = href.split('/url?q=')[1].split('&')[0]
                    if linkedin_url.startswith('http'):
                        return linkedin_url
            return None
        except Exception as e:
            logger.error(f"Error searching: {e}")
            return None
    def extract_employee_count(self, linkedin_url: str) -> Optional[int]:
        try:
            self._random_delay()
            response = self.session.get(linkedin_url, headers=self.headers, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            text = soup.get_text()
            match1 = re.search(r'(\d{1,3}(?:,\d{3})*)\s+employees', text, re.IGNORECASE)
            if match1:
                return int(match1.group(1).replace(',', ''))
            match2 = re.search(r'(\d{1,3}(?:,\d{3})*)-(\d{1,3}(?:,\d{3})*)\s+employees', text, re.IGNORECASE)
            if match2:
                min_count = int(match2.group(1).replace(',', ''))
                max_count = int(match2.group(2).replace(',', ''))
                return (min_count + max_count) // 2
            return None
        except Exception as e:
            logger.error(f"Error extracting count: {e}")
            return None
    def get_company_data(self, company_name: str, country: str = None) -> Dict:
        result = {
            'company_name': company_name,
            'linkedin_url': None,
            'employee_count': None,
            'error': None
        }
        try:
            linkedin_url = self.search_company_linkedin(company_name, country)
            if not linkedin_url:
                result['error'] = 'LinkedIn URL not found'
                return result
            result['linkedin_url'] = linkedin_url
            employee_count = self.extract_employee_count(linkedin_url)
            if employee_count:
                result['employee_count'] = employee_count
            else:
                result['error'] = 'Employee count not found'
            return result
        except Exception as e:
            result['error'] = str(e)
            return result
    def batch_extract(self, companies: List[Dict]) -> List[Dict]:
        results = []
        total = len(companies)
        for idx, company in enumerate(companies, 1):
            logger.info(f"Processing {idx}/{total}: {company['company_name']}")
            result = self.get_company_data(company['company_name'], company.get('country'))
            results.append(result)
        return results

class FallbackDataEnricher:
    STAGE_BENCHMARKS = {
        'Seed': (10, 25),
        'Series A': (25, 75),
        'Series B': (75, 200),
        'Series C': (200, 500),
        'Series D': (500, 1000),
        'Series E': (1000, 2500),
        'Series F': (2500, 5000),
        'Series G': (5000, 10000),
        'Growth': (1000, 5000),
        'Late Stage': (2000, 10000)
    }
    @classmethod
    def estimate_from_funding(cls, funding_stage: str, funding_amount: float = None) -> int:
        if funding_stage in cls.STAGE_BENCHMARKS:
            min_emp, max_emp = cls.STAGE_BENCHMARKS[funding_stage]
        else:
            min_emp, max_emp = 50, 200
        if funding_amount:
            estimated = int(funding_amount / 150000)
            estimated = max(min_emp, min(estimated, max_emp))
            return estimated
        return (min_emp + max_emp) // 2
    @classmethod
    def generate_mock_data(cls, company_name: str, funding_stage: str, funding_amount: float = None) -> Dict:
        employee_count = cls.estimate_from_funding(funding_stage, funding_amount)
        return {
            'company_name': company_name,
            'employee_count': employee_count,
            'linkedin_url': f'https://linkedin.com/company/{company_name.lower().replace(" ", "-")}',
            'error': None,
            'is_mock': True
        }
