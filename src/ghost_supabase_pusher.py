"""
Ghost Supabase Data Consolidation Pusher
Consolidates artifacts from GitHub Actions jobs and batch inserts to Supabase
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
import argparse

# Import internal modules
try:
    from ghost_supabase_client import GhostSupabaseClient
except ImportError:
    from src.ghost_supabase_client import GhostSupabaseClient


class GhostSupabasePusher:
    """Consolidates and pushes GitHub Actions artifacts to Supabase"""
    
    def __init__(self, supabase_url: str = None, supabase_key: str = None):
        """
        Initialize Ghost Supabase Pusher
        
        Args:
            supabase_url: Supabase project URL (defaults to env var SUPABASE_URL)
            supabase_key: Supabase service role key (defaults to env var SUPABASE_KEY)
        """
        self.supabase_url = supabase_url or os.getenv("SUPABASE_URL")
        self.supabase_key = supabase_key or os.getenv("SUPABASE_KEY")
        
        if not self.supabase_url or not self.supabase_key:
            raise ValueError("Supabase credentials required. Set SUPABASE_URL and SUPABASE_KEY env vars.")
        
        self.supabase = GhostSupabaseClient(self.supabase_url, self.supabase_key)
        
        print(f"✅ Ghost Supabase Pusher initialized")
        print(f"   Supabase: {self.supabase_url[:30]}...")
    
    def push_artifacts(self, artifacts_dir: str) -> Dict:
        """
        Push all artifacts from GitHub Actions to Supabase
        
        Args:
            artifacts_dir: Directory containing JSON artifacts from each job
            
        Returns:
            Dict with push statistics
        """
        artifacts_path = Path(artifacts_dir)
        
        if not artifacts_path.exists():
            raise FileNotFoundError(f"Artifacts directory not found: {artifacts_dir}")
        
        stats = {
            "started_at": datetime.utcnow().isoformat(),
            "companies_inserted": 0,
            "funding_rounds_inserted": 0,
            "job_postings_inserted": 0,
            "news_articles_inserted": 0,
            "lead_scores_inserted": 0,
            "errors": []
        }
        
        print(f"\n📦 Processing artifacts from: {artifacts_dir}")
        
        try:
            # 1. Push SEC funding data
            sec_file = artifacts_path / "sec_funding.json"
            if sec_file.exists():
                print("\n💰 Pushing SEC funding data...")
                sec_stats = self._push_sec_funding(sec_file)
                stats["companies_inserted"] += sec_stats.get("companies", 0)
                stats["funding_rounds_inserted"] += sec_stats.get("funding_rounds", 0)
            
            # 2. Push LinkedIn jobs data
            jobs_file = artifacts_path / "linkedin_jobs.json"
            if jobs_file.exists():
                print("\n💼 Pushing LinkedIn jobs data...")
                jobs_stats = self._push_jobs(jobs_file)
                stats["job_postings_inserted"] += jobs_stats.get("jobs", 0)
            
            # 3. Push news/OSINT data
            news_file = artifacts_path / "osint_news.json"
            if news_file.exists():
                print("\n📰 Pushing OSINT news data...")
                news_stats = self._push_news(news_file)
                stats["news_articles_inserted"] += news_stats.get("articles", 0)
            
            # 4. Push lead scores
            scores_file = artifacts_path / "lead_scores.json"
            if scores_file.exists():
                print("\n📊 Pushing lead scores...")
                scores_stats = self._push_lead_scores(scores_file)
                stats["lead_scores_inserted"] += scores_stats.get("scores", 0)
            
            stats["completed_at"] = datetime.utcnow().isoformat()
            
            print(f"\n✅ All artifacts pushed successfully!")
            self._print_stats(stats)
            
            return stats
            
        except Exception as e:
            error_msg = f"Error pushing artifacts: {str(e)}"
            print(f"\n❌ {error_msg}")
            stats["errors"].append(error_msg)
            raise
    
    def _push_sec_funding(self, file_path: Path) -> Dict:
        """Push SEC funding data"""
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        companies_inserted = 0
        funding_rounds_inserted = 0
        
        for item in data:
            try:
                # Insert company
                company_data = {
                    "company_name": item.get("company_name"),
                    "sec_cik": item.get("cik"),
                    "data_source": "sec_edgar",
                    "country": "United States"
                }
                self.supabase.upsert("companies", company_data)
                companies_inserted += 1
                
                # Insert funding round
                funding_data = {
                    "company_name": item.get("company_name"),
                    "funding_type": item.get("offering_type", "Form D"),
                    "amount_usd": item.get("amount_usd"),
                    "announced_date": item.get("filed_date"),
                    "source_url": item.get("edgar_url"),
                    "sec_accession_number": item.get("accession_number")
                }
                self.supabase.insert("funding_rounds", [funding_data])
                funding_rounds_inserted += 1
                
            except Exception as e:
                print(f"   ⚠️  Error inserting SEC data: {str(e)}")
        
        print(f"   ✅ Companies: {companies_inserted}, Funding rounds: {funding_rounds_inserted}")
        return {"companies": companies_inserted, "funding_rounds": funding_rounds_inserted}
    
    def _push_jobs(self, file_path: Path) -> Dict:
        """Push LinkedIn jobs data"""
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        jobs_inserted = 0
        batch = []
        
        for item in data:
            try:
                job_data = {
                    "job_id": item.get("job_id"),
                    "company_name": item.get("company"),
                    "title": item.get("title"),
                    "description": item.get("description"),
                    "location": item.get("location"),
                    "country": item.get("country", "Brazil"),
                    "job_url": item.get("url"),
                    "source": "linkedin_google",
                    "keywords": item.get("keywords"),
                    "remote_allowed": item.get("remote", False),
                    "posted_date": item.get("posted_date")
                }
                batch.append(job_data)
                
                # Batch insert every 50 records
                if len(batch) >= 50:
                    self.supabase.insert("job_postings", batch)
                    jobs_inserted += len(batch)
                    batch = []
                    
            except Exception as e:
                print(f"   ⚠️  Error preparing job data: {str(e)}")
        
        # Insert remaining batch
        if batch:
            self.supabase.insert("job_postings", batch)
            jobs_inserted += len(batch)
        
        print(f"   ✅ Jobs inserted: {jobs_inserted}")
        return {"jobs": jobs_inserted}
    
    def _push_news(self, file_path: Path) -> Dict:
        """Push OSINT news data"""
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        articles_inserted = 0
        batch = []
        
        for item in data:
            try:
                article_data = {
                    "company_name": item.get("company"),
                    "title": item.get("title"),
                    "description": item.get("summary"),
                    "article_url": item.get("url"),
                    "published_date": item.get("published"),
                    "source": item.get("source", "googlenews"),
                    "event_type": item.get("event_type", "general"),
                    "sentiment_score": item.get("sentiment", 0)
                }
                batch.append(article_data)
                
                # Batch insert every 50 records
                if len(batch) >= 50:
                    self.supabase.insert("news_articles", batch)
                    articles_inserted += len(batch)
                    batch = []
                    
            except Exception as e:
                # Skip duplicates
                if "duplicate key" not in str(e).lower():
                    print(f"   ⚠️  Error preparing news data: {str(e)}")
        
        # Insert remaining batch
        if batch:
            try:
                self.supabase.insert("news_articles", batch)
                articles_inserted += len(batch)
            except:
                pass
        
        print(f"   ✅ Articles inserted: {articles_inserted}")
        return {"articles": articles_inserted}
    
    def _push_lead_scores(self, file_path: Path) -> Dict:
        """Push lead scores"""
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        scores_inserted = 0
        
        for item in data:
            try:
                score_data = {
                    "company_name": item.get("company"),
                    "score": item.get("score"),
                    "priority": item.get("priority"),
                    "factors": item.get("factors", []),
                    "trigger_type": item.get("trigger_type", "github_actions"),
                    "calculated_at": datetime.utcnow().isoformat()
                }
                self.supabase.upsert("lead_scores", score_data)
                scores_inserted += 1
                
            except Exception as e:
                print(f"   ⚠️  Error inserting lead score: {str(e)}")
        
        print(f"   ✅ Lead scores inserted: {scores_inserted}")
        return {"scores": scores_inserted}
    
    def _print_stats(self, stats: Dict):
        """Print push statistics"""
        print("\n" + "="*60)
        print("PUSH STATISTICS")
        print("="*60)
        print(f"Companies:       {stats['companies_inserted']}")
        print(f"Funding Rounds:  {stats['funding_rounds_inserted']}")
        print(f"Job Postings:    {stats['job_postings_inserted']}")
        print(f"News Articles:   {stats['news_articles_inserted']}")
        print(f"Lead Scores:     {stats['lead_scores_inserted']}")
        
        if stats["errors"]:
            print(f"\n⚠️  Errors:        {len(stats['errors'])}")
            for error in stats["errors"][:5]:  # Show first 5 errors
                print(f"   - {error}")


def main():
    """CLI entry point"""
    parser = argparse.ArgumentParser(
        description="Push GitHub Actions artifacts to Supabase"
    )
    parser.add_argument(
        "artifacts_dir",
        help="Directory containing JSON artifact files"
    )
    parser.add_argument(
        "--supabase-url",
        help="Supabase URL (default: SUPABASE_URL env var)"
    )
    parser.add_argument(
        "--supabase-key",
        help="Supabase service role key (default: SUPABASE_KEY env var)"
    )
    
    args = parser.parse_args()
    
    pusher = GhostSupabasePusher(
        supabase_url=args.supabase_url,
        supabase_key=args.supabase_key
    )
    
    results = pusher.push_artifacts(args.artifacts_dir)
    
    # Exit with error code if there were errors
    if results.get("errors"):
        sys.exit(1)


if __name__ == "__main__":
    main()
