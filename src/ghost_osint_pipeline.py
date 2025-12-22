"""
Ghost OSINT Pipeline Orchestrator
Integrates OSINT Lead Scorer with Supabase for automated market intelligence
"""

import os
import sys
from datetime import datetime
from typing import Dict, List, Optional
import json

# Import internal modules
try:
    from osint_lead_scorer import OSINTLeadScorer
    from ghost_supabase_client import GhostSupabaseClient
except ImportError:
    print("WARNING: Could not import all modules. Attempting relative imports...")
    from src.osint_lead_scorer import OSINTLeadScorer
    from src.ghost_supabase_client import GhostSupabaseClient


class GhostOSINTPipeline:
    """Orchestrates OSINT lead scoring and pushes results to Supabase"""
    
    def __init__(self, supabase_url: str = None, supabase_key: str = None):
        """
        Initialize Ghost OSINT Pipeline
        
        Args:
            supabase_url: Supabase project URL (defaults to env var SUPABASE_URL)
            supabase_key: Supabase service role key (defaults to env var SUPABASE_KEY)
        """
        self.supabase_url = supabase_url or os.getenv("SUPABASE_URL")
        self.supabase_key = supabase_key or os.getenv("SUPABASE_KEY")
        
        if not self.supabase_url or not self.supabase_key:
            raise ValueError("Supabase credentials required. Set SUPABASE_URL and SUPABASE_KEY env vars.")
        
        # Initialize clients
        self.scorer = OSINTLeadScorer()
        self.supabase = GhostSupabaseClient(self.supabase_url, self.supabase_key)
        
        print(f"✅ Ghost OSINT Pipeline initialized")
        print(f"   Supabase: {self.supabase_url[:30]}...")
    
    def run_market_scan(
        self,
        company_names: List[str],
        days_lookback: int = 30
    ) -> Dict:
        """
        Run OSINT lead scoring on a list of companies
        
        Args:
            company_names: List of company names to analyze
            days_lookback: Days of news history to analyze
            
        Returns:
            Dict with pipeline results and statistics
        """
        run_id = self._start_pipeline_run("osint_market_scan")
        
        results = {
            "run_id": run_id,
            "started_at": datetime.utcnow().isoformat(),
            "companies_analyzed": 0,
            "news_articles_found": 0,
            "news_articles_inserted": 0,
            "lead_scores_updated": 0,
            "errors": []
        }
        
        try:
            print(f"\n🔍 Starting market scan for {len(company_names)} companies...")
            print(f"   Lookback period: {days_lookback} days")
            
            # Batch process companies
            batch_size = 10
            for i in range(0, len(company_names), batch_size):
                batch = company_names[i:i+batch_size]
                print(f"\n📊 Processing batch {i//batch_size + 1} ({len(batch)} companies)...")
                
                # Score companies
                scores = self.scorer.score_news_batch(batch, days_lookback=days_lookback)
                
                for company_name, score_data in scores.items():
                    try:
                        # Insert news articles
                        news_inserted = self._insert_news_articles(
                            company_name,
                            score_data.get("news", [])
                        )
                        results["news_articles_found"] += len(score_data.get("news", []))
                        results["news_articles_inserted"] += news_inserted
                        
                        # Upsert lead score
                        lead_score_data = self._prepare_lead_score(company_name, score_data)
                        self.supabase.upsert("lead_scores", lead_score_data)
                        results["lead_scores_updated"] += 1
                        
                        # Update company metadata if needed
                        self._upsert_company_metadata(company_name, score_data)
                        
                        results["companies_analyzed"] += 1
                        
                    except Exception as e:
                        error_msg = f"Error processing {company_name}: {str(e)}"
                        print(f"   ⚠️  {error_msg}")
                        results["errors"].append(error_msg)
            
            # Mark pipeline run as completed
            results["completed_at"] = datetime.utcnow().isoformat()
            self._complete_pipeline_run(
                run_id,
                status="completed",
                records_processed=len(company_names),
                records_inserted=results["lead_scores_updated"]
            )
            
            print(f"\n✅ Market scan completed!")
            print(f"   Companies analyzed: {results['companies_analyzed']}")
            print(f"   News articles inserted: {results['news_articles_inserted']}")
            print(f"   Lead scores updated: {results['lead_scores_updated']}")
            
            if results["errors"]:
                print(f"   ⚠️  Errors: {len(results['errors'])}")
            
            return results
            
        except Exception as e:
            # Mark pipeline run as failed
            self._complete_pipeline_run(
                run_id,
                status="failed",
                error_message=str(e)
            )
            print(f"\n❌ Market scan failed: {str(e)}")
            raise
    
    def _insert_news_articles(self, company_name: str, news_items: List[Dict]) -> int:
        """Insert news articles for a company (skip duplicates)"""
        if not news_items:
            return 0
        
        inserted = 0
        for news in news_items:
            try:
                article_data = {
                    "company_name": company_name,
                    "title": news.get("title"),
                    "description": news.get("summary"),
                    "article_url": news.get("url"),
                    "published_date": news.get("published"),
                    "source": "googlenews",
                    "event_type": self._classify_event_type(news.get("title", "")),
                    "sentiment_score": news.get("sentiment", 0)
                }
                
                # Insert (will skip if duplicate URL)
                self.supabase.insert("news_articles", [article_data])
                inserted += 1
                
            except Exception as e:
                # Skip duplicate articles
                if "duplicate key" in str(e).lower():
                    continue
                else:
                    print(f"   Warning: Could not insert article: {str(e)}")
        
        return inserted
    
    def _prepare_lead_score(self, company_name: str, score_data: Dict) -> Dict:
        """Prepare lead score data for Supabase"""
        score = score_data.get("score", 0)
        
        # Determine priority
        if score >= 80:
            priority = "critical"
        elif score >= 60:
            priority = "high"
        elif score >= 40:
            priority = "medium"
        else:
            priority = "low"
        
        # Extract scoring factors
        factors = []
        breakdown = score_data.get("breakdown", {})
        for key, value in breakdown.items():
            if value != 0:
                factors.append(f"{key}: {value:+d} points")
        
        return {
            "company_name": company_name,
            "score": score,
            "priority": priority,
            "factors": factors,
            "trigger_type": "osint_news_scan",
            "calculated_at": datetime.utcnow().isoformat()
        }
    
    def _upsert_company_metadata(self, company_name: str, score_data: Dict):
        """Upsert company metadata (optional enrichment)"""
        try:
            company_data = {
                "company_name": company_name,
                "data_source": "osint_pipeline"
            }
            self.supabase.upsert("companies", company_data)
        except Exception as e:
            # Non-critical, just log
            print(f"   Note: Could not upsert company metadata: {str(e)}")
    
    def _classify_event_type(self, title: str) -> str:
        """Classify news event type from title"""
        title_lower = title.lower()
        
        if any(word in title_lower for word in ["series a", "series b", "series c", "funding", "raises", "raised"]):
            return "funding"
        elif any(word in title_lower for word in ["expansion", "expanding", "opens", "office"]):
            return "expansion"
        elif any(word in title_lower for word in ["layoff", "cuts", "downsiz"]):
            return "layoffs"
        elif any(word in title_lower for word in ["bankrupt", "shutdown", "closes"]):
            return "negative"
        elif any(word in title_lower for word in ["hiring", "jobs", "recrui"]):
            return "hiring"
        else:
            return "general"
    
    def _start_pipeline_run(self, pipeline_type: str) -> str:
        """Start pipeline run tracking"""
        data = {
            "pipeline_type": pipeline_type,
            "status": "running",
            "started_at": datetime.utcnow().isoformat()
        }
        result = self.supabase.insert("pipeline_runs", [data])
        return result[0].get("id") if result else None
    
    def _complete_pipeline_run(
        self,
        run_id: str,
        status: str,
        records_processed: int = 0,
        records_inserted: int = 0,
        error_message: str = None
    ):
        """Complete pipeline run tracking"""
        update_data = {
            "status": status,
            "completed_at": datetime.utcnow().isoformat(),
            "records_processed": records_processed,
            "records_inserted": records_inserted
        }
        
        if error_message:
            update_data["error_message"] = error_message
        
        self.supabase.update(
            "pipeline_runs",
            update_data,
            filters={"id": f"eq.{run_id}"}
        )


def main():
    """Example usage"""
    
    # Example: Scan US tech companies for hiring signals
    companies = [
        "OpenAI",
        "Anthropic",
        "Perplexity AI",
        "Scale AI",
        "Databricks",
        "Snowflake",
        "Stripe",
        "Figma",
        "Notion",
        "Airtable"
    ]
    
    pipeline = GhostOSINTPipeline()
    results = pipeline.run_market_scan(companies, days_lookback=30)
    
    # Print results
    print("\n" + "="*60)
    print("PIPELINE RESULTS")
    print("="*60)
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
