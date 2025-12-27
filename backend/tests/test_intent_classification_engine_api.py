
import sys
import os
import pytest
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_analyze_company_endpoint():
    payload = {
        "company_name": "Acme Corp",
        "company_description": "We are a fast-growing SaaS startup building remote-first solutions. Our distributed team spans across LATAM and EMEA timezones, and we're looking to scale our engineering organization globally. We recently raised our Series A and are expanding our global talent acquisition.",
        "funding_amount": 10000000,
        "funding_stage": "series_a"
    }
    response = client.post("/intent-engine/analyze-company", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "company_name" in data
    assert "recommendation" in data
    assert "global_hiring_score" in data

def test_market_scan_endpoint():
    payload = {
        "news_queries": [
            "tech startup series B funding",
            "SaaS company raises",
            "remote-first company hiring"
        ]
    }
    response = client.post("/intent-engine/market-scan", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "scan_timestamp" in data
    assert "summary" in data
