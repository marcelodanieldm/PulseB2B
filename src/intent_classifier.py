"""
HuggingFace Transformers-based Intent Classifier
-------------------------------------------------
Uses pre-trained NLP models to detect outsourcing intent in company descriptions
and job postings. Identifies keywords like 'Remote-friendly', 'Global team',
'Distributed', 'LATAM/EMEA timezones'.
"""

import logging
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
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


@dataclass
class OutsourcingSignals:
    """Data class for outsourcing intent signals."""
    remote_work_signals: List[str] = field(default_factory=list)
    global_team_signals: List[str] = field(default_factory=list)
    timezone_signals: List[str] = field(default_factory=list)
    distribution_signals: List[str] = field(default_factory=list)
    cost_efficiency_signals: List[str] = field(default_factory=list)
    
    def total_signals(self) -> int:
        """Return total number of signals detected."""
        return (
            len(self.remote_work_signals) +
            len(self.global_team_signals) +
            len(self.timezone_signals) +
            len(self.distribution_signals) +
            len(self.cost_efficiency_signals)
        )
    
    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            'remote_work': self.remote_work_signals,
            'global_team': self.global_team_signals,
            'timezone': self.timezone_signals,
            'distribution': self.distribution_signals,
            'cost_efficiency': self.cost_efficiency_signals,
            'total_signals': self.total_signals()
        }


