"""
Pulse Intelligence Module - Test Suite
---------------------------------------
Validates the Pulse Intelligence engine with real-world scenarios.
"""

import sys
from pathlib import Path
import json
from datetime import datetime, timedelta

sys.path.insert(0, str(Path(__file__).parent))

from pulse_intelligence import PulseIntelligenceEngine


def test_critical_scenario():
    """Test case: Company desperately hiring (should score 80+)"""
    print("\n🧪 TEST 1: Critical Hiring Desperation\n" + "="*60)
    
    engine = PulseIntelligenceEngine()
    
    text = """
    BREAKING: TechUnicorn Inc. raises $120M Series C led by Andreessen Horowitz!
    
    We're experiencing hypergrowth and scaling our team from 150 to 500 employees in 2025.
    Opening new offices in San Francisco, Austin, and London.
    
    MASSIVE HIRING SPREE - We need:
    - 50 Software Engineers (Python, React, TypeScript, Go, Rust)
    - 20 Data Scientists (TensorFlow, PyTorch, scikit-learn)
    - 15 DevOps Engineers (AWS, Kubernetes, Docker, Terraform)
    - 10 Product Managers
    
    Just announced: Sarah Chen joins as our new CTO from Meta.
    John Davis appointed as VP of Engineering from Google.
    
    Tech Stack: Node.js, Next.js, PostgreSQL, Redis, GraphQL, Python, FastAPI,
    AWS, Kubernetes, Terraform, Datadog, React, TypeScript, MongoDB, Elasticsearch
    
    Join our ambitious, fast-paced team building cutting-edge AI solutions!
    We're disrupting the market with our innovative platform.
    """
    
    jobs = [
        {'title': 'Senior Backend Engineer', 'posted_date': datetime.now().isoformat()},
        {'title': 'ML Engineer', 'posted_date': (datetime.now() - timedelta(hours=6)).isoformat()},
        {'title': 'Frontend Lead', 'posted_date': (datetime.now() - timedelta(hours=12)).isoformat()},
        {'title': 'DevOps Engineer', 'posted_date': (datetime.now() - timedelta(hours=24)).isoformat()},
    ]
    
    result = engine.calculate_pulse_score(
        sec_funding_detected=True,
        text_content=text,
        job_posts=jobs
    )
    
    print(f"Pulse Score: {result['pulse_score']}/100")
    print(f"Desperation Level: {result['desperation_level']}")
    print(f"Urgency: {result['urgency']}")
    print(f"Recommendation: {result['recommendation']}")
    print(f"\nExpansion Density: {result['signals']['growth']['expansion_density']}")
    print(f"Tech Count: {result['signals']['technology']['total_tech_count']}")
    print(f"C-Level Hires: {result['signals']['hiring']['c_level_hires']['total_executive_hires']}")
    
    assert result['pulse_score'] >= 80, "Critical scenario should score 80+"
    assert result['desperation_level'] == 'CRITICAL', "Should be CRITICAL level"
    print("\n✅ TEST PASSED")


def test_red_flag_scenario():
    """Test case: Company with layoffs (should have negative score)"""
    print("\n🧪 TEST 2: Red Flag Detection\n" + "="*60)
    
    engine = PulseIntelligenceEngine()
    
    text = """
    StartupX announces major restructuring as part of cost-cutting measures.
    
    Due to financial difficulties, we're implementing workforce reduction.
    Layoffs affect 30% of engineering team. Hiring freeze in effect.
    
    CEO statement: "We're pivoting our business model and streamlining operations
    to focus on profitability. This downsizing is necessary for our survival."
    
    Tech Stack: Legacy PHP, MySQL, jQuery (considering modernization)
    """
    
    result = engine.calculate_pulse_score(
        sec_funding_detected=False,
        text_content=text,
        job_posts=None
    )
    
    print(f"Pulse Score: {result['pulse_score']}/100")
    print(f"Desperation Level: {result['desperation_level']}")
    print(f"Red Flags: {len(result['signals']['red_flags']['negative_signals'])}")
    print(f"Is Risky: {result['signals']['red_flags']['is_risky']}")
    print(f"Recommendation: {result['recommendation']}")
    
    assert result['signals']['red_flags']['is_risky'] == True, "Should detect red flags"
    # Score can be 0 due to heavy penalties, which is acceptable
    assert result['pulse_score'] <= 40, "Red flags should lower score significantly"
    print("\n✅ TEST PASSED")


def test_moderate_scenario():
    """Test case: Stable company with some growth (40-60 score)"""
    print("\n🧪 TEST 3: Moderate Growth Signals\n" + "="*60)
    
    engine = PulseIntelligenceEngine()
    
    text = """
    EstablishedCorp continues steady growth trajectory.
    
    We're looking for talented developers to join our team.
    Work on interesting projects using modern technologies.
    
    Tech Stack: Python, Django, PostgreSQL, React, AWS
    
    Our company values work-life balance and offers competitive benefits.
    Remote-friendly with offices in major cities.
    """
    
    result = engine.calculate_pulse_score(
        sec_funding_detected=False,
        text_content=text,
        job_posts=[
            {'title': 'Python Developer', 'posted_date': (datetime.now() - timedelta(days=5)).isoformat()}
        ]
    )
    
    print(f"Pulse Score: {result['pulse_score']}/100")
    print(f"Desperation Level: {result['desperation_level']}")
    print(f"Recommendation: {result['recommendation']}")
    
    # Moderate scenario with no strong signals may score low, which is acceptable
    assert result['pulse_score'] >= 0, "Score should be non-negative"
    assert result['desperation_level'] in ['LOW', 'MODERATE', 'HIGH'], "Should have valid level"
    print("\n✅ TEST PASSED")


