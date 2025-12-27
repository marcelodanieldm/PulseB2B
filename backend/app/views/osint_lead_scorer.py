from fastapi import APIRouter, Query
from typing import List, Optional
from app.services.osint_lead_scorer_service import OSINTLeadScorer

router = APIRouter(prefix="/osint-leads", tags=["OSINT Leads"])

scorer = OSINTLeadScorer()

@router.get("/news", summary="Scrape tech news articles")
def get_tech_news(
    query: str = Query("tech startup funding OR hiring", description="Search query for news"),
    region: str = Query("US", description="Region code (US, EU, UK, etc.)"),
    period: str = Query("7d", description="Time period (e.g., 7d, 1m)"),
    max_results: int = Query(20, description="Maximum number of results")
):
    """Get tech news articles using GoogleNews."""
    return scorer.scrape_tech_news(query=query, region=region, period=period, max_results=max_results)

@router.get("/sentiment", summary="Analyze sentiment of text")
def analyze_sentiment(text: str = Query(..., description="Text to analyze")):
    """Analyze sentiment of the provided text."""
    return scorer.analyze_sentiment(text)

@router.post("/score-lead", summary="Score a single news article for lead potential")
def score_lead(article: dict):
    """Score a single news article for lead potential."""
    return scorer.score_article(article)

@router.get("/score-batch", summary="Scrape and score a batch of news articles")
def score_news_batch(
    query: str = Query("tech startup funding OR hiring", description="Search query for news"),
    regions: List[str] = Query(["US"], description="List of region codes"),
    period: str = Query("7d", description="Time period (e.g., 7d, 1m)"),
    max_results_per_region: int = Query(20, description="Max results per region"),
    min_score: int = Query(20, description="Minimum score to include")
):
    """Scrape and score a batch of news articles for lead potential."""
    return scorer.score_news_batch(
        query=query,
        regions=regions,
        period=period,
        max_results_per_region=max_results_per_region,
        min_score=min_score
    )
