
import pytest
from app.services.linkedin_google_scraper import LinkedInGoogleScraper
from dotenv import load_dotenv
import os

# Cargar variables de entorno desde .env automáticamente
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

def test_search_linkedin_jobs():
    scraper = LinkedInGoogleScraper()
    results = scraper.search_linkedin_jobs("python developer", "São Paulo", max_results=1)
    assert isinstance(results, list)
    assert all("url" in r for r in results)
