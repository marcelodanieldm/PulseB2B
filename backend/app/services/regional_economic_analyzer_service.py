"""
RegionalEconomicAnalyzer Service (migrated from legacy script)
"""
from typing import Dict, Any

class RegionalEconomicAnalyzer:
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
    TIMEZONE_OVERLAP = {
        'USA': 8,
        'Canada': 8,
        'Mexico': 7,
        'Argentina': 4,
        'Uruguay': 4,
        'Chile': 4,
        'Colombia': 8,
        'Costa Rica': 8
    }
    LATAM_PREFERENCES = {
        'Colombia': 1.0,
        'Costa Rica': 0.95,
        'Argentina': 0.90,
        'Uruguay': 0.85,
        'Chile': 0.80,
        'Mexico': 0.75
    }
    def calculate_arbitrage_potential(self, funding_amount: float, funding_region: str, target_region: str) -> Dict[str, Any]:
        if funding_region not in self.TALENT_COSTS or target_region not in self.TALENT_COSTS:
            return {
                'arbitrage_score': 0,
                'cost_savings': 0,
                'probability_boost': 0,
                'recommendation': 'Unknown region'
            }
        funding_cost = self.TALENT_COSTS[funding_region]
        target_cost = self.TALENT_COSTS[target_region]
        cost_savings = funding_cost - target_cost
        cost_savings_pct = (cost_savings / funding_cost) * 100
        engineers_in_funding_region = funding_amount / funding_cost
        engineers_in_target_region = funding_amount / target_cost
        extra_capacity = engineers_in_target_region - engineers_in_funding_region
        quality_score = (
            self.STABILITY_SCORES[target_region] * 0.25 +
            self.ECOSYSTEM_MATURITY[target_region] * 0.20 +
            self.ENGLISH_PROFICIENCY[target_region] * 0.20 +
            (self.TIMEZONE_OVERLAP[target_region] / 8 * 100) * 0.20 +
            (self.LATAM_PREFERENCES.get(target_region, 0.5) * 100) * 0.15
        )
        arbitrage_score = (cost_savings_pct * 0.6) + (quality_score * 0.4)
        arbitrage_score = min(100, max(0, arbitrage_score))
        if arbitrage_score >= 70:
            probability_boost = 25
        elif arbitrage_score >= 50:
            probability_boost = 15
        elif arbitrage_score >= 30:
            probability_boost = 10
        else:
            probability_boost = 0
        is_critical = (
            funding_region in ['USA', 'Canada'] and
            target_region in ['Colombia', 'Argentina', 'Costa Rica', 'Uruguay'] and
            funding_amount >= 10_000_000
        )
        recommendation = 'CRITICAL: Expand immediately' if is_critical else 'Monitor opportunity'
        return {
            'arbitrage_score': round(arbitrage_score, 1),
            'cost_savings': int(cost_savings),
            'cost_savings_pct': round(cost_savings_pct, 1),
            'extra_capacity': int(extra_capacity),
            'probability_boost': probability_boost,
            'is_critical': is_critical,
            'recommendation': recommendation
        }

# Singleton instance
regional_economic_analyzer = RegionalEconomicAnalyzer()
