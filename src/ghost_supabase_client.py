"""
Supabase Client - REST API Integration for Ghost Pipeline
----------------------------------------------------------
Handles all interactions with Supabase (Postgres) database via REST API.
Designed for GitHub Actions serverless execution.
"""

import os
import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
import requests
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class SupabaseClient:
    """
    Client for interacting with Supabase via REST API.
    
    Supabase provides a PostgreSQL database with a RESTful API (PostgREST).
    This client abstracts all database operations for the Ghost Pipeline.
    """
    
    def __init__(
        self,
        supabase_url: Optional[str] = None,
        supabase_key: Optional[str] = None
    ):
        """
        Initialize Supabase client.
        
        Args:
            supabase_url: Supabase project URL (or set SUPABASE_URL env var)
            supabase_key: Supabase anon/service key (or set SUPABASE_KEY env var)
        """
        self.supabase_url = supabase_url or os.getenv('SUPABASE_URL')
        self.supabase_key = supabase_key or os.getenv('SUPABASE_KEY')
        
        if not self.supabase_url or not self.supabase_key:
            raise ValueError(
                "Supabase credentials not found. Set SUPABASE_URL and SUPABASE_KEY "
                "environment variables or pass them to the constructor."
            )
        
        # Remove trailing slash from URL
        self.supabase_url = self.supabase_url.rstrip('/')
        self.api_url = f"{self.supabase_url}/rest/v1"
        
        # Default headers for all requests
        self.headers = {
            'apikey': self.supabase_key,
            'Authorization': f'Bearer {self.supabase_key}',
            'Content-Type': 'application/json',
            'Prefer': 'return=representation'  # Return inserted/updated data
        }
        
        logger.info(f"Initialized Supabase client: {self.supabase_url}")
    
    def insert(
        self,
        table: str,
        data: Dict | List[Dict],
        upsert: bool = False
    ) -> Dict:
        """
        Insert data into a Supabase table.
        
        Args:
            table: Table name
            data: Dictionary or list of dictionaries to insert
            upsert: If True, use upsert (insert or update on conflict)
        
        Returns:
            Response dictionary with inserted data
        """
        url = f"{self.api_url}/{table}"
        
        # Ensure data is a list
        if isinstance(data, dict):
            data = [data]
        
        # Add timestamp if not present
        for item in data:
            if 'created_at' not in item:
                item['created_at'] = datetime.utcnow().isoformat()
        
        headers = self.headers.copy()
        if upsert:
            headers['Prefer'] = 'resolution=merge-duplicates'
        
        try:
            response = requests.post(url, json=data, headers=headers)
            response.raise_for_status()
            
            logger.info(f"Inserted {len(data)} records into {table}")
            return {
                'success': True,
                'data': response.json(),
                'count': len(data)
            }
            
        except requests.exceptions.HTTPError as e:
            logger.error(f"Failed to insert into {table}: {e}")
            logger.error(f"Response: {e.response.text}")
            return {
                'success': False,
                'error': str(e),
                'response': e.response.text
            }
        except Exception as e:
            logger.error(f"Unexpected error inserting into {table}: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def select(
        self,
        table: str,
        columns: str = "*",
        filters: Optional[Dict] = None,
        limit: Optional[int] = None,
        order: Optional[str] = None
    ) -> Dict:
        """
        Select data from a Supabase table.
        
        Args:
            table: Table name
            columns: Columns to select (default: "*")
            filters: Dictionary of filters (e.g., {'company_name': 'eq.Acme'})
            limit: Maximum number of rows to return
            order: Column to order by (e.g., 'created_at.desc')
        
        Returns:
            Response dictionary with selected data
        """
        url = f"{self.api_url}/{table}"
        params = {'select': columns}
        
        # Add filters
        if filters:
            for key, value in filters.items():
                params[key] = value
        
        # Add limit
        if limit:
            params['limit'] = limit
        
        # Add ordering
        if order:
            params['order'] = order
        
        try:
            response = requests.get(url, params=params, headers=self.headers)
            response.raise_for_status()
            
            data = response.json()
            logger.info(f"Selected {len(data)} records from {table}")
            
            return {
                'success': True,
                'data': data,
                'count': len(data)
            }
            
        except requests.exceptions.HTTPError as e:
            logger.error(f"Failed to select from {table}: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def update(
        self,
        table: str,
        data: Dict,
        filters: Dict
    ) -> Dict:
        """
        Update data in a Supabase table.
        
        Args:
            table: Table name
            data: Dictionary with fields to update
            filters: Dictionary of filters to identify rows
        
        Returns:
            Response dictionary
        """
        url = f"{self.api_url}/{table}"
        params = filters
        
        # Add updated_at timestamp
        data['updated_at'] = datetime.utcnow().isoformat()
        
        try:
            response = requests.patch(
                url,
                json=data,
                params=params,
                headers=self.headers
            )
            response.raise_for_status()
            
            logger.info(f"Updated records in {table}")
            return {
                'success': True,
                'data': response.json()
            }
            
        except requests.exceptions.HTTPError as e:
            logger.error(f"Failed to update {table}: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def delete(
        self,
        table: str,
        filters: Dict
    ) -> Dict:
        """
        Delete data from a Supabase table.
        
        Args:
            table: Table name
            filters: Dictionary of filters to identify rows to delete
        
        Returns:
            Response dictionary
        """
        url = f"{self.api_url}/{table}"
        params = filters
        
        try:
            response = requests.delete(url, params=params, headers=self.headers)
            response.raise_for_status()
            
            logger.info(f"Deleted records from {table}")
            return {
                'success': True
            }
            
        except requests.exceptions.HTTPError as e:
            logger.error(f"Failed to delete from {table}: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def call_edge_function(
        self,
        function_name: str,
        payload: Dict
    ) -> Dict:
        """
        Call a Supabase Edge Function.
        
        Args:
            function_name: Name of the edge function
            payload: Data to send to the function
        
        Returns:
            Response dictionary
        """
        url = f"{self.supabase_url}/functions/v1/{function_name}"
        
        try:
            response = requests.post(
                url,
                json=payload,
                headers=self.headers
            )
            response.raise_for_status()
            
            logger.info(f"Called edge function: {function_name}")
            return {
                'success': True,
                'data': response.json()
            }
            
        except requests.exceptions.HTTPError as e:
            logger.error(f"Failed to call edge function {function_name}: {e}")
            return {
                'success': False,
                'error': str(e),
                'response': e.response.text if e.response else None
            }
    
    # High-level methods for specific tables
    
    def insert_companies(self, companies: List[Dict]) -> Dict:
        """Insert company data into companies table."""
        return self.insert('companies', companies, upsert=True)
    
    def insert_funding_rounds(self, rounds: List[Dict]) -> Dict:
        """Insert funding rounds into funding_rounds table."""
        return self.insert('funding_rounds', rounds, upsert=True)
    
    def insert_job_postings(self, jobs: List[Dict]) -> Dict:
        """Insert job postings into job_postings table."""
        return self.insert('job_postings', jobs, upsert=True)
    
    def insert_news_articles(self, articles: List[Dict]) -> Dict:
        """Insert news articles into news_articles table."""
        return self.insert('news_articles', articles, upsert=True)
    
    def insert_lead_scores(self, scores: List[Dict]) -> Dict:
        """Insert lead scores into lead_scores table."""
        return self.insert('lead_scores', scores, upsert=True)
    
    def get_recent_companies(self, days: int = 7) -> Dict:
        """Get companies added in the last N days."""
        return self.select(
            'companies',
            filters={'created_at': f'gte.{datetime.utcnow().isoformat()}'},
            order='created_at.desc',
            limit=100
        )
    
    def search_companies(self, query: str) -> Dict:
        """Search companies by name."""
        return self.select(
            'companies',
            filters={'company_name': f'ilike.%{query}%'},
            limit=50
        )


