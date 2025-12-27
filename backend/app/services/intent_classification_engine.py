from app.services.sec_rss_scraper import SECRSSFeedScraper
from app.services.osint_lead_scorer import OSINTLeadScorer
from app.services.intent_classifier import OutsourcingIntentClassifier
from app.services.global_hiring_score import GlobalHiringScoreCalculator
import logging

logger = logging.getLogger(__name__)

class IntentClassificationEngine:
    def __init__(self):
        self.sec_scraper = SECRSSFeedScraper()
        self.osint_scorer = OSINTLeadScorer()
        self.intent_classifier = OutsourcingIntentClassifier()
        self.ghs_calculator = GlobalHiringScoreCalculator()

    def run_pipeline(self, company):
        filings = self.sec_scraper.fetch_form_d_filings()
        score = self.osint_scorer.score_company(company)
        intent = self.intent_classifier.classify(company)
        ghs = self.ghs_calculator.calculate_ghs(company.get('funding', 0))
        return {
            "filings": filings,
            "score": score,
            "intent": intent,
            "ghs": ghs
        }
