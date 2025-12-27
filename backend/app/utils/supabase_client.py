import os
import requests

class SupabaseClient:
    def __init__(self, url=None, key=None):
        self.url = url or os.getenv("SUPABASE_URL")
        self.key = key or os.getenv("SUPABASE_KEY")
        if not self.url or not self.key:
            raise ValueError("Supabase credentials required.")

    def push_lead_score(self, company, score):
        # Placeholder: implement real push to Supabase
        print(f"Pushing {company['name']} with score {score} to Supabase...")
        # Example: requests.post(f"{self.url}/rest/v1/lead_scores", ...)
