"""Supabase Client Service for Ghost Pipeline (FastAPI/MVC)."""

from typing import Dict, List, Optional
import os
import logging
from datetime import datetime
import requests

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SupabaseClient:
    def __init__(self, supabase_url: Optional[str] = None, supabase_key: Optional[str] = None):
        self.supabase_url = supabase_url or os.getenv('SUPABASE_URL')
        self.supabase_key = supabase_key or os.getenv('SUPABASE_KEY')
        self.mock_mode = False
        if not self.supabase_url or not self.supabase_key:
            logger.warning("Supabase credentials not found. Running in mock mode. No real DB operations will be performed.")
            self.mock_mode = True
        else:
            self.supabase_url = self.supabase_url.rstrip('/')
            self.api_url = f"{self.supabase_url}/rest/v1"
            self.headers = {
                'apikey': self.supabase_key,
                'Authorization': f'Bearer {self.supabase_key}',
                'Content-Type': 'application/json',
                'Prefer': 'return=representation'
            }
            logger.info(f"Initialized Supabase client: {self.supabase_url}")

    def insert(self, table: str, data: Dict | List[Dict], upsert: bool = False) -> Dict:
        if self.mock_mode:
            logger.info(f"[MOCK] Insert into {table}: {data}")
            return {'success': True, 'data': data, 'count': len(data) if isinstance(data, list) else 1}
        url = f"{self.api_url}/{table}"
        if isinstance(data, dict):
            data = [data]
        for item in data:
            if 'created_at' not in item:
                item['created_at'] = datetime.utcnow().isoformat()
        headers = self.headers.copy()
        if upsert:
            headers['Prefer'] = 'resolution=merge-duplicates'
        try:
            response = requests.post(url, json=data, headers=headers)
            response.raise_for_status()
            return {'success': True, 'data': response.json(), 'count': len(data)}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def select(self, table: str, columns: str = "*", filters: Optional[Dict] = None, limit: Optional[int] = None, order: Optional[str] = None) -> Dict:
        if self.mock_mode:
            logger.info(f"[MOCK] Select from {table} (columns={columns}, filters={filters}, limit={limit}, order={order})")
            return {'success': True, 'data': [], 'count': 0}
        url = f"{self.api_url}/{table}"
        params = {'select': columns}
        if filters:
            for key, value in filters.items():
                params[key] = value
        if limit:
            params['limit'] = limit
        if order:
            params['order'] = order
        try:
            response = requests.get(url, params=params, headers=self.headers)
            response.raise_for_status()
            data = response.json()
            return {'success': True, 'data': data, 'count': len(data)}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def update(self, table: str, data: Dict, filters: Dict) -> Dict:
        if self.mock_mode:
            logger.info(f"[MOCK] Update {table} where {filters} with {data}")
            return {'success': True, 'data': data}
        url = f"{self.api_url}/{table}"
        params = filters
        data['updated_at'] = datetime.utcnow().isoformat()
        try:
            response = requests.patch(url, json=data, params=params, headers=self.headers)
            response.raise_for_status()
            return {'success': True, 'data': response.json()}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def delete(self, table: str, filters: Dict) -> Dict:
        if self.mock_mode:
            logger.info(f"[MOCK] Delete from {table} where {filters}")
            return {'success': True}
        url = f"{self.api_url}/{table}"
        params = filters
        try:
            response = requests.delete(url, params=params, headers=self.headers)
            response.raise_for_status()
            return {'success': True}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def call_edge_function(self, function_name: str, payload: Dict) -> Dict:
        if self.mock_mode:
            logger.info(f"[MOCK] Call edge function {function_name} with {payload}")
            return {'success': True, 'data': {}}
        url = f"{self.supabase_url}/functions/v1/{function_name}"
        try:
            response = requests.post(url, json=payload, headers=self.headers)
            response.raise_for_status()
            return {'success': True, 'data': response.json()}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def insert_companies(self, companies: List[Dict]) -> Dict:
        return self.insert('companies', companies, upsert=True)
    def insert_funding_rounds(self, rounds: List[Dict]) -> Dict:
        return self.insert('funding_rounds', rounds, upsert=True)
    def insert_job_postings(self, jobs: List[Dict]) -> Dict:
        return self.insert('job_postings', jobs, upsert=True)
    def insert_news_articles(self, articles: List[Dict]) -> Dict:
        return self.insert('news_articles', articles, upsert=True)
    def insert_lead_scores(self, scores: List[Dict]) -> Dict:
        return self.insert('lead_scores', scores, upsert=True)
    def get_recent_companies(self, days: int = 7) -> Dict:
        return self.select('companies', filters={'created_at': f'gte.{datetime.utcnow().isoformat()}'}, order='created_at.desc', limit=100)
    def search_companies(self, query: str) -> Dict:
        return self.select('companies', filters={'company_name': f'ilike.%{query}%'}, limit=50)

# Singleton instance for use in services
supabase_client = SupabaseClient()
