#!/usr/bin/env python3
"""
Pulse Intelligence Quick Test
------------------------------
Fast validation script for Pulse Intelligence Module.
Run this before integrating with Oracle detector.

Usage:
    python quick_test_pulse.py
"""

import sys
from pathlib import Path

# Add scripts to path
sys.path.insert(0, str(Path(__file__).parent / 'scripts'))

try:
    from pulse_intelligence import PulseIntelligenceEngine
    print("✅ Pulse Intelligence module imported successfully\n")
except ImportError as e:
    print(f"❌ Failed to import module: {e}")
    print("\n📦 Install dependencies:")
    print("   pip install scikit-learn numpy pandas")
    sys.exit(1)

from datetime import datetime, timedelta
import json


def main():
    print("="*60)
    print("🧠 PULSE INTELLIGENCE - QUICK TEST")
    print("="*60)
    
    # Initialize engine
    print("\n1️⃣  Initializing Pulse Intelligence Engine...")
    engine = PulseIntelligenceEngine()
    print("   ✅ Engine initialized\n")
    
    # Sample data
    print("2️⃣  Analyzing sample company (TechVenture Inc.)...")
    sample_text = """
    TechVenture Inc. just raised $75M Series B from Sequoia Capital!
    
    We're scaling rapidly - hiring 50+ engineers across all levels.
    Opening new offices in San Francisco, Austin, and Berlin.
    
    Our ambitious team is building the future with cutting-edge tech:
    React, TypeScript, Python, FastAPI, AWS, Kubernetes, PostgreSQL, Redis
    
    Just announced: Sarah Chen joins as CTO from Google.
    
    Join our fast-paced startup on the path to unicorn status!
    """
    
    sample_jobs = [
        {'title': 'Senior Backend Engineer', 'posted_date': datetime.now().isoformat()},
        {'title': 'ML Engineer', 'posted_date': (datetime.now() - timedelta(hours=12)).isoformat()},
        {'title': 'Frontend Lead', 'posted_date': (datetime.now() - timedelta(hours=24)).isoformat()}
    ]
    
    # Run analysis
    result = engine.calculate_pulse_score(
        sec_funding_detected=True,
        text_content=sample_text,
        job_posts=sample_jobs
    )
    
    print("   ✅ Analysis complete\n")
    
    # Display results
    print("="*60)
    print("📊 PULSE INTELLIGENCE RESULTS")
    print("="*60)
    print(f"\n🎯 Pulse Score: {result['pulse_score']}/100")
    print(f"⚡ Desperation Level: {result['desperation_level']}")
    print(f"⏰ Urgency: {result['urgency']}")
    print(f"\n💡 Recommendation:")
    print(f"   {result['recommendation']}")
    
    print(f"\n📈 Signal Breakdown:")
    print(f"   SEC Funding: {'✅ Detected' if result['signals']['funding']['sec_detected'] else '❌ None'} (+{result['signals']['funding']['points']} pts)")
    print(f"   Expansion Density: {result['signals']['growth']['expansion_density']:.1f}% ({result['signals']['growth']['confidence']} confidence)")
    print(f"   Tech Stack: {result['signals']['technology']['total_tech_count']} technologies detected")
    print(f"   C-Level Hires: {result['signals']['hiring']['c_level_hires']['total_executive_hires']} executive(s)")
    print(f"   Job Velocity: {result['signals']['hiring']['job_velocity']['posts_in_window']} posts in 48h")
    print(f"   Red Flags: {'⚠️  YES' if result['signals']['red_flags']['is_risky'] else '✅ None'}")
    
    print(f"\n🔧 Tech Stack Detected:")
    for category, techs in result['signals']['technology']['tech_stack'].items():
        print(f"   {category.replace('_', ' ').title()}: {', '.join(techs[:5])}")
    
    print(f"\n📌 Top Growth Keywords:")
    for kw in result['signals']['growth']['top_keywords'][:5]:
        print(f"   • {kw}")
    
    print("\n" + "="*60)
    print("✅ PULSE INTELLIGENCE TEST PASSED")
    print("="*60)
    
    print("\n📋 Next Steps:")
    print("   1. Run full test suite: python scripts/test_pulse_intelligence.py")
    print("   2. Integrate with Oracle: python scripts/integrate_pulse_intelligence.py --help")
    print("   3. Review documentation: docs/PULSE_INTELLIGENCE.md")
    
    # Save sample output
    output_path = Path('data/output/pulse_sample_output.json')
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w') as f:
        json.dump(result, f, indent=2)
    
    print(f"\n💾 Sample output saved: {output_path}\n")


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
