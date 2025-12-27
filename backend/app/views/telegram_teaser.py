from fastapi import APIRouter, Body
from app.services.telegram_teaser_generator import TelegramTeaserGenerator
from typing import Dict

router = APIRouter()

@router.post("/generate/telegram-teaser", response_model=Dict)
def generate_teaser(company: Dict = Body(...)):
    generator = TelegramTeaserGenerator()
    return {"teaser": generator.generate_teaser(company)}
