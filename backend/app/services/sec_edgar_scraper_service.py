from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Optional
import logging
import json

try:
    from sec_edgar_downloader import Downloader
except ImportError:
    raise ImportError(
        "sec-edgar-downloader is required. Install it with: pip install sec-edgar-downloader"
    )

logger = logging.getLogger(__name__)

class SECFormDScraperService:
    def __init__(self, company_name: str, email: str, download_folder: str = "data/sec_filings"):
        self.company_name = company_name
        self.email = email
        self.download_folder = Path(download_folder)
        self.download_folder.mkdir(parents=True, exist_ok=True)
        self.downloader = Downloader(
            company_name=company_name,
            email_address=email,
            download_folder=str(self.download_folder)
        )

    def scrape_recent_form_d(self, ticker_symbols: Optional[List[str]] = None, after_date: Optional[str] = None, limit: int = 100) -> List[Dict]:
        """Download and extract recent Form D filings for given tickers."""
        filings = []
        if after_date is None:
            after_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
        if ticker_symbols:
            for ticker in ticker_symbols:
                try:
                    num_downloaded = self.downloader.get(
                        "D",
                        ticker,
                        after=after_date,
                        limit=limit
                    )
                    if num_downloaded > 0:
                        filing_info = self._extract_filing_metadata(ticker)
                        filings.extend(filing_info)
                except Exception as e:
                    logger.error(f"Error downloading Form D for {ticker}: {e}")
        return filings



    def _extract_filing_metadata(self, ticker: str) -> List[Dict]:
        filings = []
        ticker_folder = self.download_folder / "sec-edgar-filings" / ticker / "D"
        if not ticker_folder.exists():
            return filings
        for filing_dir in ticker_folder.iterdir():
            if filing_dir.is_dir():
                primary_doc = filing_dir / "primary-document.xml"
                full_submission = filing_dir / "full-submission.txt"
                if primary_doc.exists() or full_submission.exists():
                    filing_metadata = {
                        "ticker": ticker,
                        "form_type": "D",
                        "filing_date": filing_dir.name.split("-")[0] if "-" in filing_dir.name else filing_dir.name,
                        "accession_number": filing_dir.name,
                        "filing_path": str(filing_dir),
                        "primary_document_path": str(primary_doc) if primary_doc.exists() else None,
                        "full_submission_path": str(full_submission) if full_submission.exists() else None,
                        "scraped_at": datetime.now().isoformat()
                    }
                    filings.append(filing_metadata)
        return filings

    def parse_form_d_details(self, filing_path: str) -> Dict:
        filing_dir = Path(filing_path)
        details = {
            "parsed": False,
            "company_name": None,
            "total_offering_amount": None,
            "total_amount_sold": None,
            "total_remaining": None,
            "industry_group": None,
            "company_description": None,
            "date_first_sale": None,
            "raw_text": None
        }
        full_submission = filing_dir / "full-submission.txt"
        if full_submission.exists():
            try:
                with open(full_submission, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    details["raw_text"] = content
                    details.update(self._parse_form_d_text(content))
                    details["parsed"] = True
            except Exception as e:
                logger.error(f"Error parsing Form D at {filing_path}: {e}")
        return details

    def _parse_form_d_text(self, content: str) -> Dict:
        details = {}
        import re
        name_match = re.search(r'COMPANY CONFORMED NAME:\s*(.+)', content)
        if name_match:
            details["company_name"] = name_match.group(1).strip()
        amount_match = re.search(r'Total Offering Amount.*?(\d[\d,]+)', content, re.IGNORECASE)
        if amount_match:
            amount_str = amount_match.group(1).replace(',', '')
            try:
                details["total_offering_amount"] = float(amount_str)
            except ValueError:
                pass
        industry_match = re.search(r'STANDARD INDUSTRIAL CLASSIFICATION:.*?\[(\d+)\]', content)
        if industry_match:
            details["industry_code"] = industry_match.group(1)
        return details


sec_scraper = SECFormDScraperService(
    company_name="PulseB2B",
    email="contact@pulseb2b.com"
)
