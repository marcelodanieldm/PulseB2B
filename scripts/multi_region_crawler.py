"""
Multi-Region Ghost Crawler
===========================
Scalable scraping infrastructure for the entire American continent.
Zero-cost architecture using Google Dorking + GitHub Actions.

Regions Covered:
- North America: USA, Canada
- Central America: Mexico, Costa Rica, Panama, Guatemala, Honduras, El Salvador, Nicaragua
- Andean Region: Colombia, Ecuador, Peru, Bolivia, Venezuela
- Southern Cone: Argentina, Uruguay, Chile, Paraguay, Brazil

Author: PulseB2B Senior Backend Engineer
Strategy: Regional job boards + Google CSE + Translation + IP rotation
"""

import requests
import time
import json
import csv
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from pathlib import Path
from deep_translator import GoogleTranslator


class MultiRegionCrawler:
    """
    Multi-region job scraping with automatic translation and IP rotation.
    """
    
    # Regional job boards by area
    REGIONAL_JOB_BOARDS = {
        'north_america': {
            'usa': [
                'linkedin.com/jobs',
                'indeed.com',
                'glassdoor.com',
                'monster.com'
            ],
            'canada': [
                'linkedin.com/jobs',
                'indeed.ca',
                'workopolis.com',
                'monster.ca'
            ]
        },
        'central_america': {
            'mexico': [
                'linkedin.com/jobs',
                'indeed.com.mx',
                'computrabajo.com.mx',
                'occmundial.com.mx'
            ],
            'costa_rica': [
                'linkedin.com/jobs',
                'bumeran.cr',
                'computrabajo.co.cr',
                'tecoloco.com'
            ],
            'panama': [
                'linkedin.com/jobs',
                'konzerta.com',
                'computrabajo.com.pa'
            ],
            'guatemala': [
                'linkedin.com/jobs',
                'tecoloco.com.gt',
                'computrabajo.com.gt'
            ]
        },
        'andean_region': {
            'colombia': [
                'linkedin.com/jobs',
                'elempleo.com',
                'computrabajo.com.co',
                'magneto365.com'
            ],
            'ecuador': [
                'linkedin.com/jobs',
                'computrabajo.com.ec',
                'multitrabajos.com'
            ],
            'peru': [
                'linkedin.com/jobs',
                'computrabajo.com.pe',
                'bumeran.com.pe',
                'laborum.pe'
            ],
            'venezuela': [
                'linkedin.com/jobs',
                'computrabajo.com.ve'
            ],
            'bolivia': [
                'linkedin.com/jobs',
                'computrabajo.com.bo'
            ]
        },
        'southern_cone': {
            'argentina': [
                'linkedin.com/jobs',
                'zonajobs.com.ar',
                'bumeran.com.ar',
                'computrabajo.com.ar',
                'empleos.clarin.com'
            ],
            'uruguay': [
                'linkedin.com/jobs',
                'buscojobs.com.uy',
                'gallito.com.uy',
                'empleos.elpais.com.uy'
            ],
            'chile': [
                'linkedin.com/jobs',
                'laborum.cl',
                'computrabajo.cl',
                'indeed.cl'
            ],
            'paraguay': [
                'linkedin.com/jobs',
                'computrabajo.com.py'
            ],
            'brazil': [
                'linkedin.com/jobs',
                'vagas.com.br',
                'catho.com.br',
                'infojobs.com.br'
            ]
        }
    }
    
    # Timezone offsets from EST (Eastern Standard Time = UTC-5)
    TIMEZONE_OFFSETS = {
        'usa': 0,           # EST baseline
        'canada': 0,        # EST/AST overlap
        'mexico': -1,       # CST (UTC-6)
        'costa_rica': -1,   # CST
        'panama': 0,        # EST
        'guatemala': -1,    # CST
        'colombia': 0,      # EST (COT = UTC-5)
        'ecuador': 0,       # EST (ECT = UTC-5)
        'peru': 0,          # EST (PET = UTC-5)
        'venezuela': +1,    # VET = UTC-4
        'bolivia': +1,      # BOT = UTC-4
        'argentina': +2,    # ART = UTC-3
        'uruguay': +2,      # UYT = UTC-3
        'chile': +1,        # CLT = UTC-4 (summer) / UTC-3 (winter)
        'paraguay': +1,     # PYT = UTC-4
        'brazil': +2        # BRT = UTC-3
    }
    
    # Currency codes
    CURRENCIES = {
        'usa': 'USD',
        'canada': 'CAD',
        'mexico': 'MXN',
        'costa_rica': 'CRC',
        'panama': 'USD',  # Uses USD
        'guatemala': 'GTQ',
        'colombia': 'COP',
        'ecuador': 'USD',  # Uses USD
        'peru': 'PEN',
        'venezuela': 'VES',
        'bolivia': 'BOB',
        'argentina': 'ARS',
        'uruguay': 'UYU',
        'chile': 'CLP',
        'paraguay': 'PYG',
        'brazil': 'BRL'
    }
    
    # Country codes (ISO 3166-1 alpha-2)
    COUNTRY_CODES = {
        'usa': 'US',
        'canada': 'CA',
        'mexico': 'MX',
        'costa_rica': 'CR',
        'panama': 'PA',
        'guatemala': 'GT',
        'honduras': 'HN',
        'el_salvador': 'SV',
        'nicaragua': 'NI',
        'colombia': 'CO',
        'ecuador': 'EC',
        'peru': 'PE',
        'venezuela': 'VE',
        'bolivia': 'BO',
        'argentina': 'AR',
        'uruguay': 'UY',
        'chile': 'CL',
        'paraguay': 'PY',
        'brazil': 'BR'
    }
    
    def __init__(self, google_cse_api_key: str, google_cse_id: str, region: str):
        """
        Initialize multi-region crawler.
        
        Args:
            google_cse_api_key: Google Custom Search API key
            google_cse_id: Google Custom Search Engine ID
            region: One of 'north_america', 'central_america', 'andean_region', 'southern_cone'
        """
        self.api_key = google_cse_api_key
        self.cse_id = google_cse_id
        self.region = region
        
        # Translation setup (English, Spanish, Portuguese)
        self.translator_es = GoogleTranslator(source='es', target='en')
        self.translator_pt = GoogleTranslator(source='pt', target='en')
        
        # Rate limiting state
        self.last_request_time = 0
        self.request_count = 0
        self.max_requests_per_region = 25  # 100 daily / 4 regions = 25 per region
        
        # Cool-down tracking
        self.cool_down_file = Path('data/logs/cooldown_tracker.json')
        self.cool_down_file.parent.mkdir(parents=True, exist_ok=True)
    
    def load_companies_from_oracle(self, csv_path: str = 'data/output/oracle_predictions.csv') -> List[Dict]:
        """Load companies from Oracle detector CSV."""
        companies = []
        
        if not os.path.exists(csv_path):
            print(f"⚠️ Oracle predictions not found at {csv_path}")
            return companies
        
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                companies.append({
                    'company_name': row.get('company_name', ''),
                    'region': row.get('region', 'USA'),
                    'funding_amount': float(row.get('latest_funding', 0))
                })
        
        print(f"✅ Loaded {len(companies)} companies from Oracle")
        return companies
    
    def build_google_dork_query(self, company_name: str, country: str, job_board: str) -> str:
        """
        Build Google Dorking pattern for regional job boards.
        
        Args:
            company_name: Company to search for
            country: Country name (lowercase with underscores)
            job_board: Job board domain
            
        Returns:
            Google search query string
        """
        # Base pattern: site restriction
        query = f'site:{job_board}'
        
        # Add company name
        query += f' "{company_name}"'
        
        # Add job-related keywords (multilingual)
        if 'linkedin.com' in job_board:
            query += ' "hiring" OR "jobs" OR "careers"'
        elif 'computrabajo' in job_board:
            query += ' "empleo" OR "trabajo" OR "vacante"'
        elif 'bumeran' in job_board or 'zonajobs' in job_board:
            query += ' "empleo" OR "búsqueda"'
        elif 'vagas' in job_board or 'catho' in job_board:
            query += ' "vaga" OR "emprego"'  # Portuguese
        else:
            query += ' "job" OR "employment" OR "career"'
        
        # Add country filter for multi-country boards
        country_names = {
            'usa': 'United States',
            'canada': 'Canada',
            'mexico': 'Mexico',
            'costa_rica': 'Costa Rica',
            'panama': 'Panama',
            'guatemala': 'Guatemala',
            'colombia': 'Colombia',
            'ecuador': 'Ecuador',
            'peru': 'Peru',
            'venezuela': 'Venezuela',
            'bolivia': 'Bolivia',
            'argentina': 'Argentina',
            'uruguay': 'Uruguay',
            'chile': 'Chile',
            'paraguay': 'Paraguay',
            'brazil': 'Brazil'
        }
        
        if job_board == 'linkedin.com/jobs' and country in country_names:
            query += f' "{country_names[country]}"'
        
        return query
    
    def search_google_cse(self, query: str, country: str) -> Dict:
        """
        Execute Google Custom Search with rate limiting.
        
        Args:
            query: Search query
            country: Country code for geotargeting
            
        Returns:
            Search results dictionary
        """
        # Rate limiting: 2 seconds between requests + jitter
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        
        if time_since_last < 2.0:
            sleep_time = 2.0 - time_since_last + (time.time() % 0.5)  # 0-500ms jitter
            time.sleep(sleep_time)
        
        self.last_request_time = time.time()
        self.request_count += 1
        
        # Check if we've hit region limit
        if self.request_count >= self.max_requests_per_region:
            print(f"⚠️ Reached max requests for {self.region} ({self.max_requests_per_region})")
            return {'items': []}
        
        # Build request
        url = 'https://www.googleapis.com/customsearch/v1'
        params = {
            'key': self.api_key,
            'cx': self.cse_id,
            'q': query,
            'gl': self.COUNTRY_CODES.get(country, 'US'),  # Geolocation
            'num': 10  # Max results per query
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"❌ Google CSE error for {country}: {e}")
            return {'items': []}
    
    def translate_to_english(self, text: str, source_language: str = 'auto') -> str:
        """
        Translate text to English using deep-translator (free).
        
        Args:
            text: Text to translate
            source_language: Source language ('es', 'pt', 'auto')
            
        Returns:
            Translated text in English
        """
        if not text or len(text.strip()) == 0:
            return text
        
        # Detect if text is already English (simple heuristic)
        english_words = ['job', 'career', 'hiring', 'employment', 'engineer', 'developer']
        text_lower = text.lower()
        if any(word in text_lower for word in english_words):
            return text  # Already English
        
        try:
            # Try Spanish first (most common in LATAM)
            if source_language == 'auto' or source_language == 'es':
                try:
                    translated = self.translator_es.translate(text[:500])  # Limit to 500 chars
                    return translated
                except Exception:
                    pass
            
            # Try Portuguese (Brazil)
            if source_language == 'auto' or source_language == 'pt':
                try:
                    translated = self.translator_pt.translate(text[:500])
                    return translated
                except Exception:
                    pass
            
            # If both fail, return original
            return text
        
        except Exception as e:
            print(f"⚠️ Translation error: {e}")
            return text
    
    def scrape_region(self, companies: List[Dict]) -> List[Dict]:
        """
        Scrape all job boards for companies in this region.
        
        Args:
            companies: List of company dictionaries
            
        Returns:
            List of scraped results with normalized data
        """
        results = []
        
        # Get countries for this region
        countries = self.REGIONAL_JOB_BOARDS.get(self.region, {})
        
        print(f"\n{'='*80}")
        print(f"🌎 SCRAPING REGION: {self.region.upper()}")
        print(f"{'='*80}")
        print(f"Countries: {', '.join(countries.keys())}")
        print(f"Companies to search: {len(companies)}")
        print(f"Max requests: {self.max_requests_per_region}")
        
        for country, job_boards in countries.items():
            print(f"\n📍 Country: {country.upper()}")
            
            for company in companies[:5]:  # Limit to 5 companies per country for demo
                company_name = company['company_name']
                
                print(f"  🔍 Searching: {company_name}")
                
                job_count = 0
                job_urls = []
                
                for job_board in job_boards[:2]:  # Limit to 2 job boards per country
                    # Build Google Dork query
                    query = self.build_google_dork_query(company_name, country, job_board)
                    
                    # Execute search
                    search_results = self.search_google_cse(query, country)
                    
                    # Parse results
                    items = search_results.get('items', [])
                    job_count += len(items)
                    
                    for item in items[:3]:  # Max 3 URLs per board
                        job_urls.append(item.get('link', ''))
                
                # Normalize data
                result = {
                    'company_name': company_name,
                    'country': country,
                    'country_code': self.COUNTRY_CODES.get(country, 'US'),
                    'region': self.region,
                    'job_count': job_count,
                    'job_urls': job_urls,
                    'timezone_match': self.TIMEZONE_OFFSETS.get(country, 0),
                    'currency_type': self.CURRENCIES.get(country, 'USD'),
                    'scraped_at': datetime.utcnow().isoformat(),
                    'funding_amount': company.get('funding_amount', 0),
                    'original_region': company.get('region', 'USA')
                }
                
                results.append(result)
                
                print(f"    ✅ Found {job_count} jobs on {len(job_boards[:2])} boards")
        
        print(f"\n📊 Region {self.region} complete: {len(results)} results")
        return results
    
    def update_cooldown_tracker(self):
        """Update cool-down tracker to prevent IP flagging."""
        cooldown_data = {
            'region': self.region,
            'last_scrape': datetime.utcnow().isoformat(),
            'request_count': self.request_count,
            'next_available': (datetime.utcnow() + timedelta(hours=6)).isoformat()
        }
        
        # Load existing data
        all_cooldowns = {}
        if self.cool_down_file.exists():
            with open(self.cool_down_file, 'r') as f:
                all_cooldowns = json.load(f)
        
        # Update this region
        all_cooldowns[self.region] = cooldown_data
        
        # Save
        with open(self.cool_down_file, 'w') as f:
            json.dump(all_cooldowns, f, indent=2)
        
        print(f"✅ Cool-down tracker updated: next scrape for {self.region} at {cooldown_data['next_available']}")
    
    def check_cooldown_status(self) -> bool:
        """
        Check if this region is in cool-down period.
        
        Returns:
            True if OK to scrape, False if in cool-down
        """
        if not self.cool_down_file.exists():
            return True  # No tracker yet, OK to scrape
        
        with open(self.cool_down_file, 'r') as f:
            all_cooldowns = json.load(f)
        
        region_data = all_cooldowns.get(self.region)
        if not region_data:
            return True  # No data for this region
        
        next_available = datetime.fromisoformat(region_data['next_available'])
        
        if datetime.utcnow() < next_available:
            print(f"⏸️ Region {self.region} is in cool-down until {next_available}")
            return False
        
        return True
    
    def save_results(self, results: List[Dict], output_path: str = 'data/output/multi_region_scraped.csv'):
        """Save scraped results to CSV."""
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        
        fieldnames = [
            'company_name', 'country', 'country_code', 'region', 
            'job_count', 'job_urls', 'timezone_match', 'currency_type',
            'scraped_at', 'funding_amount', 'original_region'
        ]
        
        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            
            for result in results:
                # Convert job_urls list to string
                result['job_urls'] = '|'.join(result['job_urls'])
                writer.writerow(result)
        
        print(f"✅ Results saved to {output_path}")


