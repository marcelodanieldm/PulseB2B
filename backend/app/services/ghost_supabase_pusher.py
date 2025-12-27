import os
from app.services.supabase_client import SupabaseClient

class GhostSupabasePusher:
    """Consolidates and pushes GitHub Actions artifacts to Supabase"""
    def __init__(self, supabase_url: str = None, supabase_key: str = None):
        self.supabase_url = supabase_url or os.getenv("SUPABASE_URL")
        self.supabase_key = supabase_key or os.getenv("SUPABASE_KEY")
        if not self.supabase_url or not self.supabase_key:
            raise ValueError("Supabase credentials required. Set SUPABASE_URL and SUPABASE_KEY env vars.")
        self.supabase = SupabaseClient(self.supabase_url, self.supabase_key)

    def push_artifacts(self, table: str, artifacts: list):
        for artifact in artifacts:
            self.supabase.insert(table, artifact)
