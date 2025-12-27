import pytest
from app.services.regional_economic_analyzer_service import regional_economic_analyzer

def test_arbitrage_basic():
    result = regional_economic_analyzer.calculate_arbitrage_potential(
        funding_amount=10000000,
        funding_region='USA',
        target_region='Colombia'
    )
    assert result['arbitrage_score'] > 0
    assert result['cost_savings'] > 0
    assert result['recommendation'] in ['CRITICAL: Expand immediately', 'Monitor opportunity']

def test_arbitrage_unknown_region():
    result = regional_economic_analyzer.calculate_arbitrage_potential(
        funding_amount=5000000,
        funding_region='USA',
        target_region='UnknownLand'
    )
    assert result['arbitrage_score'] == 0
    assert result['recommendation'] == 'Unknown region'
