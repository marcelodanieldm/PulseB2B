"""
PulseIntelligenceEngine Service (migrated from legacy script)
"""
from typing import Dict, List, Tuple, Optional, Any
from datetime import datetime, timedelta
from collections import Counter
import re
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import MinMaxScaler

class PulseIntelligenceEngine:
    WEIGHTS = {
        'sec_funding': 40,
        'multiple_job_posts_48h': 30,
        'c_level_hire': 20,
        'negative_keywords': -100,
        'expansion_density': 25,
        'tech_stack_diversity': 15
    }
    EXPANSION_KEYWORDS = [
        'scaling', 'scale up', 'rapid growth', 'expansion', 'expanding',
        'new office', 'new location', 'opening office', 'global expansion',
        'hiring spree', 'aggressive hiring', 'mass hiring', 'talent acquisition',
        'investment', 'funding round', 'series a', 'series b', 'series c',
        'venture capital', 'vc backed', 'backed by', 'raised funding',
        'unicorn', 'hypergrowth', 'exponential growth', 'doubling team',
        'triple team size', 'building team', 'growing team', 'scaling team',
        'new market', 'market entry', 'launch', 'launching product',
        'innovative', 'disruptive', 'breakthrough', 'cutting edge',
        'ambitious', 'fast paced', 'dynamic', 'agile environment',
        'opportunity', 'ground floor', 'early stage', 'startup mode'
    ]
    NEGATIVE_KEYWORDS = [
        'restructuring', 'reorganization', 'downsizing', 'cost cutting',
        'layoffs', 'layoff', 'redundancies', 'workforce reduction',
        'bankruptcy', 'chapter 11', 'financial difficulties', 'struggling',
        'pivot', 'refocusing', 'streamlining', 'efficiency measures',
        'hiring freeze', 'budget cuts', 'austerity', 'consolidation'
    ]
    C_LEVEL_TITLES = [
        r'\bCEO\b', r'\bChief Executive Officer\b',
        r'\bCTO\b', r'\bChief Technology Officer\b',
        r'\bCFO\b', r'\bChief Financial Officer\b',
        r'\bCOO\b', r'\bChief Operating Officer\b',
        r'\bCMO\b', r'\bChief Marketing Officer\b',
        r'\bCPO\b', r'\bChief Product Officer\b',
        r'\bCHRO\b', r'\bChief Human Resources Officer\b',
        r'\bVP Engineering\b', r'\bVice President of Engineering\b',
        r'\bVP Product\b', r'\bHead of Engineering\b',
        r'\bHead of Product\b', r'\bDirector of Engineering\b'
    ]
    TECH_STACK = {
        'languages': [
            r'\bPython\b', r'\bJavaScript\b', r'\bTypeScript\b', r'\bJava\b',
            r'\bGo\b', r'\bRust\b', r'\bC\+\+\b', r'\bC#\b', r'\bRuby\b',
            r'\bPHP\b', r'\bSwift\b', r'\bKotlin\b', r'\bScala\b', r'\bElixir\b'
        ],
        'frontend': [
            r'\bReact\b', r'\bVue\.js\b', r'\bAngular\b', r'\bNext\.js\b',
            r'\bSvelte\b', r'\bTailwind\b', r'\bWebpack\b', r'\bVite\b'
        ],
        'backend': [
            r'\bNode\.js\b', r'\bExpress\b', r'\bDjango\b', r'\bFlask\b',
            r'\bFastAPI\b', r'\bSpring Boot\b', r'\bRails\b', r'\bLaravel\b',
            r'\bNestJS\b', r'\bGraphQL\b', r'\bREST API\b'
        ],
        'cloud': [
            r'\bAWS\b', r'\bAzure\b', r'\bGCP\b', r'\bGoogle Cloud\b',
            r'\bKubernetes\b', r'\bDocker\b', r'\bTerraform\b', r'\bVercel\b',
            r'\bNetlify\b', r'\bHeroku\b', r'\bCloudflare\b'
        ],
        'database': [
            r'\bPostgreSQL\b', r'\bMySQL\b', r'\bMongoDB\b', r'\bRedis\b',
            r'\bElasticsearch\b', r'\bCassandra\b', r'\bDynamoDB\b',
            r'\bSupabase\b', r'\bFirebase\b', r'\bPrisma\b'
        ],
        'ai_ml': [
            r'\bTensorFlow\b', r'\bPyTorch\b', r'\bscikit-learn\b', r'\bOpenAI\b',
            r'\bLangChain\b', r'\bHugging Face\b', r'\bMLOps\b', r'\bLLM\b',
            r'\bNLP\b', r'\bComputer Vision\b', r'\bDeep Learning\b'
        ],
        'devops': [
            r'\bCI/CD\b', r'\bGitHub Actions\b', r'\bJenkins\b', r'\bArgoCD\b',
            r'\bDatadog\b', r'\bPrometheus\b', r'\bGrafana\b', r'\bHelm\b'
        ]
    }
    def __init__(self):
        self.vectorizer = TfidfVectorizer(
            vocabulary=self.EXPANSION_KEYWORDS,
            lowercase=True,
            max_features=100,
            ngram_range=(1, 3)
        )
        self.scaler = MinMaxScaler(feature_range=(0, 100))
    # Add main analysis and scoring methods as needed for endpoints/background jobs

# Singleton instance
pulse_intelligence_engine = PulseIntelligenceEngine()