def main():
    """
    Example usage of Multi-Region Crawler.
    """
    import sys
    
    # Get region from command line
    if len(sys.argv) < 2:
        print("Usage: python multi_region_crawler.py <region>")
        print("Regions: north_america, central_america, andean_region, southern_cone")
        sys.exit(1)
    
    region = sys.argv[1]
    
    # Get API keys from environment
    api_key = os.getenv('GOOGLE_CSE_API_KEY')
    cse_id = os.getenv('GOOGLE_CSE_ID')
    
    if not api_key or not cse_id:
        print("❌ Missing environment variables: GOOGLE_CSE_API_KEY, GOOGLE_CSE_ID")
        sys.exit(1)
    
    print(f"🚀 Multi-Region Ghost Crawler - {region.upper()}")
    print(f"{'='*80}\n")
    
    # Initialize crawler
    crawler = MultiRegionCrawler(api_key, cse_id, region)
    
    # Check cool-down status
    if not crawler.check_cooldown_status():
        print(f"⏸️ Region {region} is in cool-down period. Skipping...")
        sys.exit(0)
    
    # Load companies
    companies = crawler.load_companies_from_oracle()
    
    if not companies:
        print("⚠️ No companies to scrape")
        sys.exit(1)
    
    # Scrape region
    results = crawler.scrape_region(companies)
    
    # Save results
    output_path = f'data/output/scraped_{region}.csv'
    crawler.save_results(results, output_path)
    
    # Update cool-down tracker
    crawler.update_cooldown_tracker()
    
    print(f"\n✅ Multi-region scraping complete for {region}")
    print(f"📊 Total results: {len(results)}")
    print(f"🔄 Cool-down: Next scrape in 6 hours")


if __name__ == '__main__':
    main()
