"""
Example: Run Complete Intent Classification Pipeline
-----------------------------------------------------
Demonstrates the full workflow of the Intent Classification Engine
for US Tech Market Intelligence.
"""

import sys
from pathlib import Path
import json
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from intent_classification_engine import IntentClassificationEngine
from osint_lead_scorer import OSINTLeadScorer
from global_hiring_score import GlobalHiringScoreCalculator


def example_1_quick_osint_scan():
    """
    Example 1: Quick OSINT Lead Scoring
    Fastest way to generate leads without SEC data.
    """
    print("="*70)
    print("EXAMPLE 1: Quick OSINT Lead Scoring")
    print("="*70)
    
    scorer = OSINTLeadScorer(use_nltk=True)
    
    # Search for funding announcements
    leads = scorer.score_news_batch(
        query="tech startup series A OR series B funding",
        regions=["US"],
        period="7d",
        max_results_per_region=20,
        min_score=30
    )
    
    # Save results
    output_dir = Path("data/output/examples")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = output_dir / f"osint_leads_{timestamp}.json"
    
    scorer.save_scored_leads(leads, str(output_file))
    
    # Print summary
    print(f"\n✓ Found {len(leads)} qualified leads")
    print(f"✓ Results saved to: {output_file}")
    
    if leads:
        print("\nTop 3 Leads:")
        for i, lead in enumerate(leads[:3], 1):
            print(f"\n{i}. {lead['company_name']}")
            print(f"   Score: {lead['growth_score']}")
            print(f"   Window: {lead['predicted_hiring_window']}")
            print(f"   Signals: {', '.join(lead['matched_signals'][:3])}")
    
    return leads


def example_2_calculate_ghs():
    """
    Example 2: Calculate Global Hiring Score
    Determine offshore hiring necessity based on funding.
    """
    print("\n" + "="*70)
    print("EXAMPLE 2: Global Hiring Score Calculation")
    print("="*70)
    
    calculator = GlobalHiringScoreCalculator()
    
    # Scenario: Series A startup with $8M funding
    result = calculator.calculate_ghs(
        funding_amount=8_000_000,
        company_stage='series_a',
        urgency_level='expansion',
        stated_headcount_goal=15,
        current_team_size=5
    )
    
    print("\nCompany Profile:")
    print(f"  Funding: ${result['funding_amount']:,.0f}")
    print(f"  Stage: {result['company_stage']}")
    print(f"  Hiring Goal: 15 engineers (10 new hires)")
    
    print("\nGlobal Hiring Score Analysis:")
    print(f"  GHS: {result['global_hiring_score']}")
    print(f"  Affordable US Engineers: {result['affordable_us_engineers']}")
    print(f"  Hiring Urgency: {result['hiring_urgency']}")
    
    print("\nOffshore Recommendation:")
    rec = result['offshore_recommendation']
    print(f"  Must Hire Offshore: {rec['must_hire_offshore']}")
    print(f"  Recommended Offshore %: {rec['offshore_percentage']}%")
    print(f"  Reason: {rec['reason']}")
    
    print("\nRecommended Team Mix:")
    mix = rec['recommended_mix']
    print(f"  US Engineers: {mix['us_engineers']}")
    print(f"  Offshore Engineers: {mix['offshore_engineers']}")
    print(f"  Total Team: {mix['total_engineers']}")
    
    # Calculate ROI
    print("\n" + "-"*70)
    print("ROI Analysis (12-month project)")
    print("-"*70)
    
    roi = calculator.calculate_roi_offshore(
        team_size=mix['total_engineers'],
        offshore_percentage=rec['offshore_percentage'],
        project_duration_months=12
    )
    
    print(f"\nCost Comparison:")
    print(f"  All-US Team: ${roi['annual_costs']['all_us_team']:,.0f}/year")
    print(f"  Mixed Team: ${roi['annual_costs']['mixed_team']:,.0f}/year")
    print(f"  Annual Savings: ${roi['annual_costs']['annual_savings']:,.0f}")
    print(f"  Savings %: {roi['project_costs']['savings_percentage']}%")
    
    return result


