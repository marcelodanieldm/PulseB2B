from fastapi import APIRouter, Body
from app.services.intent_classification_engine import IntentClassificationEngine
from typing import Dict

router = APIRouter()

@router.post("/analyze/intent", response_model=Dict)
def analyze_intent(company: Dict = Body(...)):
    engine = IntentClassificationEngine()
    return engine.run_pipeline(company)
