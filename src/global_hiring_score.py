"""
Global Hiring Score (GHS) Calculator
-------------------------------------
Calculates the likelihood that a US tech company needs to hire offshore talent
based on their funding-to-cost ratio and market indicators.

Formula: GHS = (Funding Amount / Median US Tech Salary) * Multipliers

The higher the GHS, the more developers they can afford. If the ratio is low
relative to their stated hiring needs, they MUST hire offshore.
"""

import logging
from typing import Dict, Optional, List
from dataclasses import dataclass
from enum import Enum

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class HiringUrgency(Enum):
    """Hiring urgency levels based on GHS score."""
    CRITICAL = "Critical - Must hire offshore immediately"
    HIGH = "High - Likely needs offshore talent"
    MEDIUM = "Medium - May consider offshore"
    LOW = "Low - Can afford US-only hiring"
    UNKNOWN = "Unknown - Insufficient data"


@dataclass
class MarketSalaryData:
    """
    Market salary data for different roles and regions.
    Source: 2024-2025 market averages.
    """
    # US Tech Salaries (annual, USD)
    US_SOFTWARE_ENGINEER_MEDIAN: int = 120000
    US_SENIOR_ENGINEER_MEDIAN: int = 160000
    US_STAFF_ENGINEER_MEDIAN: int = 200000
    US_ENGINEERING_MANAGER_MEDIAN: int = 180000
    
    # Offshore Salaries (annual, USD)
    LATAM_SOFTWARE_ENGINEER_MEDIAN: int = 45000
    LATAM_SENIOR_ENGINEER_MEDIAN: int = 60000
    EASTERN_EUROPE_SOFTWARE_ENGINEER_MEDIAN: int = 50000
    EASTERN_EUROPE_SENIOR_ENGINEER_MEDIAN: int = 70000
    
    # Cost multipliers (includes benefits, overhead, etc.)
    US_TOTAL_COST_MULTIPLIER: float = 1.4  # 40% overhead
    OFFSHORE_TOTAL_COST_MULTIPLIER: float = 1.25  # 25% overhead
    
    @property
    def us_engineer_total_cost(self) -> int:
        """Total annual cost for US software engineer."""
        return int(self.US_SOFTWARE_ENGINEER_MEDIAN * self.US_TOTAL_COST_MULTIPLIER)
    
    @property
    def offshore_engineer_total_cost(self) -> int:
        """Total annual cost for offshore software engineer."""
        return int(self.LATAM_SOFTWARE_ENGINEER_MEDIAN * self.OFFSHORE_TOTAL_COST_MULTIPLIER)
    
    @property
    def cost_savings_per_engineer(self) -> int:
        """Annual savings per engineer when hiring offshore."""
        return self.us_engineer_total_cost - self.offshore_engineer_total_cost