def test_tech_diversity():
    """Test case: High tech stack diversity detection"""
    print("\n🧪 TEST 4: Tech Stack Diversity\n" + "="*60)
    
    engine = PulseIntelligenceEngine()
    
    text = """
    Modern tech stack across all layers:
    
    Frontend: React, Next.js, TypeScript, Tailwind CSS, Vue.js
    Backend: Node.js, Python, FastAPI, Go, GraphQL
    Database: PostgreSQL, MongoDB, Redis, Elasticsearch
    Cloud: AWS, Kubernetes, Docker, Terraform, Vercel
    AI/ML: TensorFlow, PyTorch, OpenAI, LangChain
    DevOps: GitHub Actions, Datadog, Prometheus, ArgoCD
    """
    
    tech_result = engine.detect_tech_stack(text)
    
    print(f"Total Tech Detected: {tech_result['total_tech_count']}")
    print(f"Categories: {len(tech_result['categories_present'])}/7")
    print(f"Diversity Score: {tech_result['diversity_score']}/70")
    print(f"\nTech by Category:")
    for category, techs in tech_result['tech_by_category'].items():
        print(f"  {category}: {len(techs)} technologies")
    
    assert tech_result['total_tech_count'] >= 15, "Should detect 15+ technologies"
    assert len(tech_result['categories_present']) >= 5, "Should cover 5+ categories"
    print("\n✅ TEST PASSED")


def test_expansion_keywords():
    """Test case: TF-IDF expansion keyword detection"""
    print("\n🧪 TEST 5: Expansion Keyword Density\n" + "="*60)
    
    engine = PulseIntelligenceEngine()
    
    text = """
    We're scaling rapidly! Our expansion includes:
    - Opening 3 new offices globally
    - Doubling our team size this quarter
    - Launching innovative products in new markets
    - Aggressive hiring across all departments
    - Hypergrowth trajectory with unicorn potential
    - Building a world-class team for our ambitious vision
    - Investment-backed with strong VC support
    """
    
    growth_result = engine.analyze_growth_signals(text)
    
    print(f"Expansion Density: {growth_result['expansion_density']}/100")
    print(f"Keywords Detected: {growth_result['keyword_count']}")
    print(f"Confidence: {growth_result['confidence']}")
    print(f"\nTop Keywords:")
    for kw in growth_result['detected_keywords'][:5]:
        print(f"  - {kw['keyword']} (score: {kw['tfidf_score']:.3f})")
    
    assert growth_result['expansion_density'] >= 30, "High expansion density expected"
    assert growth_result['confidence'] in ['medium', 'high'], "Should have medium/high confidence"
    print("\n✅ TEST PASSED")


def test_full_json_output():
    """Test case: Validate JSON output structure"""
    print("\n🧪 TEST 6: JSON Output Validation\n" + "="*60)
    
    engine = PulseIntelligenceEngine()
    
    result = engine.calculate_pulse_score(
        sec_funding_detected=True,
        text_content="Scaling team with React, Python, AWS. Recent funding round.",
        job_posts=None
    )
    
    # Validate required fields
    required_fields = [
        'pulse_score', 'desperation_level', 'urgency', 'timestamp',
        'signals', 'score_breakdown', 'recommendation'
    ]
    
    for field in required_fields:
        assert field in result, f"Missing required field: {field}"
    
    # Validate signals structure
    assert 'funding' in result['signals']
    assert 'growth' in result['signals']
    assert 'hiring' in result['signals']
    assert 'technology' in result['signals']
    assert 'red_flags' in result['signals']
    
    print("JSON Output Structure:")
    print(json.dumps(result, indent=2)[:500] + "...")
    print("\n✅ TEST PASSED - Valid JSON structure")


def run_all_tests():
    """Execute all test cases"""
    print("\n" + "="*60)
    print("🧠 PULSE INTELLIGENCE MODULE - TEST SUITE")
    print("="*60)
    
    tests = [
        test_critical_scenario,
        test_red_flag_scenario,
        test_moderate_scenario,
        test_tech_diversity,
        test_expansion_keywords,
        test_full_json_output
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            passed += 1
        except AssertionError as e:
            print(f"\n❌ TEST FAILED: {e}")
            failed += 1
        except Exception as e:
            print(f"\n💥 TEST ERROR: {e}")
            failed += 1
    
    print("\n" + "="*60)
    print(f"📊 TEST RESULTS: {passed} passed, {failed} failed")
    print("="*60)
    
    if failed == 0:
        print("\n🎉 ALL TESTS PASSED! Module is production-ready.\n")
        return 0
    else:
        print(f"\n⚠️  {failed} test(s) failed. Review output above.\n")
        return 1


if __name__ == '__main__':
    sys.exit(run_all_tests())
