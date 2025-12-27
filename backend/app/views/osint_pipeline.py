from fastapi import APIRouter, Body
from app.services.ghost_osint_pipeline import GhostOSINTPipeline
from typing import List, Dict

router = APIRouter()

@router.post("/scrape/osint-pipeline", response_model=List[Dict])
def run_osint_pipeline(companies: List[Dict] = Body(...)):
    pipeline = GhostOSINTPipeline()
    return pipeline.run_pipeline(companies)
