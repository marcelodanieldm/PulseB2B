import pytest
from app.services.sec_rss_scraper import SECRSSFeedScraper

def test_fetch_form_d_filings():
    scraper = SECRSSFeedScraper()
    filings = scraper.fetch_form_d_filings()
    assert isinstance(filings, list)
    if filings:
        assert "title" in filings[0]
