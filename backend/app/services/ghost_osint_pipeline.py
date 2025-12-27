import os
from app.services.osint_lead_scorer import OSINTLeadScorer
from app.utils.supabase_client import SupabaseClient

class GhostOSINTPipeline:
    """Orchestrates OSINT lead scoring and pushes results to Supabase"""
    def __init__(self, supabase_url: str = None, supabase_key: str = None):
        self.supabase_url = supabase_url or os.getenv("SUPABASE_URL")
        self.supabase_key = supabase_key or os.getenv("SUPABASE_KEY")
        if not self.supabase_url or not self.supabase_key:
            raise ValueError("Supabase credentials required. Set SUPABASE_URL and SUPABASE_KEY env vars.")
        self.supabase = SupabaseClient(self.supabase_url, self.supabase_key)
        self.scorer = OSINTLeadScorer()

    def run_pipeline(self, companies):
        results = []
        for company in companies:
            score = self.scorer.score_company(company)
            self.supabase.push_lead_score(company, score)
            results.append({"company": company, "score": score})
        return results
