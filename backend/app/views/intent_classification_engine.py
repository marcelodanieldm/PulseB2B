"""FastAPI router for Intent Classification Engine endpoints."""

from fastapi import APIRouter, Body
from typing import Dict, Any, List, Optional
from ..services.intent_classification_engine_service import intent_classification_engine

router = APIRouter(prefix="/intent-engine", tags=["Intent Classification Engine"])

@router.post("/analyze-company", response_model=Dict[str, Any])
def analyze_company(payload: Dict[str, Any] = Body(...)):
    """Analyze a single company for intent, news, SEC, and hiring score."""
    return intent_classification_engine.analyze_company(
        company_ticker=payload.get("company_ticker"),
        company_name=payload.get("company_name"),
        company_description=payload.get("company_description"),
        funding_amount=payload.get("funding_amount"),
        funding_stage=payload.get("funding_stage", "series_a")
    )

@router.post("/market-scan", response_model=Dict[str, Any])
def market_scan(payload: Dict[str, Any] = Body(...)):
    """Run a market-wide scan for leads and intelligence."""
    return intent_classification_engine.run_market_scan(
        target_tickers=payload.get("target_tickers"),
        news_queries=payload.get("news_queries")
    )
