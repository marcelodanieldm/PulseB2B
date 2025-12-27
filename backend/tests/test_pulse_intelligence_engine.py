import pytest
from app.services.pulse_intelligence_engine_service import pulse_intelligence_engine

def test_engine_init():
    assert hasattr(pulse_intelligence_engine, 'vectorizer')
    assert hasattr(pulse_intelligence_engine, 'scaler')

def test_weights_and_keywords():
    assert 'sec_funding' in pulse_intelligence_engine.WEIGHTS
    assert 'scaling' in pulse_intelligence_engine.EXPANSION_KEYWORDS
    assert 'layoffs' in pulse_intelligence_engine.NEGATIVE_KEYWORDS
