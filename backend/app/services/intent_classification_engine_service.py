"""Service for Intent Classification Engine (Orchestrator)."""

from typing import Dict, List, Optional
from datetime import datetime
import logging
from app.services.sec_edgar_scraper_service import sec_scraper
from app.services.osint_lead_scorer_service import osint_lead_scorer
from app.services.intent_classifier_service import intent_classifier
from app.services.global_hiring_score_service import global_hiring_score_calculator

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class IntentClassificationEngine:
    def __init__(self):
        self.sec_scraper = sec_scraper
        self.osint_scorer = osint_lead_scorer
        self.intent_classifier = intent_classifier
        self.ghs_calculator = global_hiring_score_calculator

    def analyze_company(self, company_ticker: Optional[str] = None, company_name: Optional[str] = None, company_description: Optional[str] = None, funding_amount: Optional[float] = None, funding_stage: str = "series_a") -> Dict:
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
        # SEC Form D Analysis
        if company_ticker:
            try:
                filings = self.sec_scraper.scrape_recent_form_d([company_ticker], limit=5)
                if filings:
                    latest_filing = filings[0]
                    details = self.sec_scraper.parse_form_d_details(latest_filing['filing_path'])
                    analysis['sec_data'] = {
                        'has_form_d': True,
                        'latest_filing_date': latest_filing.get('filing_date'),
                        'offering_amount': details.get('total_offering_amount'),
                        'company_name_sec': details.get('company_name')
                    }
                    if details.get('total_offering_amount') and not funding_amount:
                        funding_amount = details['total_offering_amount']
            except Exception as e:
                analysis['sec_data'] = {'has_form_d': False, 'error': str(e)}
        # News Analysis
        if company_name:
            try:
                query = f"{company_name} funding OR hiring OR expansion"
                scored_leads = self.osint_scorer.score_news_batch(query=query, regions=["US"], period="30d", max_results_per_region=10, min_score=0)
                if scored_leads:
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
                    analysis['news_analysis'] = {'articles_found': 0, 'note': 'No recent news found'}
            except Exception as e:
                analysis['news_analysis'] = {'error': str(e)}
        # Intent Classification
        if company_description:
            try:
                intent_result = self.intent_classifier.analyze_company_description(company_description)
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
                analysis['intent_classification'] = {'error': str(e)}
        # Global Hiring Score
        if funding_amount:
            try:
                ghs_result = self.ghs_calculator.calculate_ghs(funding_amount=funding_amount, company_stage=funding_stage, urgency_level='expansion', stated_headcount_goal=15)
                analysis['global_hiring_score'] = {
                    'score': ghs_result['global_hiring_score'],
                    'affordable_us_engineers': ghs_result['affordable_us_engineers'],
                    'must_hire_offshore': ghs_result['offshore_recommendation']['must_hire_offshore'],
                    'offshore_percentage': ghs_result['offshore_recommendation']['offshore_percentage'],
                    'hiring_urgency': ghs_result['hiring_urgency']
                }
            except Exception as e:
                analysis['global_hiring_score'] = {'error': str(e)}
        analysis['recommendation'] = self._generate_recommendation(analysis)
        return analysis

    def run_market_scan(self, target_tickers: Optional[List[str]] = None, news_queries: Optional[List[str]] = None) -> Dict:
        results = {
            'scan_timestamp': datetime.now().isoformat(),
            'sec_filings': [],
            'osint_leads': [],
            'qualified_leads': [],
            'summary': {}
        }
        # SEC Form D Filings
        if target_tickers:
            try:
                filings = self.sec_scraper.scrape_recent_form_d(target_tickers, limit=10)
                results['sec_filings'] = filings
            except Exception as e:
                results['sec_filings'] = {'error': str(e)}
        # OSINT News
        if news_queries is None:
            news_queries = [
                "tech startup series A funding",
                "tech company expansion hiring",
                "software company raises funding"
            ]
        all_osint_leads = []
        for query in news_queries:
            try:
                leads = self.osint_scorer.score_news_batch(query=query, regions=["US"], period="7d", max_results_per_region=20, min_score=30)
                all_osint_leads.extend(leads)
            except Exception as e:
                pass
        seen_urls = set()
        unique_osint_leads = []
        for lead in all_osint_leads:
            if lead['source_url'] not in seen_urls:
                seen_urls.add(lead['source_url'])
                unique_osint_leads.append(lead)
        results['osint_leads'] = sorted(unique_osint_leads, key=lambda x: x['growth_score'], reverse=True)
        # Qualify leads
        for lead in results['osint_leads'][:20]:
            try:
                funding_amount = self._extract_funding_from_text(f"{lead['article_title']} {lead.get('article_description', '')}")
                if funding_amount:
                    ghs = self.ghs_calculator.calculate_ghs(funding_amount=funding_amount, company_stage='series_a', urgency_level='expansion')
                    qualified_lead = {**lead, 'funding_amount': funding_amount, 'global_hiring_score': ghs['global_hiring_score'], 'must_hire_offshore': ghs['offshore_recommendation']['must_hire_offshore'], 'offshore_percentage': ghs['offshore_recommendation']['offshore_percentage'], 'qualification_status': 'qualified'}
                    results['qualified_leads'].append(qualified_lead)
            except Exception:
                pass
        results['summary'] = {
            'total_sec_filings': len(results['sec_filings']),
            'total_osint_leads': len(results['osint_leads']),
            'qualified_leads': len(results['qualified_leads']),
            'high_priority_leads': len([l for l in results['qualified_leads'] if l.get('must_hire_offshore', False)]),
            'average_growth_score': (sum(l['growth_score'] for l in results['osint_leads']) / len(results['osint_leads']) if results['osint_leads'] else 0)
        }
        return results

    def _extract_funding_from_text(self, text: str) -> Optional[float]:
        import re
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
        score = 0
        factors = []
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
        sec_data = analysis.get('sec_data')
        if isinstance(sec_data, dict) and sec_data.get('has_form_d'):
            score += 10
            factors.append("Recent Form D filing (active fundraising)")
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

# Singleton instance
intent_classification_engine = IntentClassificationEngine()
