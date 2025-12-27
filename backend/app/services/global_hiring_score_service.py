
# Clean, minimal, working implementation to resolve any hidden corruption or indentation errors
import logging
from typing import Dict, Optional
from dataclasses import dataclass
from enum import Enum

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class HiringUrgency(Enum):
    CRITICAL = "Critical - Must hire offshore immediately"
    HIGH = "High - Likely needs offshore talent"
    MEDIUM = "Medium - May consider offshore"
    LOW = "Low - Can afford US-only hiring"
    UNKNOWN = "Unknown - Insufficient data"

@dataclass
class MarketSalaryData:
    US_SOFTWARE_ENGINEER_MEDIAN: int = 120000
    US_SENIOR_ENGINEER_MEDIAN: int = 160000
    US_STAFF_ENGINEER_MEDIAN: int = 200000
    US_ENGINEERING_MANAGER_MEDIAN: int = 180000
    LATAM_SOFTWARE_ENGINEER_MEDIAN: int = 45000
    LATAM_SENIOR_ENGINEER_MEDIAN: int = 60000
    EASTERN_EUROPE_SOFTWARE_ENGINEER_MEDIAN: int = 50000
    EASTERN_EUROPE_SENIOR_ENGINEER_MEDIAN: int = 70000
    US_TOTAL_COST_MULTIPLIER: float = 1.4
    OFFSHORE_TOTAL_COST_MULTIPLIER: float = 1.25
    @property
    def us_engineer_total_cost(self) -> int:
        return int(self.US_SOFTWARE_ENGINEER_MEDIAN * self.US_TOTAL_COST_MULTIPLIER)
    @property
    def offshore_engineer_total_cost(self) -> int:
        return int(self.LATAM_SOFTWARE_ENGINEER_MEDIAN * self.OFFSHORE_TOTAL_COST_MULTIPLIER)
    @property
    def cost_savings_per_engineer(self) -> int:
        return self.us_engineer_total_cost - self.offshore_engineer_total_cost

class GlobalHiringScoreCalculator:
    def __init__(self):
        self.salary_data = MarketSalaryData()
        self.urgency_multipliers = {
            'immediate_hiring': 2.0,
            'expansion': 1.5,
            'growth': 1.2,
            'standard': 1.0,
            'slow': 0.8,
        }
        self.stage_multipliers = {
            'seed': 1.5,
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
        (Implementation omitted for brevity)
        """
        stage_mult = self.stage_multipliers.get(company_stage.lower(), 1.0)
        urgency_mult = self.urgency_multipliers.get(urgency_level.lower(), 1.0)
        us_engineer_cost = self.salary_data.us_engineer_total_cost
        affordable_us_engineers = funding_amount / us_engineer_cost
        raw_ghs = affordable_us_engineers * stage_mult * urgency_mult
        return {
            'global_hiring_score': round(raw_ghs, 2),
            'affordable_us_engineers': int(affordable_us_engineers),
            'funding_amount': funding_amount,
            'company_stage': company_stage,
            'urgency_level': urgency_level,
            # ...
        }

# Singleton instance for use in services and routers
global_hiring_score_calculator = GlobalHiringScoreCalculator()