class GlobalHiringScoreCalculator:
    """
    Calculates Global Hiring Score (GHS) to determine offshore hiring necessity.
    
    The GHS is calculated as:
    GHS = (Total Funding / US Engineer Cost) * Urgency Multiplier * Growth Multiplier
    
    A low GHS relative to hiring goals indicates need for offshore talent.
    """
    
    def __init__(self):
        """Initialize the GHS calculator with market data."""
        self.salary_data = MarketSalaryData()
        
        # Urgency multipliers based on company signals
        self.urgency_multipliers = {
            'immediate_hiring': 2.0,  # "Hiring now", "Urgent need"
            'expansion': 1.5,  # "Expanding team", "Scaling up"
            'growth': 1.2,  # "Growing", "Opportunity"
            'standard': 1.0,  # Normal hiring pace
            'slow': 0.8,  # "Future hiring", "Planning"
        }
        
        # Stage multipliers (earlier stage = more cost-conscious)
        self.stage_multipliers = {
            'seed': 1.5,  # Most cost-sensitive
            'series_a': 1.3,
            'series_b': 1.2,
            'series_c': 1.1,
            'series_d_plus': 1.0,
            'public': 0.9,
        }
    
    def calculate_ghs(
        self,
        funding_amount: float,
        company_stage: str = 'series_a',
        urgency_level: str = 'standard',
        stated_headcount_goal: Optional[int] = None,
        current_team_size: Optional[int] = None
    ) -> Dict:
        """
        Calculate Global Hiring Score and offshore hiring recommendation.
        
        Args:
            funding_amount: Total funding raised (USD)
            company_stage: Funding stage (seed, series_a, series_b, etc.)
            urgency_level: Hiring urgency (immediate_hiring, expansion, growth, etc.)
            stated_headcount_goal: Number of engineers they plan to hire
            current_team_size: Current number of engineers
        
        Returns:
            Dictionary with GHS score and analysis
        """
        # Get multipliers
        stage_mult = self.stage_multipliers.get(company_stage.lower(), 1.0)
        urgency_mult = self.urgency_multipliers.get(urgency_level.lower(), 1.0)
        
        # Base calculation: How many US engineers can they afford?
        us_engineer_cost = self.salary_data.us_engineer_total_cost
        affordable_us_engineers = funding_amount / us_engineer_cost
        
        # Calculate GHS with multipliers
        raw_ghs = affordable_us_engineers * stage_mult * urgency_mult
        
        # Determine offshore necessity
        offshore_recommendation = self._determine_offshore_necessity(
            affordable_us_engineers=affordable_us_engineers,
            stated_goal=stated_headcount_goal,
            current_size=current_team_size,
            funding_amount=funding_amount
        )
        
        # Calculate potential savings with offshore hiring
        savings_analysis = self._calculate_savings_analysis(
            stated_headcount_goal or 0,
            funding_amount
        )
        
        # Determine hiring urgency
        urgency = self._determine_urgency(
            raw_ghs,
            offshore_recommendation['offshore_percentage']
        )
        
        return {
            'global_hiring_score': round(raw_ghs, 2),
            'affordable_us_engineers': int(affordable_us_engineers),
            'funding_amount': funding_amount,
            'company_stage': company_stage,
            'urgency_level': urgency_level,
            'hiring_urgency': urgency.value,
            'offshore_recommendation': offshore_recommendation,
            'savings_analysis': savings_analysis,
            'market_context': {
                'us_engineer_annual_cost': us_engineer_cost,
                'offshore_engineer_annual_cost': self.salary_data.offshore_engineer_total_cost,
                'cost_savings_per_engineer': self.salary_data.cost_savings_per_engineer,
            },
            'multipliers_applied': {
                'stage_multiplier': stage_mult,
                'urgency_multiplier': urgency_mult,
                'combined_multiplier': stage_mult * urgency_mult
            }
        }
    
    def _determine_offshore_necessity(
        self,
        affordable_us_engineers: float,
        stated_goal: Optional[int],
        current_size: Optional[int],
        funding_amount: float
    ) -> Dict:
        """
        Determine the necessity and percentage of offshore hiring.
        
        Args:
            affordable_us_engineers: Number of US engineers affordable with funding
            stated_goal: Stated hiring goal
            current_size: Current team size
            funding_amount: Total funding
        
        Returns:
            Dictionary with offshore hiring recommendation
        """
        recommendation = {
            'must_hire_offshore': False,
            'offshore_percentage': 0,
            'reason': '',
            'recommended_mix': {}
        }
        
        if stated_goal is None:
            # Estimate based on funding stage
            if funding_amount < 5_000_000:  # Seed/Early A
                estimated_goal = int(affordable_us_engineers * 0.3)  # Use 30% of funding for hiring
            elif funding_amount < 20_000_000:  # Series A/B
                estimated_goal = int(affordable_us_engineers * 0.4)
            else:  # Series C+
                estimated_goal = int(affordable_us_engineers * 0.5)
            
            stated_goal = max(estimated_goal, 5)  # Minimum 5 engineers
        
        # Calculate hiring gap
        hiring_gap = stated_goal
        if current_size:
            hiring_gap = max(stated_goal - current_size, 0)
        
        # Determine offshore necessity
        if affordable_us_engineers < hiring_gap:
            # Cannot afford to hire all US - MUST go offshore
            recommendation['must_hire_offshore'] = True
            
            # Calculate optimal mix
            us_hires = int(affordable_us_engineers * 0.6)  # Use 60% of budget for US leads
            remaining_budget = funding_amount - (us_hires * self.salary_data.us_engineer_total_cost)
            offshore_hires = int(remaining_budget / self.salary_data.offshore_engineer_total_cost)
            
            total_hires = us_hires + offshore_hires
            offshore_pct = (offshore_hires / total_hires * 100) if total_hires > 0 else 0
            
            recommendation['offshore_percentage'] = round(offshore_pct, 1)
            recommendation['reason'] = (
                f"Funding only covers {int(affordable_us_engineers)} US engineers, "
                f"but need to hire {hiring_gap}. Must hire {offshore_pct:.0f}% offshore."
            )
            recommendation['recommended_mix'] = {
                'us_engineers': us_hires,
                'offshore_engineers': offshore_hires,
                'total_engineers': total_hires,
                'offshore_percentage': offshore_pct
            }
            
        elif affordable_us_engineers < hiring_gap * 1.5:
            # Tight budget - Should consider offshore for efficiency
            recommendation['must_hire_offshore'] = False
            recommendation['offshore_percentage'] = 40.0
            recommendation['reason'] = (
                f"Can afford all US hiring but budget is tight. "
                f"Recommend 40% offshore for capital efficiency."
            )
            
            us_hires = int(hiring_gap * 0.6)
            offshore_hires = int(hiring_gap * 0.4)
            
            recommendation['recommended_mix'] = {
                'us_engineers': us_hires,
                'offshore_engineers': offshore_hires,
                'total_engineers': us_hires + offshore_hires,
                'offshore_percentage': 40.0
            }
            
        else:
            # Comfortable budget - Can do all US but offshore is still strategic
            recommendation['must_hire_offshore'] = False
            recommendation['offshore_percentage'] = 20.0
            recommendation['reason'] = (
                f"Sufficient funding for all-US team, but 20% offshore "
                f"recommended for 24/7 coverage and cost optimization."
            )
            
            us_hires = int(hiring_gap * 0.8)
            offshore_hires = int(hiring_gap * 0.2)
            
            recommendation['recommended_mix'] = {
                'us_engineers': us_hires,
                'offshore_engineers': offshore_hires,
                'total_engineers': us_hires + offshore_hires,
                'offshore_percentage': 20.0
            }
        
        return recommendation
    
    def _calculate_savings_analysis(
        self,
        target_hires: int,
        available_budget: float
    ) -> Dict:
        """
        Calculate potential savings with different offshore percentages.
        
        Args:
            target_hires: Number of engineers to hire
            available_budget: Available budget
        
        Returns:
            Dictionary with savings scenarios
        """
        if target_hires == 0:
            target_hires = 10  # Default assumption
        
        # Calculate costs for different offshore percentages
        scenarios = {}
        
        for offshore_pct in [0, 20, 40, 60, 80, 100]:
            offshore_count = int(target_hires * offshore_pct / 100)
            us_count = target_hires - offshore_count
            
            total_cost = (
                us_count * self.salary_data.us_engineer_total_cost +
                offshore_count * self.salary_data.offshore_engineer_total_cost
            )
            
            scenarios[f'{offshore_pct}%_offshore'] = {
                'us_engineers': us_count,
                'offshore_engineers': offshore_count,
                'total_annual_cost': total_cost,
                'within_budget': total_cost <= available_budget,
                'savings_vs_all_us': (
                    (target_hires * self.salary_data.us_engineer_total_cost) - total_cost
                )
            }
        
        return {
            'target_hires': target_hires,
            'available_budget': available_budget,
            'scenarios': scenarios
        }
    
    def _determine_urgency(
        self,
        ghs_score: float,
        offshore_percentage: float
    ) -> HiringUrgency:
        """
        Determine hiring urgency based on GHS and offshore necessity.
        
        Args:
            ghs_score: Global Hiring Score
            offshore_percentage: Recommended offshore percentage
        
        Returns:
            HiringUrgency enum value
        """
        if offshore_percentage >= 60:
            return HiringUrgency.CRITICAL
        elif offshore_percentage >= 40:
            return HiringUrgency.HIGH
        elif offshore_percentage >= 20:
            return HiringUrgency.MEDIUM
        elif ghs_score > 50:
            return HiringUrgency.LOW
        else:
            return HiringUrgency.UNKNOWN
    
    def calculate_roi_offshore(
        self,
        team_size: int,
        offshore_percentage: float,
        project_duration_months: int = 12
    ) -> Dict:
        """
        Calculate ROI of offshore hiring strategy.
        
        Args:
            team_size: Total team size
            offshore_percentage: Percentage of team that's offshore (0-100)
            project_duration_months: Project duration in months
        
        Returns:
            Dictionary with ROI analysis
        """
        offshore_count = int(team_size * offshore_percentage / 100)
        us_count = team_size - offshore_count
        
        # Annual costs
        all_us_cost = team_size * self.salary_data.us_engineer_total_cost
        mixed_cost = (
            us_count * self.salary_data.us_engineer_total_cost +
            offshore_count * self.salary_data.offshore_engineer_total_cost
        )
        
        # Project costs
        project_cost_all_us = all_us_cost * (project_duration_months / 12)
        project_cost_mixed = mixed_cost * (project_duration_months / 12)
        
        savings = project_cost_all_us - project_cost_mixed
        savings_percentage = (savings / project_cost_all_us * 100) if project_cost_all_us > 0 else 0
        
        return {
            'team_composition': {
                'total_team_size': team_size,
                'us_engineers': us_count,
                'offshore_engineers': offshore_count,
                'offshore_percentage': offshore_percentage
            },
            'annual_costs': {
                'all_us_team': all_us_cost,
                'mixed_team': mixed_cost,
                'annual_savings': all_us_cost - mixed_cost
            },
            'project_costs': {
                'duration_months': project_duration_months,
                'all_us_team': project_cost_all_us,
                'mixed_team': project_cost_mixed,
                'total_savings': savings,
                'savings_percentage': round(savings_percentage, 1)
            },
            'additional_benefits': [
                '24/7 development coverage',
                'Access to global talent pool',
                'Faster time to market',
                'Risk diversification',
                'Knowledge transfer opportunities'
            ]
        }


