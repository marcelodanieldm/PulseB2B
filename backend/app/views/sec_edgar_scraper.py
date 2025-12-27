from fastapi import APIRouter, Query
from pydantic import BaseModel
from typing import List, Optional
from app.services.sec_edgar_scraper_service import SECFormDScraperService
import os

router = APIRouter()

class ScrapeRequest(BaseModel):
    ticker_symbols: Optional[List[str]] = None
    after_date: Optional[str] = None
    limit: Optional[int] = 100
    company_name: Optional[str] = os.getenv("SEC_COMPANY_NAME", "PulseB2B Market Intelligence")
    email: Optional[str] = os.getenv("SEC_CONTACT_EMAIL", "contact@pulseb2b.com")

@router.post("/scrape/sec-formd")
def scrape_sec_formd(request: ScrapeRequest):
    service = SECFormDScraperService(
        company_name=request.company_name,
        email=request.email
    )
    filings = service.scrape_recent_form_d(
        ticker_symbols=request.ticker_symbols,
        after_date=request.after_date,
        limit=request.limit
    )
    return {"filings": filings}

class ParseRequest(BaseModel):
    filing_path: str

@router.post("/parse/sec-formd")
def parse_sec_formd(request: ParseRequest):
    service = SECFormDScraperService(
        company_name=os.getenv("SEC_COMPANY_NAME", "PulseB2B Market Intelligence"),
        email=os.getenv("SEC_CONTACT_EMAIL", "contact@pulseb2b.com")
    )
    details = service.parse_form_d_details(request.filing_path)
    return details
