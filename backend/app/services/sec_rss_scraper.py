import feedparser
import logging
from typing import List, Dict

logger = logging.getLogger(__name__)

class SECRSSFeedScraper:
    """
    Scraper for SEC.gov RSS feeds to get Form D filings.
    """
    SEC_FORM_D_FEED = "https://www.sec.gov/cgi-bin/browse-edgar?action=getcurrent&CIK=&type=D&company=&dateb=&owner=include&start=0&count=100&output=atom"

    def fetch_form_d_filings(self) -> List[Dict]:
        logger.info("Fetching SEC Form D filings from RSS feed...")
        feed = feedparser.parse(self.SEC_FORM_D_FEED)
        filings = []
        for entry in feed.entries:
            filings.append({
                "title": entry.get("title"),
                "link": entry.get("link"),
                "published": entry.get("published"),
                "summary": entry.get("summary"),
            })
        return filings
