
import sys
import os
import pytest
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app.services.hpi_calculator_service import HPICalculator

def test_hpi_recent():
    calc = HPICalculator()
    result = calc.calculate_funding_recency_score('2025-12-01')
    assert 'funding_recency_score' in result and 'recency_tier' in result

def test_hpi_invalid():
    calc = HPICalculator()
    result = calc.calculate_funding_recency_score('invalid-date')
    assert result['funding_recency_score'] == 0
    assert result['recency_tier'] == 'Unknown'
