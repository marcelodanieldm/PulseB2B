import pytest
from app.services.telegram_teaser_generator import TelegramTeaserGenerator

def test_generate_teaser():
    generator = TelegramTeaserGenerator()
    company = {"name": "TestCo", "total_funding": 1000000, "hiring_probability": 80}
    teaser = generator.generate_teaser(company)
    assert "TestCo" in teaser
    assert "80" in teaser