class OutsourcingIntentClassifier:
    """
    NLP-based classifier for detecting outsourcing intent in text.
    
    Uses HuggingFace transformers for:
    - Zero-shot classification
    - Named Entity Recognition
    - Sentiment analysis
    - Keyword extraction
    """
    
    # Comprehensive keyword patterns for outsourcing intent
    KEYWORD_PATTERNS = {
        'remote_work': [
            r'\bremote[-\s]friendly\b',
            r'\bremote[-\s]first\b',
            r'\bremote work\b',
            r'\bwork from anywhere\b',
            r'\bfully remote\b',
            r'\b100% remote\b',
            r'\bhybrid remote\b',
            r'\bremote[-\s]optional\b',
            r'\bdistributed workforce\b',
            r'\bwork remotely\b',
        ],
        'global_team': [
            r'\bglobal team\b',
            r'\binternational team\b',
            r'\bworldwide team\b',
            r'\bmulti[-\s]national team\b',
            r'\bteam across \w+ countries\b',
            r'\bglobal workforce\b',
            r'\bglobal talent\b',
            r'\binternational talent\b',
            r'\bdiverse team\b',
            r'\bcross[-\s]border team\b',
        ],
        'timezone': [
            r'\blatam timezone\b',
            r'\bemea timezone\b',
            r'\bapac timezone\b',
            r'\basia timezone\b',
            r'\beurope timezone\b',
            r'\bmultiple timezones\b',
            r'\btime[-\s]zone flexible\b',
            r'\ball timezones\b',
            r'\b24/?7 coverage\b',
            r'\bfollow[-\s]the[-\s]sun\b',
            r'\bgmt[-+]\d+\b',
            r'\bist\b|\best\b|\bpst\b|\bcet\b',  # Timezone abbreviations
        ],
        'distribution': [
            r'\bdistributed team\b',
            r'\bdistributed company\b',
            r'\bdistributed[-\s]first\b',
            r'\bfully distributed\b',
            r'\bglobally distributed\b',
            r'\bdecentralized team\b',
            r'\basynchronous work\b',
            r'\basync[-\s]first\b',
            r'\blocation[-\s]independent\b',
            r'\bno office\b',
        ],
        'cost_efficiency': [
            r'\bcost[-\s]effective\b',
            r'\bbudget[-\s]conscious\b',
            r'\bcompetitive rates\b',
            r'\baffordable talent\b',
            r'\boptimize costs\b',
            r'\befficient hiring\b',
            r'\bscale efficiently\b',
            r'\bresource optimization\b',
        ],
        'offshore_explicit': [
            r'\boffshore\b',
            r'\bnearshore\b',
            r'\boutsource\b',
            r'\boutsourcing\b',
            r'\boffshore development\b',
            r'\bnearshore development\b',
            r'\boutsorc(?:e|ing)\b',
            r'\bcontract\w*\s+developer',
            r'\bfreelance\b',
        ],
        'latam_specific': [
            r'\blatam\b',
            r'\blatin america\b',
            r'\bmexico\b',
            r'\bbrazil\b',
            r'\bargentina\b',
            r'\bcolombia\b',
            r'\bchile\b',
            r'\bcosta rica\b',
            r'\bcentral america\b',
            r'\bsouth america\b',
        ],
        'emea_specific': [
            r'\bemea\b',
            r'\beastern europe\b',
            r'\bukraine\b',
            r'\bpoland\b',
            r'\bromania\b',
            r'\bczech\b',
            r'\bportugal\b',
            r'\bspain\b',
            r'\bmiddle east\b',
            r'\bafrica\b',
        ]
    }
    
    def __init__(self, use_transformers: bool = True, device: str = "cpu"):
        """
        Initialize the intent classifier.
        
        Args:
            use_transformers: Whether to use HuggingFace transformers
            device: Device to run models on ('cpu' or 'cuda')
        """
        self.use_transformers = use_transformers and TRANSFORMERS_AVAILABLE
        self.device = device
        self.classifier = None
        self.sentiment_analyzer = None
        
        if self.use_transformers:
            self._initialize_models()
    
    def _initialize_models(self):
        """Initialize HuggingFace models."""
        try:
            logger.info("Initializing HuggingFace models...")
            
            # Zero-shot classification model for intent detection
            self.classifier = pipeline(
                "zero-shot-classification",
                model="facebook/bart-large-mnli",
                device=0 if self.device == "cuda" and torch.cuda.is_available() else -1
            )
            
            # Sentiment analysis for company culture detection
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
    
    def detect_outsourcing_intent(
        self,
        text: str,
        use_ml: bool = True
    ) -> Dict:
        """
        Detect outsourcing intent in text using NLP and keyword analysis.
        
        Args:
            text: Text to analyze (company description, job post, etc.)
            use_ml: Whether to use ML models (if available)
        
        Returns:
            Dictionary with intent classification results
        """
        text_lower = text.lower()
        
        # 1. Keyword-based signal detection
        signals = self._detect_keyword_signals(text_lower)
        
        # 2. ML-based classification (if available and requested)
        ml_scores = None
        if use_ml and self.use_transformers and self.classifier:
            ml_scores = self._classify_with_ml(text)
        
        # 3. Calculate intent score
        intent_score = self._calculate_intent_score(signals, ml_scores)
        
        # 4. Determine intent level
        intent_level = self._determine_intent_level(intent_score)
        
        return {
            'outsourcing_intent_detected': intent_score >= 30,
            'intent_score': intent_score,
            'intent_level': intent_level,
            'signals': signals.to_dict(),
            'ml_classification': ml_scores,
            'confidence': self._calculate_confidence(signals, ml_scores)
        }
    
    def _detect_keyword_signals(self, text: str) -> OutsourcingSignals:
        """
        Detect outsourcing signals using keyword patterns.
        
        Args:
            text: Lowercase text to analyze
        
        Returns:
            OutsourcingSignals object with detected keywords
        """
        signals = OutsourcingSignals()
        
        # Remote work signals
        for pattern in self.KEYWORD_PATTERNS['remote_work']:
            matches = re.findall(pattern, text, re.IGNORECASE)
            signals.remote_work_signals.extend(matches)
        
        # Global team signals
        for pattern in self.KEYWORD_PATTERNS['global_team']:
            matches = re.findall(pattern, text, re.IGNORECASE)
            signals.global_team_signals.extend(matches)
        
        # Timezone signals
        for pattern in self.KEYWORD_PATTERNS['timezone']:
            matches = re.findall(pattern, text, re.IGNORECASE)
            signals.timezone_signals.extend(matches)
        
        # Distribution signals
        for pattern in (
            self.KEYWORD_PATTERNS['distribution'] +
            self.KEYWORD_PATTERNS['offshore_explicit'] +
            self.KEYWORD_PATTERNS['latam_specific'] +
            self.KEYWORD_PATTERNS['emea_specific']
        ):
            matches = re.findall(pattern, text, re.IGNORECASE)
            signals.distribution_signals.extend(matches)
        
        # Cost efficiency signals
        for pattern in self.KEYWORD_PATTERNS['cost_efficiency']:
            matches = re.findall(pattern, text, re.IGNORECASE)
            signals.cost_efficiency_signals.extend(matches)
        
        return signals
    
    def _classify_with_ml(self, text: str) -> Optional[Dict]:
        """
        Classify text using HuggingFace zero-shot classification.
        
        Args:
            text: Text to classify
        
        Returns:
            Dictionary with ML classification results
        """
        if not self.classifier:
            return None
        
        try:
            # Define candidate labels for outsourcing intent
            candidate_labels = [
                "remote work and distributed teams",
                "global hiring and international talent",
                "offshore development and outsourcing",
                "cost-effective hiring",
                "traditional on-site work"
            ]
            
            # Classify
            result = self.classifier(
                text[:512],  # Truncate to max length
                candidate_labels,
                multi_label=True
            )
            
            # Parse results
            scores = {}
            for label, score in zip(result['labels'], result['scores']):
                scores[label] = float(score)
            
            # Calculate outsourcing probability
            outsourcing_score = (
                scores.get("remote work and distributed teams", 0) * 0.3 +
                scores.get("global hiring and international talent", 0) * 0.3 +
                scores.get("offshore development and outsourcing", 0) * 0.4
            )
            
            return {
                'outsourcing_probability': outsourcing_score,
                'label_scores': scores,
                'top_label': result['labels'][0],
                'top_score': result['scores'][0]
            }
            
        except Exception as e:
            logger.error(f"Error in ML classification: {e}")
            return None
    
    def _calculate_intent_score(
        self,
        signals: OutsourcingSignals,
        ml_scores: Optional[Dict]
    ) -> float:
        """
        Calculate overall outsourcing intent score (0-100).
        
        Args:
            signals: Detected keyword signals
            ml_scores: ML classification scores
        
        Returns:
            Intent score (0-100)
        """
        # Keyword-based score (0-70)
        keyword_score = min(70, signals.total_signals() * 10)
        
        # ML-based score (0-30)
        ml_score = 0
        if ml_scores:
            ml_score = ml_scores.get('outsourcing_probability', 0) * 30
        
        # Combined score
        total_score = keyword_score + ml_score
        
        return min(100, total_score)
    
    def _determine_intent_level(self, score: float) -> str:
        """
        Determine intent level based on score.
        
        Args:
            score: Intent score (0-100)
        
        Returns:
            Intent level string
        """
        if score >= 70:
            return "Very High - Strong outsourcing intent"
        elif score >= 50:
            return "High - Clear outsourcing signals"
        elif score >= 30:
            return "Medium - Some outsourcing indicators"
        elif score >= 15:
            return "Low - Minimal outsourcing signals"
        else:
            return "Very Low - No clear outsourcing intent"
    
    def _calculate_confidence(
        self,
        signals: OutsourcingSignals,
        ml_scores: Optional[Dict]
    ) -> float:
        """
        Calculate confidence in the classification.
        
        Args:
            signals: Detected keyword signals
            ml_scores: ML classification scores
        
        Returns:
            Confidence score (0-1)
        """
        # Base confidence on number of signals
        signal_confidence = min(1.0, signals.total_signals() / 5.0)
        
        # ML confidence
        ml_confidence = 0.5  # Default
        if ml_scores and 'top_score' in ml_scores:
            ml_confidence = ml_scores['top_score']
        
        # Weighted average
        if ml_scores:
            return (signal_confidence * 0.6 + ml_confidence * 0.4)
        else:
            return signal_confidence
    
    def analyze_job_posting(self, job_text: str) -> Dict:
        """
        Analyze a job posting for outsourcing intent.
        
        Args:
            job_text: Job posting text
        
        Returns:
            Dictionary with analysis results
        """
        # Detect intent
        intent_analysis = self.detect_outsourcing_intent(job_text)
        
        # Extract additional job-specific signals
        location_flexibility = self._detect_location_flexibility(job_text)
        salary_indicators = self._detect_salary_indicators(job_text)
        
        return {
            **intent_analysis,
            'location_flexibility': location_flexibility,
            'salary_indicators': salary_indicators,
            'text_length': len(job_text),
            'analysis_type': 'job_posting'
        }
    
    def analyze_company_description(self, description: str) -> Dict:
        """
        Analyze a company description for outsourcing culture.
        
        Args:
            description: Company description text
        
        Returns:
            Dictionary with analysis results
        """
        # Detect intent
        intent_analysis = self.detect_outsourcing_intent(description)
        
        # Sentiment analysis
        sentiment = None
        if self.sentiment_analyzer:
            try:
                sentiment_result = self.sentiment_analyzer(description[:512])
                sentiment = {
                    'label': sentiment_result[0]['label'],
                    'score': sentiment_result[0]['score']
                }
            except Exception as e:
                logger.error(f"Error in sentiment analysis: {e}")
        
        return {
            **intent_analysis,
            'sentiment': sentiment,
            'text_length': len(description),
            'analysis_type': 'company_description'
        }
    
    def _detect_location_flexibility(self, text: str) -> Dict:
        """Detect location flexibility indicators in job postings."""
        text_lower = text.lower()
        
        indicators = {
            'work_from_anywhere': bool(re.search(r'work from anywhere|location independent', text_lower)),
            'specific_regions': bool(re.search(r'latam|emea|europe|asia|specific region', text_lower)),
            'timezone_mentioned': bool(re.search(r'timezone|time zone|gmt|utc', text_lower)),
            'relocation_not_required': bool(re.search(r'no relocation|relocation not required', text_lower))
        }
        
        return {
            'indicators': indicators,
            'flexibility_score': sum(indicators.values()) * 25  # 0-100
        }
    
    def _detect_salary_indicators(self, text: str) -> Dict:
        """Detect salary range indicators that suggest offshore hiring."""
        text_lower = text.lower()
        
        # Look for salary mentions
        salary_patterns = [
            r'\$\d+k?\s*-\s*\$\d+k?',
            r'\d+k?\s*-\s*\d+k?\s*(?:usd|dollars)',
            r'competitive salary',
            r'market rate',
            r'based on experience'
        ]
        
        salary_mentions = []
        for pattern in salary_patterns:
            matches = re.findall(pattern, text_lower)
            salary_mentions.extend(matches)
        
        return {
            'salary_mentioned': len(salary_mentions) > 0,
            'mentions': salary_mentions,
            'competitive_wording': 'competitive' in text_lower or 'market rate' in text_lower
        }


