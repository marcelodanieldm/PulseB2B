import pytest
from app.services.web_scraper import LinkedInScraper

def test_search_company_linkedin():
    scraper = LinkedInScraper()
    url = scraper.search_company_linkedin("Google")
    assert url is None or isinstance(url, str)
