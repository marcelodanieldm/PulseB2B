from apscheduler.schedulers.background import BackgroundScheduler
from app.services.linkedin_google_scraper import LinkedInGoogleScraper
from app.services.sec_rss_scraper import SECRSSFeedScraper
import logging

logger = logging.getLogger(__name__)

scheduler = BackgroundScheduler()

# Example: scrape LinkedIn jobs every day at 2am
@scheduler.scheduled_job('cron', hour=2)
def scheduled_linkedin_scrape():
    scraper = LinkedInGoogleScraper()
    for country, cities in scraper.LATAM_LOCATIONS.items():
        for city in cities:
            for keyword in scraper.JOB_KEYWORDS:
                jobs = scraper.search_linkedin_jobs(keyword, city, max_results=5)
                logger.info(f"Scraped {len(jobs)} jobs for {keyword} in {city}")

# Example: fetch SEC Form D filings every day at 3am
@scheduler.scheduled_job('cron', hour=3)
def scheduled_sec_scrape():
    scraper = SECRSSFeedScraper()
    filings = scraper.fetch_form_d_filings()
    logger.info(f"Fetched {len(filings)} SEC Form D filings")

def start_scheduler():
    scheduler.start()
