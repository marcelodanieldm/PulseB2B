import os
import requests
import logging
from typing import Optional

logger = logging.getLogger(__name__)

class SupabaseClient:
    def __init__(self, supabase_url: Optional[str] = None, supabase_key: Optional[str] = None):
        self.supabase_url = supabase_url or os.getenv("SUPABASE_URL")
        self.supabase_key = supabase_key or os.getenv("SUPABASE_KEY")
        if not self.supabase_url or not self.supabase_key:
            raise ValueError("Supabase credentials required.")
        self.headers = {
            "apikey": self.supabase_key,
            "Authorization": f"Bearer {self.supabase_key}",
            "Content-Type": "application/json"
        }

    def insert(self, table: str, data: dict):
        url = f"{self.supabase_url}/rest/v1/{table}"
        resp = requests.post(url, headers=self.headers, json=data)
        logger.info(f"Inserted into {table}: {resp.status_code}")
        return resp.json()

    def select(self, table: str, params: dict = None):
        url = f"{self.supabase_url}/rest/v1/{table}"
        resp = requests.get(url, headers=self.headers, params=params)
        logger.info(f"Selected from {table}: {resp.status_code}")
        return resp.json()