# Example usage and testing
if __name__ == "__main__":
    # Initialize classifier
    classifier = OutsourcingIntentClassifier(use_transformers=False)  # Set to True if transformers installed
    
    # Test cases
    test_texts = [
        {
            'name': 'High Intent - Remote-First Company',
            'text': """
            We are a remote-first company with a global team spanning LATAM, EMEA, and APAC timezones.
            We believe in hiring the best talent regardless of location and offer competitive rates
            for distributed teams. Work from anywhere with flexible hours.
            """
        },
        {
            'name': 'Medium Intent - Hybrid',
            'text': """
            Join our growing team! We offer hybrid work options with some remote flexibility.
            Our team is primarily based in the US but we welcome international applicants.
            """
        },
        {
            'name': 'Low Intent - On-site',
            'text': """
            Seeking a Software Engineer for our San Francisco office. This is an on-site position
            requiring daily attendance. Must be willing to relocate to the Bay Area.
            """
        }
    ]
    
    print("="*60)
    print("OUTSOURCING INTENT CLASSIFICATION TESTS")
    print("="*60)
    
    for test in test_texts:
        print(f"\n{test['name']}")
        print("-"*60)
        
        result = classifier.detect_outsourcing_intent(test['text'])
        
        print(f"Intent Detected: {result['outsourcing_intent_detected']}")
        print(f"Intent Score: {result['intent_score']}/100")
        print(f"Intent Level: {result['intent_level']}")
        print(f"Confidence: {result['confidence']:.2%}")
        print(f"Total Signals: {result['signals']['total_signals']}")
        
        if result['signals']['remote_work']:
            print(f"Remote Work Signals: {result['signals']['remote_work']}")
        if result['signals']['global_team']:
            print(f"Global Team Signals: {result['signals']['global_team']}")
        if result['signals']['timezone']:
            print(f"Timezone Signals: {result['signals']['timezone']}")
    
    print("\n" + "="*60)
