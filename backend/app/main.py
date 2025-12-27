


from fastapi import FastAPI
from app.views.company import router as company_router
from app.views.linkedin_google_scraper import router as linkedin_jobs_router
from app.views import osint_lead_scorer
from app.views.sec_rss_scraper import router as sec_rss_router
from app.views.sec_edgar_scraper import router as sec_edgar_scraper_router
from app.views.osint_pipeline import router as osint_router
from app.views.web_scraper import router as web_scraper_router
from app.views.intent_classification import router as intent_router

from app.views.hpi_calculator import router as hpi_router
from app.views.global_hiring_score import router as ghs_router
from app.views.telegram_teaser import router as telegram_teaser_router
from app.views.intent_classification_engine import router as intent_engine_router


from app.tasks.scheduler import start_scheduler

app = FastAPI()

@app.on_event("startup")
def startup_event():
    start_scheduler()

@app.get("/")
def read_root():
    return {"message": "PulseB2B FastAPI backend running!"}

app.include_router(company_router)
app.include_router(linkedin_jobs_router)
app.include_router(sec_rss_router)
app.include_router(sec_edgar_scraper_router)
app.include_router(osint_router)
app.include_router(web_scraper_router)
app.include_router(intent_router)
app.include_router(hpi_router)
app.include_router(ghs_router)
app.include_router(telegram_teaser_router)
app.include_router(intent_engine_router)
app.include_router(osint_lead_scorer.router)
