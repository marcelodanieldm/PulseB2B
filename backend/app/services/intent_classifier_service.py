
import logging
from app.services.intent_classifier_base import OutsourcingIntentClassifier as LegacyOutsourcingIntentClassifier

class OutsourcingIntentClassifier(LegacyOutsourcingIntentClassifier):
    """
    FastAPI-adapted Outsourcing Intent Classifier service.
    Inherits all logic from the legacy OutsourcingIntentClassifier.
    """
    pass

# Singleton instance for use in services and routers
intent_classifier = OutsourcingIntentClassifier(use_transformers=False)
