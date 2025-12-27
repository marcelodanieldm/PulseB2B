import logging
from typing import List, Dict, Optional
from app.utils.supabase_client import SupabaseClient
import requests
from bs4 import BeautifulSoup
from urllib.parse import quote_plus

logger = logging.getLogger(__name__)

class LinkedInGoogleScraper:
    LATAM_LOCATIONS = {
        'Brazil': [
            'São Paulo', 'Rio de Janeiro', 'Brasília', 'Belo Horizonte',
            'Curitiba', 'Porto Alegre', 'Salvador', 'Fortaleza'
        ],
        'Mexico': [
            'Mexico City', 'Guadalajara', 'Monterrey', 'Puebla',
            'Tijuana', 'León', 'Querétaro'
        ],
        'Argentina': [
            'Buenos Aires', 'Córdoba', 'Rosario', 'Mendoza'
        ],
        'Colombia': [
            'Bogotá', 'Medellín', 'Cali', 'Barranquilla'
        ],
        'Chile': [
            'Santiago', 'Valparaíso', 'Concepción'
        ]
    }
    JOB_KEYWORDS = [
        'software engineer',
        'backend developer',
        'frontend developer',
        'full stack developer',
        'data engineer',
        'devops engineer',
        'cloud engineer',
        'mobile developer',
        'python developer',
        'react developer',
        'QA Engineer',
        'QA Automation',
        'QA'
    ]

    def __init__(self, supabase_client: Optional[SupabaseClient] = None):
        self.supabase = supabase_client or SupabaseClient()
        self.headers = {
            'User-Agent': 'Mozilla/5.0',
            'Accept': 'text/html',
        }
        logger.info("Initialized LinkedIn Google Search Scraper")

    def search_linkedin_jobs(self, keywords: str, location: str, max_results: int = 20) -> List[Dict]:
        query = f"site:linkedin.com/jobs/view {keywords} {location}"
        url = f"https://www.google.com/search?q={quote_plus(query)}"
        resp = requests.get(url, headers=self.headers)
        soup = BeautifulSoup(resp.text, 'html.parser')
        results = []
        for g in soup.find_all('div', class_='g'):
            link = g.find('a', href=True)
            if link and 'linkedin.com/jobs/view' in link['href']:
                results.append({'url': link['href'], 'title': link.text})
            if len(results) >= max_results:
                break
        return results
