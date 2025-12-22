"""
Regional Economic Factor Module
================================
Advanced arbitrage detection for cross-border hiring opportunities.
Calculates hiring probability based on funding location vs talent cost.

Author: PulseB2B Lead Data Scientist
Strategy: Detect when US/Canadian funded companies expand to LATAM delivery centers
"""

import numpy as np
from typing import Dict, Tuple, Optional
from datetime import datetime


class RegionalEconomicAnalyzer:
    """
    Analyzes regional economic factors to predict cross-border hiring opportunities.
    """
    
    # Average annual software engineer salaries (USD, 2025)
    TALENT_COSTS = {
        'USA': 145000,
        'Canada': 95000,
        'Mexico': 42000,
        'Argentina': 38000,
        'Uruguay': 45000,
        'Chile': 48000,
        'Colombia': 35000,
        'Costa Rica': 40000
    }
    
    # Economic stability scores (0-100, higher = more stable)
    STABILITY_SCORES = {
        'USA': 95,
        'Canada': 93,
        'Mexico': 72,
        'Argentina': 58,
        'Uruguay': 78,
        'Chile': 80,
        'Colombia': 70,
        'Costa Rica': 82
    }
    
    # Tech ecosystem maturity (0-100, higher = more mature)
    ECOSYSTEM_MATURITY = {
        'USA': 100,
        'Canada': 90,
        'Mexico': 65,
        'Argentina': 75,
        'Uruguay': 72,
        'Chile': 68,
        'Colombia': 60,
        'Costa Rica': 70
    }
    
    # English proficiency index (0-100, higher = better)
    ENGLISH_PROFICIENCY = {
        'USA': 100,
        'Canada': 100,
        'Mexico': 52,
        'Argentina': 58,
        'Uruguay': 60,
        'Chile': 53,
        'Colombia': 48,
        'Costa Rica': 57
    }
    
    # Time zone overlap with US (hours, positive = advantage)
    TIMEZONE_OVERLAP = {
        'USA': 8,        # Reference
        'Canada': 8,     # Same/similar zones
        'Mexico': 7,     # CST/MST overlap
        'Argentina': 4,  # EST+2 hours
        'Uruguay': 4,    # EST+2 hours
        'Chile': 4,      # EST+1/2 hours
        'Colombia': 8,   # EST perfect match
        'Costa Rica': 8  # CST perfect match
    }
    
    # Preferred LATAM destinations for US companies (based on market research)
    LATAM_PREFERENCES = {
        'Colombia': 1.0,    # Highest preference
        'Costa Rica': 0.95,
        'Argentina': 0.90,
        'Uruguay': 0.85,
        'Chile': 0.80,
        'Mexico': 0.75
    }
    
    def __init__(self):
        """Initialize the analyzer."""
        pass
    
    def calculate_arbitrage_potential(
        self, 
        funding_amount: float,
        funding_region: str,
        target_region: str
    ) -> Dict[str, any]:
        """
        Calculate arbitrage potential for hiring in a different region.
        
        Args:
            funding_amount: Total funding raised (USD)
            funding_region: Where the company got funding (e.g., 'USA', 'Canada')
            target_region: Where they might hire (e.g., 'Colombia', 'Argentina')
            
        Returns:
            Dictionary with arbitrage metrics
        """
        if funding_region not in self.TALENT_COSTS or target_region not in self.TALENT_COSTS:
            return {
                'arbitrage_score': 0,
                'cost_savings': 0,
                'probability_boost': 0,
                'recommendation': 'Unknown region'
            }
        
        # Calculate cost savings
        funding_cost = self.TALENT_COSTS[funding_region]
        target_cost = self.TALENT_COSTS[target_region]
        cost_savings = funding_cost - target_cost
        cost_savings_pct = (cost_savings / funding_cost) * 100
        
        # Calculate how many engineers could be hired
        engineers_in_funding_region = funding_amount / funding_cost
        engineers_in_target_region = funding_amount / target_cost
        extra_capacity = engineers_in_target_region - engineers_in_funding_region
        
        # Quality factors (weighted)
        quality_score = (
            self.STABILITY_SCORES[target_region] * 0.25 +
            self.ECOSYSTEM_MATURITY[target_region] * 0.20 +
            self.ENGLISH_PROFICIENCY[target_region] * 0.20 +
            (self.TIMEZONE_OVERLAP[target_region] / 8 * 100) * 0.20 +
            (self.LATAM_PREFERENCES.get(target_region, 0.5) * 100) * 0.15
        )
        
        # Arbitrage score (0-100)
        # Higher savings + higher quality = higher score
        arbitrage_score = (cost_savings_pct * 0.6) + (quality_score * 0.4)
        arbitrage_score = min(100, max(0, arbitrage_score))
        
        # Probability boost for Pulse Intelligence
        # Cross-border hiring gets a boost if arbitrage is strong
        if arbitrage_score >= 70:
            probability_boost = 25  # +25 points
        elif arbitrage_score >= 50:
            probability_boost = 15  # +15 points
        elif arbitrage_score >= 30:
            probability_boost = 10  # +10 points
        else:
            probability_boost = 0
        
        # Critical hiring score (95%) if conditions are met
        is_critical = (
            funding_region in ['USA', 'Canada'] and
            target_region in ['Colombia', 'Argentina', 'Costa Rica', 'Uruguay'] and
            funding_amount >= 10_000_000 and  # $10M+ funding
            arbitrage_score >= 60
        )
        
        return {
            'arbitrage_score': round(arbitrage_score, 2),
            'cost_savings_usd': int(cost_savings),
            'cost_savings_pct': round(cost_savings_pct, 1),
            'extra_capacity': round(extra_capacity, 1),
            'quality_score': round(quality_score, 2),
            'stability': self.STABILITY_SCORES[target_region],
            'ecosystem_maturity': self.ECOSYSTEM_MATURITY[target_region],
            'english_proficiency': self.ENGLISH_PROFICIENCY[target_region],
            'timezone_overlap_hours': self.TIMEZONE_OVERLAP[target_region],
            'probability_boost': probability_boost,
            'is_critical_opportunity': is_critical,
            'recommended_action': self._generate_recommendation(
                arbitrage_score, 
                is_critical, 
                funding_region, 
                target_region
            )
        }
    
    def calculate_regional_opportunity_index(
        self,
        company_data: Dict,
        detected_regions: list
    ) -> Dict[str, any]:
        """
        Calculate unified regional opportunity index.
        
        Args:
            company_data: Company information (funding, location, etc.)
            detected_regions: List of regions mentioned in news/content
            
        Returns:
            Regional opportunity analysis
        """
        funding_region = company_data.get('region', 'USA')
        funding_amount = company_data.get('funding_amount', 0)
        
        opportunities = []
        
        # Analyze each detected region
        for target_region in detected_regions:
            if target_region == funding_region:
                continue  # Skip same region
            
            arbitrage = self.calculate_arbitrage_potential(
                funding_amount,
                funding_region,
                target_region
            )
            
            opportunities.append({
                'target_region': target_region,
                'arbitrage_score': arbitrage['arbitrage_score'],
                'cost_savings_pct': arbitrage['cost_savings_pct'],
                'probability_boost': arbitrage['probability_boost'],
                'is_critical': arbitrage['is_critical_opportunity'],
                'quality_score': arbitrage['quality_score']
            })
        
        # Sort by arbitrage score
        opportunities.sort(key=lambda x: x['arbitrage_score'], reverse=True)
        
        # Calculate overall regional opportunity index (0-100)
        if not opportunities:
            roi_score = 0
        else:
            # Weighted average of top 3 opportunities
            top_opportunities = opportunities[:3]
            roi_score = sum(opp['arbitrage_score'] for opp in top_opportunities) / len(top_opportunities)
        
        # Determine expansion strategy
        expansion_strategy = self._determine_expansion_strategy(opportunities, funding_region)
        
        return {
            'regional_opportunity_index': round(roi_score, 2),
            'funding_region': funding_region,
            'expansion_opportunities': opportunities,
            'top_target': opportunities[0]['target_region'] if opportunities else None,
            'expansion_strategy': expansion_strategy,
            'total_regions_analyzed': len(detected_regions),
            'critical_opportunities': sum(1 for o in opportunities if o['is_critical']),
            'timestamp': datetime.now().isoformat()
        }
    
    def _generate_recommendation(
        self,
        arbitrage_score: float,
        is_critical: bool,
        funding_region: str,
        target_region: str
    ) -> str:
        """Generate actionable recommendation."""
        if is_critical:
            return f"🔥 CRITICAL: {funding_region} company should establish delivery center in {target_region} immediately"
        elif arbitrage_score >= 70:
            return f"⚡ HIGH: Strong arbitrage opportunity in {target_region} - prioritize outreach"
        elif arbitrage_score >= 50:
            return f"📊 MODERATE: Consider {target_region} for cost optimization"
        else:
            return f"📋 LOW: Limited arbitrage potential in {target_region}"
    
    def _determine_expansion_strategy(
        self,
        opportunities: list,
        funding_region: str
    ) -> str:
        """Determine recommended expansion strategy."""
        if not opportunities:
            return "local_only"
        
        critical_count = sum(1 for o in opportunities if o['is_critical'])
        high_arbitrage = [o for o in opportunities if o['arbitrage_score'] >= 70]
        
        if critical_count >= 2:
            return "multi_region_latam"  # Expand to multiple LATAM countries
        elif critical_count == 1 or len(high_arbitrage) >= 2:
            return "single_region_latam"  # Focus on one LATAM country
        elif len(high_arbitrage) == 1:
            return "pilot_program"  # Start with small team
        else:
            return "monitor"  # Not ready for expansion yet
    
    def get_region_details(self, region: str) -> Dict[str, any]:
        """Get detailed information about a region."""
        if region not in self.TALENT_COSTS:
            return None
        
        return {
            'region': region,
            'talent_cost_usd': self.TALENT_COSTS[region],
            'stability_score': self.STABILITY_SCORES[region],
            'ecosystem_maturity': self.ECOSYSTEM_MATURITY[region],
            'english_proficiency': self.ENGLISH_PROFICIENCY[region],
            'timezone_overlap': self.TIMEZONE_OVERLAP[region],
            'latam_preference': self.LATAM_PREFERENCES.get(region, 0.5)
        }


