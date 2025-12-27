import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_news_endpoint():
    response = client.get("/osint-leads/news?query=tech+startup&region=US&period=7d&max_results=2")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_sentiment_endpoint():
    response = client.get("/osint-leads/sentiment?text=This+startup+is+growing+fast")
    assert response.status_code == 200
    assert "polarity" in response.json()

def test_score_lead_endpoint():
    article = {"title": "Startup X raises funding", "description": "Series A round"}
    response = client.post("/osint-leads/score-lead", json=article)
    assert response.status_code == 200
    assert "growth_score" in response.json()

def test_score_batch_endpoint():
    response = client.get("/osint-leads/score-batch?query=tech+startup&regions=US&period=7d&max_results_per_region=2&min_score=0")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
