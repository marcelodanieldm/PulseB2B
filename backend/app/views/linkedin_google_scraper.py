from fastapi import APIRouter, Query
from typing import List, Optional
from app.services.linkedin_google_scraper_service import LinkedInGoogleScraper

router = APIRouter(prefix="/linkedin-google", tags=["LinkedIn Google Scraper"])

scraper = LinkedInGoogleScraper()

@router.get("/search", summary="Buscar empleos de LinkedIn usando Google")
def search_linkedin_jobs(
    keywords: str = Query("software engineer", description="Palabras clave del empleo"),
    location: str = Query("São Paulo", description="Ciudad o ubicación"),
    max_results: int = Query(10, description="Máximo de resultados")
):
    """Buscar empleos de LinkedIn usando Google Search scraping."""
    return scraper.search_linkedin_jobs(keywords=keywords, location=location, max_results=max_results)

@router.get("/latam", summary="Scrapear empleos de LinkedIn para LATAM")
def scrape_latam_jobs(
    max_per_location: int = Query(5, description="Máximo por ubicación"),
    focus_countries: Optional[List[str]] = Query(None, description="Países a enfocar (ej: Brazil, Mexico)")
):
    """Scrapear empleos de LinkedIn para ubicaciones LATAM."""
    return scraper.scrape_latam_jobs(max_per_location=max_per_location, focus_countries=focus_countries)
