import pytest
from app.services.global_hiring_score import GlobalHiringScoreCalculator, HiringUrgency

def test_ghs_urgency():
    calc = GlobalHiringScoreCalculator()
    assert calc.get_urgency(0.3) == HiringUrgency.CRITICAL
    assert calc.get_urgency(0.7) == HiringUrgency.HIGH
    assert calc.get_urgency(1.5) == HiringUrgency.MEDIUM
    assert calc.get_urgency(2.5) == HiringUrgency.LOW

def test_ghs_calculation():
    calc = GlobalHiringScoreCalculator()
    assert calc.calculate_ghs(140000, 140000) == 1.0
    assert calc.calculate_ghs(0, 140000) == 0.0
    assert calc.calculate_ghs(140000, 0) == 0.0
