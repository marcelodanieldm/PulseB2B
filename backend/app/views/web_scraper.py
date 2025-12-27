from fastapi import APIRouter, Query
from typing import List, Dict, Optional
from app.services.web_scraper_service import LinkedInScraper, FallbackDataEnricher

router = APIRouter(prefix="/web-scraper", tags=["Web Scraper"])

scraper = LinkedInScraper()

@router.get("/company", summary="Obtener datos de empresa en LinkedIn")
def get_company_data(
    company_name: str = Query(..., description="Nombre de la empresa"),
    country: Optional[str] = Query(None, description="País (opcional)")
):
    """Obtiene datos de LinkedIn para una empresa."""
    return scraper.get_company_data(company_name, country)

@router.post("/batch", summary="Extraer datos de varias empresas")
def batch_extract(companies: List[Dict]):
    """Extrae datos de LinkedIn para una lista de empresas."""
    return scraper.batch_extract(companies)

@router.get("/mock", summary="Generar datos mock de empleados por funding stage")
def generate_mock_data(
    company_name: str = Query(..., description="Nombre de la empresa"),
    funding_stage: str = Query(..., description="Etapa de funding (ej: Series A)"),
    funding_amount: Optional[float] = Query(None, description="Monto de funding (opcional)")
):
    """Genera datos mock de empleados según etapa de funding."""
    return FallbackDataEnricher.generate_mock_data(company_name, funding_stage, funding_amount)