def main():
    """
    Example usage of Regional Economic Analyzer.
    """
    print("🌎 Regional Economic Factor - Test Run\n")
    
    analyzer = RegionalEconomicAnalyzer()
    
    # Scenario 1: US company with $50M funding considering Colombia
    print("=" * 60)
    print("SCENARIO 1: US Startup ($50M) → Colombia Expansion")
    print("=" * 60)
    
    arbitrage = analyzer.calculate_arbitrage_potential(
        funding_amount=50_000_000,
        funding_region='USA',
        target_region='Colombia'
    )
    
    print(f"Arbitrage Score: {arbitrage['arbitrage_score']}/100")
    print(f"Cost Savings: ${arbitrage['cost_savings_usd']:,} per engineer ({arbitrage['cost_savings_pct']}%)")
    print(f"Extra Capacity: {arbitrage['extra_capacity']} more engineers")
    print(f"Quality Score: {arbitrage['quality_score']}/100")
    print(f"Probability Boost: +{arbitrage['probability_boost']} points")
    print(f"Critical Opportunity: {arbitrage['is_critical_opportunity']}")
    print(f"Recommendation: {arbitrage['recommended_action']}")
    
    # Scenario 2: Regional opportunity index
    print("\n" + "=" * 60)
    print("SCENARIO 2: Regional Opportunity Analysis")
    print("=" * 60)
    
    company_data = {
        'region': 'USA',
        'funding_amount': 75_000_000
    }
    
    detected_regions = ['Colombia', 'Argentina', 'Costa Rica', 'Mexico', 'Uruguay']
    
    roi_analysis = analyzer.calculate_regional_opportunity_index(
        company_data,
        detected_regions
    )
    
    print(f"Regional Opportunity Index: {roi_analysis['regional_opportunity_index']}/100")
    print(f"Top Target: {roi_analysis['top_target']}")
    print(f"Expansion Strategy: {roi_analysis['expansion_strategy']}")
    print(f"Critical Opportunities: {roi_analysis['critical_opportunities']}")
    
    print("\nTop 3 Expansion Opportunities:")
    for i, opp in enumerate(roi_analysis['expansion_opportunities'][:3], 1):
        print(f"  {i}. {opp['target_region']}: {opp['arbitrage_score']:.1f} score "
              f"({opp['cost_savings_pct']:.0f}% savings, +{opp['probability_boost']} boost)")
    
    print("\n✅ Regional Economic analysis complete!")