# Helper function for batch operations
def batch_insert(
    client: SupabaseClient,
    table: str,
    data: List[Dict],
    batch_size: int = 100
) -> Dict:
    """
    Insert data in batches to avoid request size limits.
    
    Args:
        client: SupabaseClient instance
        table: Table name
        data: List of dictionaries to insert
        batch_size: Number of records per batch
    
    Returns:
        Summary dictionary
    """
    total = len(data)
    batches = [data[i:i + batch_size] for i in range(0, total, batch_size)]
    
    results = {
        'total_records': total,
        'batches': len(batches),
        'successful': 0,
        'failed': 0,
        'errors': []
    }
    
    for i, batch in enumerate(batches, 1):
        logger.info(f"Inserting batch {i}/{len(batches)} ({len(batch)} records)")
        
        result = client.insert(table, batch)
        
        if result['success']:
            results['successful'] += len(batch)
        else:
            results['failed'] += len(batch)
            results['errors'].append(result.get('error'))
    
    logger.info(
        f"Batch insert complete: {results['successful']}/{total} successful, "
        f"{results['failed']} failed"
    )
    
    return results


# Example usage
if __name__ == "__main__":
    # Initialize client
    client = SupabaseClient()
    
    # Example: Insert company data
    test_company = {
        'company_name': 'Test Corp',
        'industry': 'Technology',
        'country': 'US',
        'funding_amount': 10000000,
        'funding_stage': 'Series A',
        'employee_count': 50,
        'website': 'https://testcorp.com'
    }
    
    result = client.insert_companies([test_company])
    print(f"Insert result: {result}")
    
    # Example: Search companies
    search_result = client.search_companies('Test')
    print(f"Search result: {search_result}")
