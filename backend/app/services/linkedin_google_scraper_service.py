import requests
from bs4 import BeautifulSoup
import logging
import time
import json
from datetime import datetime
from typing import List, Dict, Optional
from pathlib import Path
import re
from urllib.parse import quote_plus
from app.services.ghost_supabase_client_service import SupabaseClient

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
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
        'react developer'
    ]
    def __init__(self, supabase_client: Optional[SupabaseClient] = None, use_google_api: bool = False):
        self.supabase = supabase_client or SupabaseClient()
        self.use_google_api = use_google_api
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
        logger.info("Initialized LinkedIn Google Search Scraper")
    def search_linkedin_jobs(self, keywords: str, location: str, max_results: int = 20) -> List[Dict]:
        query = f'site:linkedin.com/jobs/view "{keywords}" {location}'
        logger.info(f"Searching: {query}")
        if self.use_google_api:
            return self._search_with_google_api(query, max_results)
        else:
            return self._search_with_scraping(query, max_results)
    def _search_with_scraping(self, query: str, max_results: int) -> List[Dict]:
        jobs = []
        try:
            encoded_query = quote_plus(query)
            url = f"https://www.google.com/search?q={encoded_query}&num={max_results}"
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            search_results = soup.find_all('div', class_='g')
            for result in search_results:
                try:
                    link_tag = result.find('a')
                    if not link_tag or 'href' not in link_tag.attrs:
                        continue
                    job_url = link_tag['href']
                    if 'linkedin.com/jobs/view' not in job_url:
                        continue
                    title_tag = result.find('h3')
                    title = title_tag.text if title_tag else None
                    desc_tag = result.find('div', class_='VwiC3b')
                    description = desc_tag.text if desc_tag else None
                    job_id_match = re.search(r'/jobs/view/(\d+)', job_url)
                    job_id = job_id_match.group(1) if job_id_match else None
                    if job_id:
                        job = {
                            'job_id': job_id,
                            'title': title,
                            'description': description,
                            'url': job_url,
                            'source': 'linkedin',
                            'search_query': query,
                            'scraped_at': datetime.utcnow().isoformat()
                        }
                        jobs.append(job)
                        logger.info(f"Found job: {title}")
                except Exception as e:
                    logger.error(f"Error parsing search result: {e}")
                    continue
            time.sleep(2)
        except Exception as e:
            logger.error(f"Error searching Google: {e}")
        return jobs
    def _search_with_google_api(self, query: str, max_results: int) -> List[Dict]:
        import os
        api_key = os.getenv('GOOGLE_SEARCH_API_KEY')
        search_engine_id = os.getenv('GOOGLE_SEARCH_ENGINE_ID', '017576662512468239146:omuauf_lfve')
        if not api_key:
            logger.warning("Google API key not found. Falling back to scraping.")
            return self._search_with_scraping(query, max_results)
        jobs = []
        try:
            url = "https://www.googleapis.com/customsearch/v1"
            params = {
                'key': api_key,
                'cx': search_engine_id,
                'q': query,
                'num': min(max_results, 10)
            }
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            for item in data.get('items', []):
                job_url = item.get('link', '')
                if 'linkedin.com/jobs/view' not in job_url:
                    continue
                job_id_match = re.search(r'/jobs/view/(\d+)', job_url)
                job_id = job_id_match.group(1) if job_id_match else None
                if job_id:
                    job = {
                        'job_id': job_id,
                        'title': item.get('title'),
                        'description': item.get('snippet'),
                        'url': job_url,
                        'source': 'linkedin',
                        'search_query': query,
                        'scraped_at': datetime.utcnow().isoformat()
                    }
                    jobs.append(job)
        except Exception as e:
            logger.error(f"Error with Google API: {e}")
        return jobs
    def scrape_latam_jobs(self, max_per_location: int = 10, focus_countries: Optional[List[str]] = None) -> List[Dict]:
        if focus_countries is None:
            focus_countries = ['Brazil', 'Mexico']
        all_jobs = []
        target_locations = {}
        for country in focus_countries:
            if country in self.LATAM_LOCATIONS:
                target_locations[country] = self.LATAM_LOCATIONS[country]
        logger.info(f"Scraping jobs for {len(target_locations)} countries")
        sample_keywords = self.JOB_KEYWORDS[:3]
        for country, cities in target_locations.items():
            logger.info(f"\nProcessing {country}")
            main_city = cities[0]
            for keyword in sample_keywords:
                logger.info(f"  Searching: {keyword} in {main_city}")
                try:
                    jobs = self.search_linkedin_jobs(
                        keywords=keyword,
                        location=f"{main_city}, {country}",
                        max_results=max_per_location
                    )
                    for job in jobs:
                        job['country'] = country
                        job['city'] = main_city
                        job['keywords'] = keyword
                    all_jobs.extend(jobs)
                    logger.info(f"    Found {len(jobs)} jobs")
                    time.sleep(3)
                except Exception as e:
                    logger.error(f"Error scraping {keyword} in {main_city}: {e}")
        unique_jobs = self._deduplicate_jobs(all_jobs)
        logger.info(f"\nTotal jobs scraped: {len(all_jobs)}")
        logger.info(f"Unique jobs: {len(unique_jobs)}")
        return unique_jobs
    def _deduplicate_jobs(self, jobs: List[Dict]) -> List[Dict]:
        seen_ids = set()
        unique_jobs = []
        for job in jobs:
            job_id = job.get('job_id')
            if job_id and job_id not in seen_ids:
                seen_ids.add(job_id)
                unique_jobs.append(job)
        return unique_jobs
    def push_to_supabase(self, jobs: List[Dict]) -> Dict:
        if not jobs:
            logger.info("No jobs to push to Supabase")
            return {'success': True, 'count': 0}
        logger.info(f"Pushing {len(jobs)} jobs to Supabase")
        job_postings = []
        for job in jobs:
            posting = {
                'job_id': job.get('job_id'),
                'title': job.get('title'),
                'description': job.get('description'),
                'company_name': self._extract_company_from_title(job.get('title', '')),
                'location': f"{job.get('city')}, {job.get('country')}",
                'country': job.get('country'),
                'job_url': job.get('url'),
                'source': 'linkedin_google',
                'keywords': job.get('keywords')
            }
            job_postings.append(posting)
        result = self.supabase.insert_job_postings(job_postings)
        logger.info(f"Successfully pushed jobs to Supabase: {result}")
        return result
    def _extract_company_from_title(self, title: str) -> Optional[str]:
        if ' - ' in title:
            parts = title.split(' - ')
            if len(parts) >= 2:
                return parts[-1].strip()
        return None
    def save_to_file(self, jobs: List[Dict], output_path: str = None) -> None:
        if output_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = f"data/output/linkedin_jobs/linkedin_jobs_{timestamp}.json"
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(jobs, f, indent=2, ensure_ascii=False)
        logger.info(f"Saved {len(jobs)} jobs to {output_path}")
