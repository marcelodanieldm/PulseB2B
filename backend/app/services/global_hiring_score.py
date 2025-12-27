from enum import Enum
from dataclasses import dataclass
import logging
from typing import Dict

logger = logging.getLogger(__name__)

class HiringUrgency(Enum):
    CRITICAL = "Critical - Must hire offshore immediately"
    HIGH = "High - Likely needs offshore talent"
    MEDIUM = "Medium - May consider offshore"
    LOW = "Low - Can afford US-only hiring"
    UNKNOWN = "Unknown - Insufficient data"

@dataclass
class MarketSalaryData:
    us_tech_salary: float = 140000.0
    offshore_salary: float = 35000.0

class GlobalHiringScoreCalculator:
    def calculate_ghs(self, funding_amount: float, median_salary: float = 140000.0) -> float:
        if median_salary == 0:
            return 0.0
        return funding_amount / median_salary

    def get_urgency(self, ghs: float) -> HiringUrgency:
        if ghs < 0.5:
            return HiringUrgency.CRITICAL
        elif ghs < 1.0:
            return HiringUrgency.HIGH
        elif ghs < 2.0:
            return HiringUrgency.MEDIUM
        elif ghs >= 2.0:
            return HiringUrgency.LOW
        else:
            return HiringUrgency.UNKNOWN
