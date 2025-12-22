"""
SEC EDGAR Form D Scraper for US Tech Market Intelligence
---------------------------------------------------------
This module scrapes new Form D filings from the SEC EDGAR system to detect
companies that have recently raised capital and may need to scale operations.

Form D filings indicate companies raising capital under Regulation D,
which often precedes hiring waves and outsourcing opportunities.
"""

import os
import json
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from pathlib import Path

try:
    from sec_edgar_downloader import Downloader
except ImportError:
    raise ImportError(
        "sec-edgar-downloader is required. Install it with: "
        "pip install sec-edgar-downloader"
    )

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class SECFormDScraper:
    """
    Scraper for SEC EDGAR Form D filings.
    
    Form D is filed by companies raising capital under Regulation D.
    These companies are prime candidates for outsourcing services as they
    scale operations after funding rounds.
    """
    
    def __init__(
        self,
        company_name: str,
        email: str,
        download_folder: str = "data/sec_filings"
    ):
        """
        Initialize the SEC EDGAR scraper.
        
        Args:
            company_name: Your company name (required by SEC)
            email: Your email address (required by SEC)
            download_folder: Where to store downloaded filings
        """
        self.company_name = company_name
        self.email = email
        self.download_folder = Path(download_folder)
        self.download_folder.mkdir(parents=True, exist_ok=True)
        
        # Initialize downloader with required identification
        self.downloader = Downloader(
            company_name=company_name,
            email_address=email,
            download_folder=str(self.download_folder)
        )
        
        logger.info(
            f"Initialized SEC EDGAR scraper. "
            f"Downloads will be stored in: {self.download_folder}"
        )
    
    def scrape_recent_form_d(
        self,
        ticker_symbols: Optional[List[str]] = None,
        after_date: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict]:
        """
        Scrape recent Form D filings.
        
        Args:
            ticker_symbols: List of company ticker symbols to monitor.
                           If None, will scrape most recent filings.
            after_date: Only get filings after this date (format: YYYY-MM-DD)
            limit: Maximum number of filings to download per company
        
        Returns:
            List of dictionaries containing filing metadata
        """
        filings = []
        
        if after_date is None:
            # Default to last 30 days
            after_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
        
        logger.info(f"Scraping Form D filings after {after_date}")
        
        if ticker_symbols:
            # Download for specific companies
            for ticker in ticker_symbols:
                try:
                    logger.info(f"Downloading Form D for {ticker}")
                    
                    # Download Form D filings
                    num_downloaded = self.downloader.get(
                        "D",  # Form D
                        ticker,
                        after=after_date,
                        limit=limit
                    )
                    
                    if num_downloaded > 0:
                        filing_info = self._extract_filing_metadata(ticker)
                        filings.extend(filing_info)
                        logger.info(
                            f"Downloaded {num_downloaded} Form D filings for {ticker}"
                        )
                    else:
                        logger.info(f"No Form D filings found for {ticker}")
                        
                except Exception as e:
                    logger.error(f"Error downloading Form D for {ticker}: {e}")
        else:
            logger.warning(
                "No ticker symbols provided. "
                "Please provide a list of companies to monitor."
            )
        
        return filings
    
    def _extract_filing_metadata(self, ticker: str) -> List[Dict]:
        """
        Extract metadata from downloaded Form D filings.
        
        Args:
            ticker: Company ticker symbol
        
        Returns:
            List of dictionaries with filing metadata
        """
        filings = []
        ticker_folder = self.download_folder / "sec-edgar-filings" / ticker / "D"
        
        if not ticker_folder.exists():
            return filings
        
        # Iterate through filing folders
        for filing_dir in ticker_folder.iterdir():
            if filing_dir.is_dir():
                # Look for the primary document
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
        """
        Parse Form D filing to extract key information.
        
        Args:
            filing_path: Path to the Form D filing directory
        
        Returns:
            Dictionary containing parsed Form D details
        """
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
        
        # Try to read the full submission text file
        full_submission = filing_dir / "full-submission.txt"
        if full_submission.exists():
            try:
                with open(full_submission, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    details["raw_text"] = content
                    
                    # Extract key information using simple text parsing
                    # Note: For production, use proper XML parsing
                    details.update(self._parse_form_d_text(content))
                    details["parsed"] = True
                    
            except Exception as e:
                logger.error(f"Error parsing Form D at {filing_path}: {e}")
        
        return details
    
    def _parse_form_d_text(self, content: str) -> Dict:
        """
        Parse Form D text content to extract key fields.
        
        This is a simplified parser. For production use,
        implement proper XML parsing of the primary-document.xml file.
        
        Args:
            content: Raw text content from Form D filing
        
        Returns:
            Dictionary with parsed fields
        """
        details = {}
        
        # These are simplified regex patterns
        # In production, use proper XML parsing
        import re
        
        # Extract company name
        name_match = re.search(r'COMPANY CONFORMED NAME:\s*(.+)', content)
        if name_match:
            details["company_name"] = name_match.group(1).strip()
        
        # Extract offering amount (simplified)
        amount_match = re.search(r'Total Offering Amount.*?(\d[\d,]+)', content, re.IGNORECASE)
        if amount_match:
            amount_str = amount_match.group(1).replace(',', '')
            try:
                details["total_offering_amount"] = float(amount_str)
            except ValueError:
                pass
        
        # Extract industry classification
        industry_match = re.search(r'STANDARD INDUSTRIAL CLASSIFICATION:.*?\[(\d+)\]', content)
        if industry_match:
            details["industry_code"] = industry_match.group(1)
        
        return details
    
    def save_filings_summary(
        self,
        filings: List[Dict],
        output_path: str = "data/output/form_d_filings.json"
    ) -> None:
        """
        Save scraped filings metadata to JSON file.
        
        Args:
            filings: List of filing dictionaries
            output_path: Path to output JSON file
        """
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(filings, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Saved {len(filings)} filings to {output_path}")


# Example usage and testing functions
def get_tech_company_tickers() -> List[str]:
    """
    Get a list of tech company tickers to monitor.
    
    Returns:
        List of ticker symbols for tech companies
    """
    # This is a starter list of major tech companies
    # In production, expand this based on your target market
    return [
        "AAPL", "MSFT", "GOOGL", "META", "AMZN",
        "NVDA", "TSLA", "NFLX", "ADBE", "CRM",
        "ORCL", "INTC", "AMD", "CSCO", "AVGO",
        "QCOM", "TXN", "SNOW", "PLTR", "DDOG"
    ]


if __name__ == "__main__":
    # Example usage
    scraper = SECFormDScraper(
        company_name="PulseB2B Market Intelligence",
        email="contact@pulseb2b.com"  # Replace with your actual email
    )
    
    # Get tech company tickers
    tech_tickers = get_tech_company_tickers()
    
    # Scrape recent Form D filings (last 90 days)
    after_date = (datetime.now() - timedelta(days=90)).strftime("%Y-%m-%d")
    
    logger.info(f"Starting Form D scrape for {len(tech_tickers)} companies")
    filings = scraper.scrape_recent_form_d(
        ticker_symbols=tech_tickers[:5],  # Start with first 5 for testing
        after_date=after_date,
        limit=10
    )
    
    # Parse details for each filing
    detailed_filings = []
    for filing in filings:
        details = scraper.parse_form_d_details(filing["filing_path"])
        filing.update(details)
        detailed_filings.append(filing)
    
    # Save results
    scraper.save_filings_summary(
        detailed_filings,
        "data/output/form_d_analysis/form_d_filings.json"
    )
    
    logger.info(f"Completed scraping. Found {len(detailed_filings)} Form D filings")
