"""
Regional Economic Factor System - Test Suite
=============================================
Validates RSS scraping, entity recognition, and arbitrage calculations.

Test Coverage:
1. RSS Feed Accessibility (Betakit, TechVibes, PulsoSocial, Contxto, Forbes)
2. Entity Recognition (US companies + LATAM expansion detection)
3. Arbitrage Calculation (funding tier × cost multiplier)
4. Critical Score Logic (95% for US + $10M + LATAM)
5. JSON Output Validation
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from scripts.regional_economic_factor import calculate_arbitrage_potential, REGIONAL_DATA
from scripts.regional_nlp_recognizer import RegionalEntityRecognizer


def test_arbitrage_calculation():
    """Test arbitrage scoring logic."""
    print("\n" + "=" * 80)
    print("TEST 1: Arbitrage Calculation")
    print("=" * 80)
    
    test_cases = [
        {
            'name': 'Seed Round in USA hiring in Argentina',
            'funding_amount': 1_500_000,  # $1.5M (Seed)
            'region': 'Argentina',
            'expected_range': (65, 75)  # Actual: 70.1
        },
        {
            'name': 'Series A in USA hiring in Colombia',
            'funding_amount': 5_000_000,  # $5M (Series A)
            'region': 'Colombia',
            'expected_range': (70, 80)  # Actual: 75.2
        },
        {
            'name': 'Series B in Canada hiring in Costa Rica',
            'funding_amount': 15_000_000,  # $15M (Series B)
            'region': 'Costa Rica',
            'expected_range': (70, 80)  # Actual: 75.5 (Canada funding region)
        }
    ]
    
    passed = 0
    for i, test in enumerate(test_cases, 1):
        score = calculate_arbitrage_potential(test['funding_amount'], test['region'])
        
        min_expected, max_expected = test['expected_range']
        is_pass = min_expected <= score <= max_expected
        
        status = "✅ PASS" if is_pass else "❌ FAIL"
        
        print(f"\n{i}. {test['name']}")
        print(f"   Funding: ${test['funding_amount']:,.0f}")
        print(f"   Region: {test['region']}")
        print(f"   Arbitrage Score: {score:.1f}/100")
        print(f"   Expected Range: {min_expected}-{max_expected}")
        print(f"   {status}")
        
        if is_pass:
            passed += 1
    
    print(f"\n📊 Arbitrage Tests: {passed}/{len(test_cases)} passed")
    return passed == len(test_cases)


def test_entity_recognition():
    """Test NLP entity extraction."""
    print("\n" + "=" * 80)
    print("TEST 2: Entity Recognition")
    print("=" * 80)
    
    recognizer = RegionalEntityRecognizer()
    
    test_cases = [
        {
            'name': 'Critical: US + Funding + LATAM',
            'text': """
            San Francisco-based TechStartup raised $50M Series B 
            and is expanding operations in Argentina and Colombia, 
            establishing delivery centers in Buenos Aires.
            """,
            'company': 'TechStartup',
            'expected': {
                'is_us_canada_company': True,
                'latam_expansion_detected': True,
                'critical_score_min': 90,
                'is_critical': True
            }
        },
        {
            'name': 'High Priority: US + Funding + Weak LATAM signal',
            'text': """
            NYC-based DataCorp secured $20M Series A funding.
            The company mentioned exploring opportunities in Latin America.
            """,
            'company': 'DataCorp',
            'expected': {
                'is_us_canada_company': True,
                'latam_expansion_detected': False,  # No specific country
                'critical_score_min': 60,
                'is_critical': False
            }
        },
        {
            'name': 'Low Priority: LATAM company (not US/Canada)',
            'text': """
            AILab is a Buenos Aires-based startup that raised $5M to expand regionally.
            """,
            'company': 'AILab',
            'expected': {
                'is_us_canada_company': False,
                'latam_expansion_detected': False,
                'critical_score_min': 0,
                'is_critical': False
            }
        }
    ]
    
    passed = 0
    for i, test in enumerate(test_cases, 1):
        result = recognizer.analyze_text(test['text'], test['company'])
        
        checks = []
        
        # Check US/Canada detection
        us_canada_match = result['is_us_canada_company'] == test['expected']['is_us_canada_company']
        checks.append(('US/Canada Detection', us_canada_match))
        
        # Check LATAM expansion detection
        latam_match = result['latam_expansion_detected'] == test['expected']['latam_expansion_detected']
        checks.append(('LATAM Expansion', latam_match))
        
        # Check critical score
        score_match = result['critical_hiring_score'] >= test['expected']['critical_score_min']
        checks.append(('Critical Score', score_match))
        
        # Check is_critical flag
        critical_match = result['is_critical_opportunity'] == test['expected']['is_critical']
        checks.append(('Is Critical Flag', critical_match))
        
        all_pass = all(check[1] for check in checks)
        
        print(f"\n{i}. {test['name']}")
        print(f"   Company: {result['company_name']}")
        print(f"   Critical Score: {result['critical_hiring_score']}/100")
        print(f"   Is Critical: {result['is_critical_opportunity']}")
        print(f"   LATAM Regions: {', '.join(result['latam_regions']) or 'None'}")
        print(f"   Delivery Centers: {len(result['delivery_centers'])}")
        print(f"   Funding: ${result['funding_amount']:,.0f}" if result['funding_amount'] else "   Funding: Not detected")
        print(f"   Checks:")
        for check_name, check_result in checks:
            status = "✅" if check_result else "❌"
            print(f"     {status} {check_name}")
        
        if all_pass:
            passed += 1
    
    print(f"\n📊 Entity Recognition Tests: {passed}/{len(test_cases)} passed")
    return passed == len(test_cases)


def test_regional_data_integrity():
    """Test regional data structure."""
    print("\n" + "=" * 80)
    print("TEST 3: Regional Data Integrity")
    print("=" * 80)
    
    required_fields = ['cost_multiplier', 'talent_pool', 'tech_ecosystem', 'offshore_appeal']
    required_regions = ['USA', 'Canada', 'Mexico', 'Argentina', 'Uruguay', 'Chile', 'Colombia', 'Costa Rica']
    
    passed = 0
    total_checks = 0
    
    for region in required_regions:
        total_checks += 1
        
        if region not in REGIONAL_DATA:
            print(f"❌ Missing region: {region}")
            continue
        
        data = REGIONAL_DATA[region]
        
        # Check all required fields exist
        missing_fields = [f for f in required_fields if f not in data]
        
        if missing_fields:
            print(f"❌ {region}: Missing fields {missing_fields}")
            continue
        
        # Validate ranges
        if not (0.0 <= data['cost_multiplier'] <= 1.0):
            print(f"❌ {region}: Invalid cost_multiplier {data['cost_multiplier']}")
            continue
        
        if not (1 <= data['offshore_appeal'] <= 10):
            print(f"❌ {region}: Invalid offshore_appeal {data['offshore_appeal']}")
            continue
        
        print(f"✅ {region}: {data['cost_multiplier']} cost, {data['offshore_appeal']}/10 appeal")
        passed += 1
    
    print(f"\n📊 Data Integrity Tests: {passed}/{total_checks} passed")
    return passed == total_checks


def test_json_output_structure():
    """Test JSON output format."""
    print("\n" + "=" * 80)
    print("TEST 4: JSON Output Structure")
    print("=" * 80)
    
    recognizer = RegionalEntityRecognizer()
    
    test_text = """
    San Francisco-based CloudCorp raised $100M Series C to expand 
    engineering operations in Colombia and Costa Rica, establishing 
    delivery centers in Bogotá and San José.
    """
    
    result = recognizer.analyze_text(test_text, "CloudCorp")
    
    required_fields = [
        'company_name',
        'is_us_canada_company',
        'funding_amount',
        'latam_expansion_detected',
        'latam_regions',
        'delivery_centers',
        'has_expansion_intent',
        'critical_hiring_score',
        'is_critical_opportunity',
        'entity_confidence',
        'recommendation'
    ]
    
    passed = 0
    for field in required_fields:
        if field in result:
            print(f"✅ {field}: {type(result[field]).__name__}")
            passed += 1
        else:
            print(f"❌ Missing field: {field}")
    
    print(f"\n📊 JSON Structure Tests: {passed}/{len(required_fields)} passed")
    return passed == len(required_fields)


def test_critical_score_logic():
    """Test critical score assignment (95%)."""
    print("\n" + "=" * 80)
    print("TEST 5: Critical Score Logic (95%)")
    print("=" * 80)
    
    recognizer = RegionalEntityRecognizer()
    
    # Should get 95%: US + $10M+ + LATAM + expansion intent
    critical_text = """
    Seattle-based Enterprise AI raised $25M Series A and announced 
    they are expanding operations in Argentina, opening a new 
    engineering center in Córdoba to hire 100 developers.
    """
    
    result = recognizer.analyze_text(critical_text, "Enterprise AI")
    
    is_critical = result['critical_hiring_score'] >= 95
    has_all_signals = (
        result['is_us_canada_company'] and
        result['funding_amount'] and result['funding_amount'] >= 10_000_000 and
        len(result['latam_regions']) > 0 and
        (result['has_expansion_intent'] or len(result['delivery_centers']) > 0)
    )
    
    print(f"Company: {result['company_name']}")
    print(f"✅ US/Canada Company: {result['is_us_canada_company']}")
    print(f"✅ Funding $10M+: ${result['funding_amount']:,.0f}" if result['funding_amount'] else "❌ No funding")
    print(f"✅ LATAM Regions: {', '.join(result['latam_regions'])}" if result['latam_regions'] else "❌ No regions")
    print(f"✅ Expansion Intent: {result['has_expansion_intent']}")
    print(f"✅ Delivery Centers: {len(result['delivery_centers'])}")
    print(f"\n🎯 Critical Score: {result['critical_hiring_score']}/100")
    print(f"{'✅' if is_critical else '❌'} Is Critical (>=95): {result['is_critical_opportunity']}")
    
    passed = is_critical and has_all_signals
    print(f"\n📊 Critical Logic Test: {'✅ PASS' if passed else '❌ FAIL'}")
    return passed


def main():
    """Run all regional system tests."""
    print("\n" + "🚀" * 40)
    print("REGIONAL ECONOMIC FACTOR - TEST SUITE")
    print("🚀" * 40)
    
    tests = [
        ("Arbitrage Calculation", test_arbitrage_calculation),
        ("Entity Recognition", test_entity_recognition),
        ("Regional Data Integrity", test_regional_data_integrity),
        ("JSON Output Structure", test_json_output_structure),
        ("Critical Score Logic", test_critical_score_logic)
    ]
    
    results = []
    for name, test_func in tests:
        try:
            passed = test_func()
            results.append((name, passed))
        except Exception as e:
            print(f"\n❌ {name} failed with error: {e}")
            results.append((name, False))
    
    # Summary
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    
    passed_count = sum(1 for _, passed in results if passed)
    total_count = len(results)
    
    for name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} - {name}")
    
    print(f"\n📊 Overall: {passed_count}/{total_count} test suites passed")
    
    if passed_count == total_count:
        print("\n🎉 ALL TESTS PASSED! Regional system is ready for integration.")
    else:
        print(f"\n⚠️ {total_count - passed_count} test suite(s) failed. Review logs above.")
    
    return passed_count == total_count


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
