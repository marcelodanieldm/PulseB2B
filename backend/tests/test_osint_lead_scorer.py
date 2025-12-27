import pytest
from app.services.osint_lead_scorer import OSINTLeadScorer

def test_osint_lead_scorer():
    scorer = OSINTLeadScorer()
    company = {"name": "TestCo"}
    score = scorer.score_company(company)
    assert isinstance(score, float)
