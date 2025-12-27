from fastapi import APIRouter, Query
from typing import Optional
from app.services.sec_rss_scraper_service import SECRSSFeedScraper

router = APIRouter(prefix="/sec-rss", tags=["SEC RSS Scraper"])

scraper = SECRSSFeedScraper()

@router.get("/form-d", summary="Scrape SEC Form D RSS feed")
def scrape_form_d(
    max_items: int = Query(100, description="Maximum number of items to process"),
    days_back: int = Query(1, description="Days back to include filings")
):
    """Scrape the SEC Form D RSS feed for recent filings."""
    return scraper.scrape_form_d_feed(max_items=max_items, days_back=days_back)
