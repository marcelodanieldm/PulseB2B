"""
Intent Classification Engine - Main Orchestrator
-------------------------------------------------
Integrates SEC EDGAR scraper, OSINT lead scorer, intent classifier, and
Global Hiring Score calculator into a unified pipeline for US Tech Market
intelligence.
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
import sys

# Import our custom modules
from sec_edgar_scraper import SECFormDScraper
from osint_lead_scorer import OSINTLeadScorer
from intent_classifier import OutsourcingIntentClassifier
from global_hiring_score import GlobalHiringScoreCalculator

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class IntentClassificationEngine:
    """
    Main orchestrator for the Intent Classification Engine.
    
    Combines multiple data sources and analysis methods:
    1. SEC Form D filings (funding data)
    2. Tech news scraping (OSINT)
    3. NLP intent classification
    4. Global Hiring Score calculation
    """
    
    def __init__(
        self,
        company_name: str = "PulseB2B",
        contact_email: str = "contact@pulseb2b.com",
        use_transformers: bool = False
    ):
        """
        Initialize the Intent Classification Engine.
        
        Args:
            company_name: Your company name (for SEC identification)
            contact_email: Your contact email (for SEC identification)
            use_transformers: Whether to use HuggingFace transformers (requires installation)
        """
        logger.info("Initializing Intent Classification Engine...")
        
        # Initialize components
        self.sec_scraper = SECFormDScraper(
            company_name=company_name,
            email=contact_email
        )
        
        self.osint_scorer = OSINTLeadScorer(use_nltk=True)
        
        self.intent_classifier = OutsourcingIntentClassifier(
            use_transformers=use_transformers
        )
        
        self.ghs_calculator = GlobalHiringScoreCalculator()
        
        logger.info("All components initialized successfully")
    
    def analyze_company(
        self,
        company_ticker: Optional[str] = None,
        company_name: Optional[str] = None,
        company_description: Optional[str] = None,
        funding_amount: Optional[float] = None,
        funding_stage: str = "series_a"
    ) -> Dict:
        """
        Perform comprehensive analysis on a single company.
        
        Args:
            company_ticker: Stock ticker symbol (for SEC lookup)
            company_name: Company name (for news search)
            company_description: Company description text
            funding_amount: Known funding amount
            funding_stage: Funding stage (seed, series_a, etc.)
        
        Returns:
            Dictionary with complete analysis results
        """
        logger.info(f"Analyzing company: {company_name or company_ticker}")
        
        analysis = {
            'company_name': company_name,
            'company_ticker': company_ticker,
            'analyzed_at': datetime.now().isoformat(),
            'sec_data': None,
            'news_analysis': None,
            'intent_classification': None,
            'global_hiring_score': None,
            'recommendation': None
        }
        
        # 1. SEC Form D Analysis (if ticker provided)
        if company_ticker:
            try:
                logger.info(f"Fetching SEC Form D data for {company_ticker}")
                filings = self.sec_scraper.scrape_recent_form_d(
                    ticker_symbols=[company_ticker],
                    limit=5
                )
                
                if filings:
                    latest_filing = filings[0]
                    details = self.sec_scraper.parse_form_d_details(
                        latest_filing['filing_path']
                    )
                    
                    analysis['sec_data'] = {
                        'has_form_d': True,
                        'latest_filing_date': latest_filing.get('filing_date'),
                        'offering_amount': details.get('total_offering_amount'),
                        'company_name_sec': details.get('company_name')
                    }
                    
                    # Update funding amount if found in Form D
                    if details.get('total_offering_amount') and not funding_amount:
                        funding_amount = details['total_offering_amount']
                        
            except Exception as e:
                logger.warning(f"Could not fetch SEC data: {e}")
                analysis['sec_data'] = {'has_form_d': False, 'error': str(e)}
        
        # 2. News Analysis (if company name provided)
        if company_name:
            try:
                logger.info(f"Analyzing news for {company_name}")
                
                # Search for company-specific news
                query = f"{company_name} funding OR hiring OR expansion"
                scored_leads = self.osint_scorer.score_news_batch(
                    query=query,
                    regions=["US"],
                    period="30d",
                    max_results_per_region=10,
                    min_score=0
                )
                
                if scored_leads:
                    # Get the highest-scoring article
                    top_article = scored_leads[0]
                    
                    analysis['news_analysis'] = {
                        'articles_found': len(scored_leads),
                        'top_article': {
                            'title': top_article['article_title'],
                            'growth_score': top_article['growth_score'],
                            'signals': top_article['matched_signals'],
                            'hiring_window': top_article['predicted_hiring_window']
                        },
                        'aggregate_score': sum(a['growth_score'] for a in scored_leads) / len(scored_leads)
                    }
                else:
                    analysis['news_analysis'] = {
                        'articles_found': 0,
                        'note': 'No recent news found'
                    }
                    
            except Exception as e:
                logger.warning(f"Could not analyze news: {e}")
                analysis['news_analysis'] = {'error': str(e)}
        
        # 3. Intent Classification (if description provided)
        if company_description:
            try:
                logger.info("Classifying outsourcing intent")
                
                intent_result = self.intent_classifier.analyze_company_description(
                    company_description
                )
                
                analysis['intent_classification'] = {
                    'outsourcing_intent_detected': intent_result['outsourcing_intent_detected'],
                    'intent_score': intent_result['intent_score'],
                    'intent_level': intent_result['intent_level'],
                    'confidence': intent_result['confidence'],
                    'key_signals': {
                        'remote_work': len(intent_result['signals']['remote_work']) > 0,
                        'global_team': len(intent_result['signals']['global_team']) > 0,
                        'timezone_flexible': len(intent_result['signals']['timezone']) > 0
                    }
                }
                
            except Exception as e:
                logger.warning(f"Could not classify intent: {e}")
                analysis['intent_classification'] = {'error': str(e)}
        
        # 4. Global Hiring Score (if funding data available)
        if funding_amount:
            try:
                logger.info("Calculating Global Hiring Score")
                
                ghs_result = self.ghs_calculator.calculate_ghs(
                    funding_amount=funding_amount,
                    company_stage=funding_stage,
                    urgency_level='expansion',
                    stated_headcount_goal=15  # Default estimate
                )
                
                analysis['global_hiring_score'] = {
                    'score': ghs_result['global_hiring_score'],
                    'affordable_us_engineers': ghs_result['affordable_us_engineers'],
                    'must_hire_offshore': ghs_result['offshore_recommendation']['must_hire_offshore'],
                    'offshore_percentage': ghs_result['offshore_recommendation']['offshore_percentage'],
                    'hiring_urgency': ghs_result['hiring_urgency']
                }
                
            except Exception as e:
                logger.warning(f"Could not calculate GHS: {e}")
                analysis['global_hiring_score'] = {'error': str(e)}
        
        # 5. Generate Recommendation
        analysis['recommendation'] = self._generate_recommendation(analysis)
        
        return analysis
    
    def run_market_scan(
        self,
        target_tickers: Optional[List[str]] = None,
        news_queries: Optional[List[str]] = None,
        output_dir: str = "data/output/market_intelligence"
    ) -> Dict:
        """
        Run a comprehensive market scan across multiple data sources.
        
        Args:
            target_tickers: List of ticker symbols to monitor
            news_queries: List of news search queries
            output_dir: Directory to save results
        
        Returns:
            Dictionary with scan results and summary
        """
        logger.info("="*60)
        logger.info("Starting Market Intelligence Scan")
        logger.info("="*60)
        
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        results = {
            'scan_timestamp': datetime.now().isoformat(),
            'sec_filings': [],
            'osint_leads': [],
            'qualified_leads': [],
            'summary': {}
        }
        
        # 1. Scan SEC Form D Filings
        if target_tickers:
            logger.info(f"\n[1/3] Scanning SEC Form D for {len(target_tickers)} companies")
            try:
                filings = self.sec_scraper.scrape_recent_form_d(
                    ticker_symbols=target_tickers,
                    limit=10
                )
                results['sec_filings'] = filings
                logger.info(f"Found {len(filings)} Form D filings")
            except Exception as e:
                logger.error(f"SEC scan error: {e}")
        
        # 2. Scan Tech News (OSINT)
        if news_queries is None:
            news_queries = [
                "tech startup series A funding",
                "tech company expansion hiring",
                "software company raises funding"
            ]
        
        logger.info(f"\n[2/3] Scanning tech news with {len(news_queries)} queries")
        all_osint_leads = []
        
        for query in news_queries:
            try:
                leads = self.osint_scorer.score_news_batch(
                    query=query,
                    regions=["US"],
                    period="7d",
                    max_results_per_region=20,
                    min_score=30
                )
                all_osint_leads.extend(leads)
            except Exception as e:
                logger.error(f"OSINT scan error for query '{query}': {e}")
        
        # Deduplicate OSINT leads
        seen_urls = set()
        unique_osint_leads = []
        for lead in all_osint_leads:
            if lead['source_url'] not in seen_urls:
                seen_urls.add(lead['source_url'])
                unique_osint_leads.append(lead)
        
        results['osint_leads'] = sorted(
            unique_osint_leads,
            key=lambda x: x['growth_score'],
            reverse=True
        )
        
        logger.info(f"Found {len(unique_osint_leads)} qualified OSINT leads")
        
        # 3. Combine and Qualify Leads
        logger.info("\n[3/3] Qualifying leads and calculating GHS")
        
        for lead in results['osint_leads'][:20]:  # Top 20 leads
            try:
                # Extract funding amount if mentioned in article
                funding_amount = self._extract_funding_from_text(
                    f"{lead['article_title']} {lead.get('article_description', '')}"
                )
                
                if funding_amount:
                    # Calculate GHS
                    ghs = self.ghs_calculator.calculate_ghs(
                        funding_amount=funding_amount,
                        company_stage='series_a',
                        urgency_level='expansion'
                    )
                    
                    qualified_lead = {
                        **lead,
                        'funding_amount': funding_amount,
                        'global_hiring_score': ghs['global_hiring_score'],
                        'must_hire_offshore': ghs['offshore_recommendation']['must_hire_offshore'],
                        'offshore_percentage': ghs['offshore_recommendation']['offshore_percentage'],
                        'qualification_status': 'qualified'
                    }
                    
                    results['qualified_leads'].append(qualified_lead)
            except Exception as e:
                logger.debug(f"Could not qualify lead: {e}")
        
        # Generate Summary
        results['summary'] = {
            'total_sec_filings': len(results['sec_filings']),
            'total_osint_leads': len(results['osint_leads']),
            'qualified_leads': len(results['qualified_leads']),
            'high_priority_leads': len([
                l for l in results['qualified_leads']
                if l.get('must_hire_offshore', False)
            ]),
            'average_growth_score': (
                sum(l['growth_score'] for l in results['osint_leads']) / len(results['osint_leads'])
                if results['osint_leads'] else 0
            )
        }
        
        # Save results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = output_path / f"market_scan_{timestamp}.json"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        logger.info(f"\nResults saved to: {output_file}")
        
        # Print summary
        self._print_scan_summary(results)
        
        return results
    
    def _extract_funding_from_text(self, text: str) -> Optional[float]:
        """Extract funding amount from text (e.g., '$5M', '$10 million')."""
        import re
        
        # Patterns for funding amounts
        patterns = [
            r'\$(\d+(?:\.\d+)?)\s*(?:million|M)\b',
            r'\$(\d+(?:\.\d+)?)\s*(?:billion|B)\b',
            r'raised\s+\$(\d+(?:\.\d+)?)\s*(?:million|M)\b',
            r'secured\s+\$(\d+(?:\.\d+)?)\s*(?:million|M)\b',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                amount = float(match.group(1))
                if 'billion' in pattern.lower() or 'B' in pattern:
                    return amount * 1_000_000_000
                else:
                    return amount * 1_000_000
        
        return None
    
    def _generate_recommendation(self, analysis: Dict) -> Dict:
        """Generate actionable recommendation based on analysis."""
        score = 0
        factors = []
        
        # Score based on available data
        if analysis.get('global_hiring_score'):
            ghs = analysis['global_hiring_score']
            if ghs.get('must_hire_offshore'):
                score += 40
                factors.append(f"Must hire offshore ({ghs.get('offshore_percentage')}%)")
            elif ghs.get('offshore_percentage', 0) >= 30:
                score += 25
                factors.append(f"Should consider offshore ({ghs.get('offshore_percentage')}%)")
        
        if analysis.get('intent_classification'):
            intent = analysis['intent_classification']
            if intent.get('outsourcing_intent_detected'):
                score += 30
                factors.append(f"Strong outsourcing intent ({intent.get('intent_score')}/100)")
        
        if analysis.get('news_analysis'):
            news = analysis['news_analysis']
            if news.get('top_article', {}).get('growth_score', 0) >= 70:
                score += 20
                factors.append("High growth signals in recent news")
        
        if analysis.get('sec_data', {}).get('has_form_d'):
            score += 10
            factors.append("Recent Form D filing (active fundraising)")
        
        # Determine priority
        if score >= 70:
            priority = "Critical - Immediate Outreach"
            action = "Schedule discovery call within 48 hours"
        elif score >= 50:
            priority = "High - Priority Outreach"
            action = "Add to outreach queue for next week"
        elif score >= 30:
            priority = "Medium - Monitor"
            action = "Add to monitoring list, check back in 2-4 weeks"
        else:
            priority = "Low - Long-term Nurture"
            action = "Add to general marketing list"
        
        return {
            'qualification_score': score,
            'priority': priority,
            'recommended_action': action,
            'key_factors': factors
        }
    
    def _print_scan_summary(self, results: Dict):
        """Print a formatted summary of scan results."""
        summary = results['summary']
        
        print("\n" + "="*60)
        print("MARKET INTELLIGENCE SCAN SUMMARY")
        print("="*60)
        print(f"Scan Time: {results['scan_timestamp']}")
        print(f"\nData Sources:")
        print(f"  - SEC Form D Filings: {summary['total_sec_filings']}")
        print(f"  - OSINT Leads: {summary['total_osint_leads']}")
        print(f"  - Qualified Leads: {summary['qualified_leads']}")
        print(f"  - High Priority: {summary['high_priority_leads']}")
        
        if results['qualified_leads']:
            print(f"\nTop 5 Qualified Leads:")
            print("-"*60)
            
            for i, lead in enumerate(results['qualified_leads'][:5], 1):
                print(f"\n{i}. {lead['company_name']}")
                print(f"   Growth Score: {lead['growth_score']}")
                print(f"   GHS: {lead.get('global_hiring_score', 'N/A')}")
                print(f"   Offshore Need: {lead.get('offshore_percentage', 0)}%")
                print(f"   Window: {lead.get('predicted_hiring_window', 'N/A')}")
        
        print("\n" + "="*60)


# Main execution
if __name__ == "__main__":
    # Initialize engine
    engine = IntentClassificationEngine(
        company_name="PulseB2B Market Intelligence",
        contact_email="contact@pulseb2b.com",
        use_transformers=False  # Set to True if you have transformers installed
    )
    
    # Example 1: Analyze a specific company
    print("\n" + "="*60)
    print("EXAMPLE 1: Single Company Analysis")
    print("="*60)
    
    company_analysis = engine.analyze_company(
        company_name="Acme Corp",
        company_description="""
        We are a fast-growing SaaS startup building remote-first solutions.
        Our distributed team spans across LATAM and EMEA timezones, and we're
        looking to scale our engineering organization globally. We recently
        raised our Series A and are expanding our global talent acquisition.
        """,
        funding_amount=10_000_000,
        funding_stage="series_a"
    )
    
    print(json.dumps(company_analysis, indent=2))
    
    # Example 2: Run market scan
    print("\n" + "="*60)
    print("EXAMPLE 2: Market-Wide Scan")
    print("="*60)
    
    scan_results = engine.run_market_scan(
        news_queries=[
            "tech startup series B funding",
            "SaaS company raises",
            "remote-first company hiring"
        ]
    )
    
    print(f"\nScan complete. Found {scan_results['summary']['qualified_leads']} qualified leads")
