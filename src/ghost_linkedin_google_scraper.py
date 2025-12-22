"""
LinkedIn Jobs via Google Search - LATAM Scraper
------------------------------------------------
Scrapes LinkedIn job postings using Google Search to avoid LinkedIn's expensive API.

Search pattern: site:linkedin.com/jobs/view [location] [keywords]

This is a FREE alternative to LinkedIn's Talent Solutions API.
"""

import requests
from bs4 import BeautifulSoup
import logging
import time
import json
from datetime import datetime
from typing import List, Dict, Optional
from pathlib import Path
import re
from urllib.parse import quote_plus, urlparse, parse_qs

from ghost_supabase_client import SupabaseClient

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class LinkedInGoogleScraper:
    """
    Scraper that uses Google Search to find LinkedIn job postings.
    
    Strategy: Use Google's site: operator to search LinkedIn specifically.
    Example query: site:linkedin.com/jobs/view "software engineer" Brazil
    
    This bypasses LinkedIn's API restrictions and is completely free.
    """
    
    # LATAM countries and cities to target
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
    
    # Job keywords to search for
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
    
    def __init__(
        self,
        supabase_client: Optional[SupabaseClient] = None,
        use_google_api: bool = False
    ):
        """
        Initialize LinkedIn Google scraper.
        
        Args:
            supabase_client: SupabaseClient instance
            use_google_api: If True, use Google Custom Search API (requires key)
        """
        self.supabase = supabase_client or SupabaseClient()
        self.use_google_api = use_google_api
        
        # Headers to mimic browser
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
        
        logger.info("Initialized LinkedIn Google Search Scraper")
    
    def search_linkedin_jobs(
        self,
        keywords: str,
        location: str,
        max_results: int = 20
    ) -> List[Dict]:
        """
        Search for LinkedIn jobs using Google.
        
        Args:
            keywords: Job keywords (e.g., "software engineer")
            location: Location (e.g., "São Paulo")
            max_results: Maximum number of results
        
        Returns:
            List of job posting dictionaries
        """
        # Build Google search query
        query = f'site:linkedin.com/jobs/view "{keywords}" {location}'
        
        logger.info(f"Searching: {query}")
        
        if self.use_google_api:
            return self._search_with_google_api(query, max_results)
        else:
            return self._search_with_scraping(query, max_results)
    
    def _search_with_scraping(
        self,
        query: str,
        max_results: int
    ) -> List[Dict]:
        """
        Search Google by scraping HTML (free method).
        
        Args:
            query: Google search query
            max_results: Maximum number of results
        
        Returns:
            List of job posting dictionaries
        """
        jobs = []
        
        try:
            # URL encode query
            encoded_query = quote_plus(query)
            url = f"https://www.google.com/search?q={encoded_query}&num={max_results}"
            
            # Make request
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            # Parse HTML
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find search result links
            search_results = soup.find_all('div', class_='g')
            
            for result in search_results:
                try:
                    # Extract link
                    link_tag = result.find('a')
                    if not link_tag or 'href' not in link_tag.attrs:
                        continue
                    
                    job_url = link_tag['href']
                    
                    # Verify it's a LinkedIn job URL
                    if 'linkedin.com/jobs/view' not in job_url:
                        continue
                    
                    # Extract title
                    title_tag = result.find('h3')
                    title = title_tag.text if title_tag else None
                    
                    # Extract description snippet
                    desc_tag = result.find('div', class_='VwiC3b')
                    description = desc_tag.text if desc_tag else None
                    
                    # Extract job ID from URL
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
            
            # Respect rate limiting
            time.sleep(2)
            
        except Exception as e:
            logger.error(f"Error searching Google: {e}")
        
        return jobs
    
    def _search_with_google_api(
        self,
        query: str,
        max_results: int
    ) -> List[Dict]:
        """
        Search using Google Custom Search API (requires API key).
        
        Args:
            query: Google search query
            max_results: Maximum number of results
        
        Returns:
            List of job posting dictionaries
        """
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
                'num': min(max_results, 10)  # API limit is 10 per request
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            for item in data.get('items', []):
                job_url = item.get('link', '')
                
                if 'linkedin.com/jobs/view' not in job_url:
                    continue
                
                # Extract job ID
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
    
    def scrape_latam_jobs(
        self,
        max_per_location: int = 10,
        focus_countries: Optional[List[str]] = None
    ) -> List[Dict]:
        """
        Scrape LinkedIn jobs for LATAM locations.
        
        Args:
            max_per_location: Max results per location
            focus_countries: List of countries to focus on (default: Brazil, Mexico)
        
        Returns:
            List of all scraped jobs
        """
        if focus_countries is None:
            focus_countries = ['Brazil', 'Mexico']
        
        all_jobs = []
        
        # Get locations for specified countries
        target_locations = {}
        for country in focus_countries:
            if country in self.LATAM_LOCATIONS:
                target_locations[country] = self.LATAM_LOCATIONS[country]
        
        logger.info(f"Scraping jobs for {len(target_locations)} countries")
        
        # Sample keywords (in production, you'd use all keywords)
        sample_keywords = self.JOB_KEYWORDS[:3]  # Use first 3 to avoid rate limiting
        
        for country, cities in target_locations.items():
            logger.info(f"\nProcessing {country}")
            
            # Use main city from each country
            main_city = cities[0]
            
            for keyword in sample_keywords:
                logger.info(f"  Searching: {keyword} in {main_city}")
                
                try:
                    jobs = self.search_linkedin_jobs(
                        keywords=keyword,
                        location=f"{main_city}, {country}",
                        max_results=max_per_location
                    )
                    
                    # Add location metadata
                    for job in jobs:
                        job['country'] = country
                        job['city'] = main_city
                        job['keywords'] = keyword
                    
                    all_jobs.extend(jobs)
                    
                    logger.info(f"    Found {len(jobs)} jobs")
                    
                    # Rate limiting (important!)
                    time.sleep(3)
                    
                except Exception as e:
                    logger.error(f"Error scraping {keyword} in {main_city}: {e}")
        
        # Remove duplicates
        unique_jobs = self._deduplicate_jobs(all_jobs)
        
        logger.info(f"\nTotal jobs scraped: {len(all_jobs)}")
        logger.info(f"Unique jobs: {len(unique_jobs)}")
        
        return unique_jobs
    
    def _deduplicate_jobs(self, jobs: List[Dict]) -> List[Dict]:
        """Remove duplicate jobs based on job_id."""
        seen_ids = set()
        unique_jobs = []
        
        for job in jobs:
            job_id = job.get('job_id')
            if job_id and job_id not in seen_ids:
                seen_ids.add(job_id)
                unique_jobs.append(job)
        
        return unique_jobs
    
    def push_to_supabase(self, jobs: List[Dict]) -> Dict:
        """
        Push scraped jobs to Supabase.
        
        Args:
            jobs: List of job dictionaries
        
        Returns:
            Result dictionary
        """
        if not jobs:
            logger.info("No jobs to push to Supabase")
            return {'success': True, 'count': 0}
        
        logger.info(f"Pushing {len(jobs)} jobs to Supabase")
        
        # Transform data for job_postings table
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
        
        # Insert into Supabase
        result = self.supabase.insert_job_postings(job_postings)
        
        logger.info(f"Successfully pushed jobs to Supabase: {result}")
        
        return result
    
    def _extract_company_from_title(self, title: str) -> Optional[str]:
        """Extract company name from job title."""
        # LinkedIn titles often format as: "Title - Company Name"
        if ' - ' in title:
            parts = title.split(' - ')
            if len(parts) >= 2:
                return parts[-1].strip()
        
        return None
    
    def save_to_file(self, jobs: List[Dict], output_path: str = None) -> None:
        """
        Save scraped jobs to JSON file.
        
        Args:
            jobs: List of job dictionaries
            output_path: Path to output file
        """
        if output_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = f"data/output/linkedin_jobs/linkedin_jobs_{timestamp}.json"
        
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(jobs, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Saved {len(jobs)} jobs to {output_path}")


# Main execution for GitHub Actions
if __name__ == "__main__":
    logger.info("="*60)
    logger.info("LinkedIn Jobs via Google Search - Starting")
    logger.info("="*60)
    
    # Initialize scraper
    scraper = LinkedInGoogleScraper()
    
    # Scrape LATAM jobs (Brazil and Mexico focus)
    jobs = scraper.scrape_latam_jobs(
        max_per_location=10,
        focus_countries=['Brazil', 'Mexico']
    )
    
    logger.info(f"\nScraped {len(jobs)} LinkedIn jobs")
    
    # Save to file
    scraper.save_to_file(jobs)
    
    # Push to Supabase
    if jobs:
        result = scraper.push_to_supabase(jobs)
        
        # Print summary
        print("\n" + "="*60)
        print("LINKEDIN SCRAPING SUMMARY")
        print("="*60)
        print(f"Total Jobs Scraped: {len(jobs)}")
        print(f"Jobs Added to Supabase: {result.get('count', 0)}")
        print("="*60)
        
        # Print sample jobs
        if jobs:
            print("\nSample Jobs:")
            for i, job in enumerate(jobs[:5], 1):
                print(f"\n{i}. {job.get('title')}")
                print(f"   Location: {job.get('city')}, {job.get('country')}")
                print(f"   Keywords: {job.get('keywords')}")
                print(f"   URL: {job.get('url')}")
    
    logger.info("LinkedIn scraper completed successfully")
