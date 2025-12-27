import logging
from typing import List, Dict, Optional, Tuple
from datetime import datetime
from app.services.osint_lead_scorer_base import OSINTLeadScorer as LegacyOSINTLeadScorer


class OSINTLeadScorer(LegacyOSINTLeadScorer):
    """
    FastAPI-adapted OSINT Lead Scorer service.
    Inherits all logic from the legacy OSINTLeadScorer.
    """
    pass

# Singleton instance for use in services and routers
osint_lead_scorer = OSINTLeadScorer()