def example_3_analyze_specific_company():
    """
    Example 3: Comprehensive Company Analysis
    Full pipeline for a specific target company.
    """
    print("\n" + "="*70)
    print("EXAMPLE 3: Comprehensive Company Analysis")
    print("="*70)
    
    engine = IntentClassificationEngine(
        company_name="PulseB2B Market Intelligence",
        contact_email="contact@pulseb2b.com",
        use_transformers=False
    )
    
    # Analyze a company with all available data
    company_data = {
        'company_name': 'RemoteFirst Tech',
        'company_description': """
        RemoteFirst Tech is a rapidly growing SaaS platform for distributed teams.
        We're building tools for remote-first companies and have a global team
        spanning LATAM, EMEA, and APAC timezones. After raising our $12M Series A,
        we're expanding our engineering organization and looking for talent worldwide.
        We believe in hiring the best people regardless of location.
        """,
        'funding_amount': 12_000_000,
        'funding_stage': 'series_a'
    }
    
    result = engine.analyze_company(**company_data)
    
    # Print analysis
    print(f"\nCompany: {result['company_name']}")
    print(f"Analyzed at: {result['analyzed_at']}")
    
    if result.get('intent_classification'):
        intent = result['intent_classification']
        print("\nOutsourcing Intent Classification:")
        print(f"  Intent Detected: {intent['outsourcing_intent_detected']}")
        print(f"  Intent Score: {intent['intent_score']}/100")
        print(f"  Intent Level: {intent['intent_level']}")
        print(f"  Confidence: {intent['confidence']:.2%}")
        
        print("\n  Key Signals:")
        for signal, detected in intent['key_signals'].items():
            status = "✓" if detected else "✗"
            print(f"    {status} {signal.replace('_', ' ').title()}")
    
    if result.get('global_hiring_score'):
        ghs = result['global_hiring_score']
        print("\nGlobal Hiring Score:")
        print(f"  Score: {ghs['score']}")
        print(f"  Must Hire Offshore: {ghs['must_hire_offshore']}")
        print(f"  Recommended Offshore %: {ghs['offshore_percentage']}%")
        print(f"  Urgency: {ghs['hiring_urgency']}")
    
    if result.get('recommendation'):
        rec = result['recommendation']
        print("\n" + "-"*70)
        print("RECOMMENDATION")
        print("-"*70)
        print(f"  Qualification Score: {rec['qualification_score']}/100")
        print(f"  Priority: {rec['priority']}")
        print(f"  Action: {rec['recommended_action']}")
        
        if rec['key_factors']:
            print("\n  Key Factors:")
            for factor in rec['key_factors']:
                print(f"    • {factor}")
    
    # Save detailed results
    output_dir = Path("data/output/examples")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    output_file = output_dir / f"company_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    
    print(f"\n✓ Detailed analysis saved to: {output_file}")
    
    return result


def example_4_market_wide_scan():
    """
    Example 4: Market-Wide Intelligence Scan
    Scan multiple sources to find all opportunities in the market.
    """
    print("\n" + "="*70)
    print("EXAMPLE 4: Market-Wide Intelligence Scan")
    print("="*70)
    
    engine = IntentClassificationEngine(
        company_name="PulseB2B Market Intelligence",
        contact_email="contact@pulseb2b.com"
    )
    
    # Define search parameters
    news_queries = [
        "tech startup series A funding",
        "SaaS company raises",
        "remote-first company hiring",
        "tech company expansion"
    ]
    
    print(f"\nScanning with {len(news_queries)} queries...")
    print("This may take a few minutes...\n")
    
    # Run comprehensive scan
    results = engine.run_market_scan(
        news_queries=news_queries,
        output_dir="data/output/examples/market_scan"
    )
    
    # Results are automatically saved and printed by the engine
    
    return results


def main():
    """Run all examples."""
    print("\n" + "="*70)
    print("INTENT CLASSIFICATION ENGINE - COMPLETE EXAMPLES")
    print("="*70)
    print("\nThis script demonstrates all major features of the engine.")
    print("Results will be saved to data/output/examples/\n")
    
    try:
        # Run examples
        example_1_quick_osint_scan()
        
        input("\nPress Enter to continue to Example 2...")
        example_2_calculate_ghs()
        
        input("\nPress Enter to continue to Example 3...")
        example_3_analyze_specific_company()
        
        input("\nPress Enter to continue to Example 4 (this may take a while)...")
        example_4_market_wide_scan()
        
        print("\n" + "="*70)
        print("✓ ALL EXAMPLES COMPLETED SUCCESSFULLY")
        print("="*70)
        print("\nCheck data/output/examples/ for all generated files.")
        
    except KeyboardInterrupt:
        print("\n\nExecution interrupted by user.")
    except Exception as e:
        print(f"\n\nError: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