# Compatibility layer for standalone function imports
REGIONAL_DATA = {
    'USA': {
        'cost_multiplier': 1.0,
        'talent_pool': 1_500_000,
        'tech_ecosystem': 100,
        'offshore_appeal': 5
    },
    'Canada': {
        'cost_multiplier': 0.66,
        'talent_pool': 300_000,
        'tech_ecosystem': 90,
        'offshore_appeal': 6
    },
    'Mexico': {
        'cost_multiplier': 0.29,
        'talent_pool': 200_000,
        'tech_ecosystem': 65,
        'offshore_appeal': 7
    },
    'Argentina': {
        'cost_multiplier': 0.26,
        'talent_pool': 150_000,
        'tech_ecosystem': 75,
        'offshore_appeal': 9
    },
    'Uruguay': {
        'cost_multiplier': 0.31,
        'talent_pool': 30_000,
        'tech_ecosystem': 72,
        'offshore_appeal': 8
    },
    'Chile': {
        'cost_multiplier': 0.33,
        'talent_pool': 100_000,
        'tech_ecosystem': 68,
        'offshore_appeal': 7
    },
    'Colombia': {
        'cost_multiplier': 0.24,
        'talent_pool': 180_000,
        'tech_ecosystem': 60,
        'offshore_appeal': 10
    },
    'Costa Rica': {
        'cost_multiplier': 0.28,
        'talent_pool': 50_000,
        'tech_ecosystem': 70,
        'offshore_appeal': 9
    }
}


def calculate_arbitrage_potential(funding_amount: float, region: str) -> float:
    """
    Standalone function for quick arbitrage calculation.
    Assumes USA as funding region.
    
    Args:
        funding_amount: Funding raised in USD
        region: Target hiring region
        
    Returns:
        Arbitrage score (0-100)
    """
    analyzer = RegionalEconomicAnalyzer()
    result = analyzer.calculate_arbitrage_potential(
        funding_amount=funding_amount,
        funding_region='USA',
        target_region=region
    )
    return result['arbitrage_score']


if __name__ == '__main__':
    main()
