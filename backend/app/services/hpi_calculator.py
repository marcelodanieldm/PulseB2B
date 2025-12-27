import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict
from sklearn.preprocessing import MinMaxScaler
import logging

logger = logging.getLogger(__name__)

class HPICalculator:
    def __init__(self):
        self.scaler = MinMaxScaler(feature_range=(0, 100))

    def calculate_funding_recency_score(self, last_funding_date: str) -> Dict:
        try:
            funding_date = pd.to_datetime(last_funding_date)
            today = pd.Timestamp.now()
            days_since = (today - funding_date).days
            if days_since <= 180:
                score = 100 - (days_since / 180) * 15
                tier = 'Very Recent'
            elif days_since <= 365:
                score = 85 - ((days_since - 180) / 185) * 25
                tier = 'Recent'
            elif days_since <= 545:
                score = 60 - ((days_since - 365) / 180) * 25
                tier = 'Moderate'
            elif days_since <= 730:
                score = 35 - ((days_since - 545) / 185) * 20
                tier = 'Old'
            else:
                score = max(0, 15 - ((days_since - 730) / 365) * 10)
                tier = 'Very Old'
            return {"score": score, "tier": tier}
        except Exception as e:
            logger.error(f"Error calculating funding recency score: {e}")
            return {"score": 0, "tier": "Unknown"}
