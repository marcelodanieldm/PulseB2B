import logging
from typing import Dict, List, Optional, Tuple
import re

try:
    from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
    import torch
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False
    logging.warning(
        "HuggingFace transformers not available. "
        "Install with: pip install transformers torch"
    )

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class OutsourcingIntentClassifier:
    """
    Legacy Outsourcing Intent Classifier logic (from src/intent_classifier.py)
    """
    def __init__(self, use_transformers: bool = True, device: str = "cpu"):
        self.use_transformers = use_transformers and TRANSFORMERS_AVAILABLE
        self.device = device
        self.classifier = None
        self.sentiment_analyzer = None
        if self.use_transformers:
            self._initialize_models()

    def _initialize_models(self):
        try:
            logger.info("Initializing HuggingFace models...")
            self.classifier = pipeline(
                "zero-shot-classification",
                model="facebook/bart-large-mnli",
                device=0 if self.device == "cuda" and torch.cuda.is_available() else -1
            )
            self.sentiment_analyzer = pipeline(
                "sentiment-analysis",
                model="distilbert-base-uncased-finetuned-sst-2-english",
                device=0 if self.device == "cuda" and torch.cuda.is_available() else -1
            )
            logger.info("Models initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing models: {e}")
            logger.warning("Falling back to keyword-only classification")
            self.use_transformers = False

    # ... (other methods from src/intent_classifier.py)