# Example usage and testing
if __name__ == "__main__":
    calculator = GlobalHiringScoreCalculator()
    
    # Example 1: Series A startup with tight budget
    print("="*60)
    print("EXAMPLE 1: Series A Startup")
    print("="*60)
    
    result1 = calculator.calculate_ghs(
        funding_amount=8_000_000,  # $8M Series A
        company_stage='series_a',
        urgency_level='expansion',
        stated_headcount_goal=15,
        current_team_size=5
    )
    
    print(f"\nGlobal Hiring Score: {result1['global_hiring_score']}")
    print(f"Affordable US Engineers: {result1['affordable_us_engineers']}")
    print(f"Hiring Urgency: {result1['hiring_urgency']}")
    print(f"\nOffshore Recommendation:")
    print(f"  Must Hire Offshore: {result1['offshore_recommendation']['must_hire_offshore']}")
    print(f"  Offshore %: {result1['offshore_recommendation']['offshore_percentage']}%")
    print(f"  Reason: {result1['offshore_recommendation']['reason']}")
    print(f"\nRecommended Mix:")
    mix = result1['offshore_recommendation']['recommended_mix']
    print(f"  US Engineers: {mix['us_engineers']}")
    print(f"  Offshore Engineers: {mix['offshore_engineers']}")
    print(f"  Total: {mix['total_engineers']}")
    
    # Example 2: Well-funded Series C
    print("\n" + "="*60)
    print("EXAMPLE 2: Well-funded Series C")
    print("="*60)
    
    result2 = calculator.calculate_ghs(
        funding_amount=50_000_000,  # $50M Series C
        company_stage='series_c',
        urgency_level='growth',
        stated_headcount_goal=25,
        current_team_size=20
    )
    
    print(f"\nGlobal Hiring Score: {result2['global_hiring_score']}")
    print(f"Affordable US Engineers: {result2['affordable_us_engineers']}")
    print(f"Hiring Urgency: {result2['hiring_urgency']}")
    print(f"\nOffshore Recommendation:")
    print(f"  Must Hire Offshore: {result2['offshore_recommendation']['must_hire_offshore']}")
    print(f"  Offshore %: {result2['offshore_recommendation']['offshore_percentage']}%")
    print(f"  Reason: {result2['offshore_recommendation']['reason']}")
    
    # ROI Analysis
    print("\n" + "="*60)
    print("ROI ANALYSIS: 40% Offshore Team")
    print("="*60)
    
    roi = calculator.calculate_roi_offshore(
        team_size=20,
        offshore_percentage=40,
        project_duration_months=12
    )
    
    print(f"\nTeam Composition:")
    print(f"  US Engineers: {roi['team_composition']['us_engineers']}")
    print(f"  Offshore Engineers: {roi['team_composition']['offshore_engineers']}")
    print(f"\nAnnual Cost Comparison:")
    print(f"  All US Team: ${roi['annual_costs']['all_us_team']:,.0f}")
    print(f"  Mixed Team: ${roi['annual_costs']['mixed_team']:,.0f}")
    print(f"  Annual Savings: ${roi['annual_costs']['annual_savings']:,.0f}")
    print(f"\n12-Month Project Savings:")
    print(f"  Total Savings: ${roi['project_costs']['total_savings']:,.0f}")
    print(f"  Savings %: {roi['project_costs']['savings_percentage']}%")
    
    print("\n" + "="*60)
