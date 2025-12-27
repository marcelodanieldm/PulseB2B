import requests
from bs4 import BeautifulSoup
import time
import re
import logging
from typing import Dict, Optional, List
from urllib.parse import quote_plus
import random

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
                if 'linkedin.com/company/' in href:
                    return href
        except Exception as e:
            logger.error(f"Error searching LinkedIn: {e}")
        return None
