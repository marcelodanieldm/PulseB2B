"""
Pulse Intelligence Module
--------------------------
Advanced NLP-based talent desperation analyzer for PulseB2B.
Uses TF-IDF vectorization to detect expansion signals and weighted scoring.

Author: PulseB2B AI Lead
Memory Footprint: <500MB (GitHub Actions compatible)
"""

import re
import json
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
from collections import Counter
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import MinMaxScaler


class PulseIntelligenceEngine:
    """
    Advanced intelligence engine that detects company talent desperation signals.
    """
    
    # Scoring weights
    WEIGHTS = {
        'sec_funding': 40,
        'multiple_job_posts_48h': 30,
        'c_level_hire': 20,
        'negative_keywords': -100,
        'expansion_density': 25,
        'tech_stack_diversity': 15
    }
    
    # Expansion keywords for TF-IDF analysis
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
    
    # Negative indicators (red flags)
    NEGATIVE_KEYWORDS = [
        'restructuring', 'reorganization', 'downsizing', 'cost cutting',
        'layoffs', 'layoff', 'redundancies', 'workforce reduction',
        'bankruptcy', 'chapter 11', 'financial difficulties', 'struggling',
        'pivot', 'refocusing', 'streamlining', 'efficiency measures',
        'hiring freeze', 'budget cuts', 'austerity', 'consolidation'
    ]
    
    # C-level titles for executive hire detection
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
    
    # Comprehensive tech stack (50+ terms organized by category)
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
        """Initialize the Pulse Intelligence Engine."""
        self.vectorizer = TfidfVectorizer(
            vocabulary=self.EXPANSION_KEYWORDS,
            lowercase=True,
            max_features=100,
            ngram_range=(1, 3)
        )
        self.scaler = MinMaxScaler(feature_range=(0, 100))
        
    def analyze_growth_signals(self, text_content: str) -> Dict[str, any]:
        """
        Analyze text content for expansion/growth signals using TF-IDF.
        
        Args:
            text_content: Raw text from company website, job posts, news, etc.
            
        Returns:
            Dictionary with density scores and detected keywords
        """
        if not text_content or len(text_content.strip()) < 50:
            return {
                'expansion_density': 0.0,
                'detected_keywords': [],
                'keyword_count': 0,
                'confidence': 'low'
            }
        
        try:
            # Fit and transform the text
            tfidf_matrix = self.vectorizer.fit_transform([text_content.lower()])
            feature_names = self.vectorizer.get_feature_names_out()
            
            # Get TF-IDF scores
            scores = tfidf_matrix.toarray()[0]
            
            # Find keywords with non-zero scores
            detected_keywords = []
            for idx, score in enumerate(scores):
                if score > 0:
                    detected_keywords.append({
                        'keyword': feature_names[idx],
                        'tfidf_score': float(score)
                    })
            
            # Sort by score
            detected_keywords.sort(key=lambda x: x['tfidf_score'], reverse=True)
            
            # Calculate expansion density (normalized 0-100)
            expansion_density = float(np.sum(scores) * 100)  # Scale up for visibility
            expansion_density = min(expansion_density, 100.0)  # Cap at 100
            
            # Determine confidence level
            keyword_count = len(detected_keywords)
            if keyword_count >= 10 and expansion_density >= 50:
                confidence = 'high'
            elif keyword_count >= 5 and expansion_density >= 25:
                confidence = 'medium'
            else:
                confidence = 'low'
            
            return {
                'expansion_density': round(expansion_density, 2),
                'detected_keywords': detected_keywords[:10],  # Top 10
                'keyword_count': keyword_count,
                'confidence': confidence
            }
            
        except Exception as e:
            print(f"⚠️  TF-IDF analysis failed: {e}")
            return {
                'expansion_density': 0.0,
                'detected_keywords': [],
                'keyword_count': 0,
                'confidence': 'error'
            }
    
    def detect_tech_stack(self, text_content: str) -> Dict[str, List[str]]:
        """
        Detect technology stack using regex pattern matching.
        
        Args:
            text_content: Raw text from job descriptions or company pages
            
        Returns:
            Dictionary with detected tech by category
        """
        detected_tech = {}
        all_tech = []
        
        for category, patterns in self.TECH_STACK.items():
            category_matches = []
            for pattern in patterns:
                matches = re.findall(pattern, text_content, re.IGNORECASE)
                if matches:
                    # Normalize and deduplicate
                    normalized = list(set([m.strip() for m in matches]))
                    category_matches.extend(normalized)
                    all_tech.extend(normalized)
            
            if category_matches:
                detected_tech[category] = list(set(category_matches))
        
        # Calculate diversity score (more categories = higher score)
        diversity_score = len(detected_tech.keys()) * 10  # Max 70 points (7 categories)
        
        return {
            'tech_by_category': detected_tech,
            'total_tech_count': len(set(all_tech)),
            'diversity_score': diversity_score,
            'categories_present': list(detected_tech.keys())
        }
    
    def detect_negative_signals(self, text_content: str) -> Dict[str, any]:
        """
        Detect negative keywords that indicate company distress.
        
        Args:
            text_content: Raw text to analyze
            
        Returns:
            Dictionary with detected red flags
        """
        detected_negatives = []
        
        for keyword in self.NEGATIVE_KEYWORDS:
            pattern = r'\b' + re.escape(keyword) + r'\b'
            matches = re.findall(pattern, text_content, re.IGNORECASE)
            if matches:
                detected_negatives.append({
                    'keyword': keyword,
                    'occurrences': len(matches)
                })
        
        # Calculate penalty
        total_penalty = len(detected_negatives) * abs(self.WEIGHTS['negative_keywords'])
        
        return {
            'negative_signals': detected_negatives,
            'total_red_flags': len(detected_negatives),
            'penalty_points': total_penalty,
            'is_risky': len(detected_negatives) > 0
        }
    
    def detect_c_level_hires(self, text_content: str, recent_date_threshold: Optional[datetime] = None) -> Dict[str, any]:
        """
        Detect recent C-level executive hires.
        
        Args:
            text_content: Text containing hire announcements or LinkedIn updates
            recent_date_threshold: Consider hires after this date as "recent"
            
        Returns:
            Dictionary with detected executive hires
        """
        if recent_date_threshold is None:
            recent_date_threshold = datetime.now() - timedelta(days=90)  # Last 3 months
        
        detected_hires = []
        
        # Common patterns for hire announcements
        hire_patterns = [
            r'(joined|joining|appointed|hired|announced|welcomes?)\s+.*?\s+as\s+({})'.format('|'.join(self.C_LEVEL_TITLES)),
            r'({})\s+.*?\s+(joined|joining|appointed|hired)'.format('|'.join(self.C_LEVEL_TITLES)),
            r'new\s+({})\s+'.format('|'.join(self.C_LEVEL_TITLES))
        ]
        
        for pattern in hire_patterns:
            matches = re.finditer(pattern, text_content, re.IGNORECASE)
            for match in matches:
                detected_hires.append({
                    'context': match.group(0),
                    'position': match.group(0)
                })
        
        c_level_score = len(detected_hires) * self.WEIGHTS['c_level_hire']
        
        return {
            'c_level_hires': detected_hires[:5],  # Top 5
            'total_executive_hires': len(detected_hires),
            'bonus_points': c_level_score,
            'has_recent_executives': len(detected_hires) > 0
        }
    
    def detect_job_post_velocity(self, job_posts: List[Dict], hours_window: int = 48) -> Dict[str, any]:
        """
        Analyze job posting frequency to detect hiring urgency.
        
        Args:
            job_posts: List of job post dictionaries with 'posted_date' field
            hours_window: Time window in hours (default 48h)
            
        Returns:
            Dictionary with job posting velocity metrics
        """
        if not job_posts:
            return {
                'posts_in_window': 0,
                'velocity_score': 0,
                'is_hiring_spree': False,
                'posts_per_day': 0.0
            }
        
        cutoff_time = datetime.now() - timedelta(hours=hours_window)
        recent_posts = []
        
        for post in job_posts:
            try:
                # Parse date (assume ISO format or common formats)
                posted_date = post.get('posted_date')
                if isinstance(posted_date, str):
                    posted_date = datetime.fromisoformat(posted_date.replace('Z', '+00:00'))
                
                if posted_date and posted_date >= cutoff_time:
                    recent_posts.append(post)
            except Exception:
                continue
        
        posts_count = len(recent_posts)
        velocity_score = min(posts_count * 10, self.WEIGHTS['multiple_job_posts_48h'])
        is_hiring_spree = posts_count >= 3  # 3+ posts in 48h = spree
        posts_per_day = posts_count / (hours_window / 24.0)
        
        return {
            'posts_in_window': posts_count,
            'velocity_score': velocity_score,
            'is_hiring_spree': is_hiring_spree,
            'posts_per_day': round(posts_per_day, 2),
            'recent_job_titles': [post.get('title', 'Unknown') for post in recent_posts[:5]]
        }
    
    def calculate_pulse_score(self, 
                            sec_funding_detected: bool,
                            text_content: str,
                            job_posts: Optional[List[Dict]] = None) -> Dict[str, any]:
        """
        Calculate comprehensive Pulse Intelligence Score.
        
        Args:
            sec_funding_detected: Whether SEC funding was detected
            text_content: Combined text from website, jobs, news
            job_posts: List of job posting dictionaries (optional)
            
        Returns:
            Standardized JSON output with all signals and final score
        """
        # Run all analysis modules
        growth_signals = self.analyze_growth_signals(text_content)
        tech_analysis = self.detect_tech_stack(text_content)
        negative_signals = self.detect_negative_signals(text_content)
        c_level_analysis = self.detect_c_level_hires(text_content)
        
        # Job velocity (if data available)
        if job_posts:
            job_velocity = self.detect_job_post_velocity(job_posts)
        else:
            job_velocity = {'velocity_score': 0, 'is_hiring_spree': False}
        
        # Calculate weighted score
        score_components = {
            'sec_funding': self.WEIGHTS['sec_funding'] if sec_funding_detected else 0,
            'job_velocity': job_velocity['velocity_score'],
            'c_level_hires': c_level_analysis['bonus_points'],
            'negative_penalty': -negative_signals['penalty_points'],
            'expansion_density': growth_signals['expansion_density'] * (self.WEIGHTS['expansion_density'] / 100),
            'tech_diversity': tech_analysis['diversity_score'] * (self.WEIGHTS['tech_stack_diversity'] / 100)
        }
        
        # Total score (capped at 0-100)
        raw_score = sum(score_components.values())
        final_score = max(0, min(100, raw_score))
        
        # Determine desperation level
        if final_score >= 80:
            desperation_level = 'CRITICAL'
            urgency = 'immediate'
        elif final_score >= 60:
            desperation_level = 'HIGH'
            urgency = 'urgent'
        elif final_score >= 40:
            desperation_level = 'MODERATE'
            urgency = 'normal'
        else:
            desperation_level = 'LOW'
            urgency = 'low_priority'
        
        # Compile standardized output
        return {
            'pulse_score': round(final_score, 2),
            'desperation_level': desperation_level,
            'urgency': urgency,
            'timestamp': datetime.now().isoformat(),
            'signals': {
                'funding': {
                    'sec_detected': sec_funding_detected,
                    'points': score_components['sec_funding']
                },
                'growth': {
                    'expansion_density': growth_signals['expansion_density'],
                    'confidence': growth_signals['confidence'],
                    'top_keywords': [kw['keyword'] for kw in growth_signals['detected_keywords'][:5]],
                    'points': score_components['expansion_density']
                },
                'hiring': {
                    'job_velocity': job_velocity,
                    'c_level_hires': c_level_analysis,
                    'total_points': score_components['job_velocity'] + score_components['c_level_hires']
                },
                'technology': {
                    'tech_stack': tech_analysis['tech_by_category'],
                    'total_tech_count': tech_analysis['total_tech_count'],
                    'diversity_score': tech_analysis['diversity_score'],
                    'points': score_components['tech_diversity']
                },
                'red_flags': {
                    'negative_signals': negative_signals['negative_signals'],
                    'is_risky': negative_signals['is_risky'],
                    'penalty': score_components['negative_penalty']
                }
            },
            'score_breakdown': score_components,
            'recommendation': self._generate_recommendation(final_score, desperation_level, negative_signals['is_risky'])
        }
    
    def _generate_recommendation(self, score: float, level: str, is_risky: bool) -> str:
        """Generate actionable recommendation based on analysis."""
        if is_risky:
            return "⚠️ RED FLAG DETECTED - Company shows distress signals. Proceed with caution or skip."
        
        if level == 'CRITICAL':
            return "🔥 IMMEDIATE ACTION - Company is desperately hiring. Prioritize outreach within 24h."
        elif level == 'HIGH':
            return "⚡ HIGH PRIORITY - Strong hiring signals detected. Engage within 48-72h."
        elif level == 'MODERATE':
            return "📊 MODERATE INTEREST - Track company but not urgent. Review weekly."
        else:
            return "📋 LOW PRIORITY - Minimal hiring signals. Consider for future pipeline."


def main():
    """
    Example usage of Pulse Intelligence Engine.
    """
    print("🧠 Pulse Intelligence Module - Test Run\n")
    
    # Initialize engine
    engine = PulseIntelligenceEngine()
    
    # Sample text (simulating scraped content)
    sample_text = """
    TechVenture Inc. just raised $50M in Series B funding led by Sequoia Capital.
    We are scaling rapidly and expanding to 5 new offices globally this year.
    
    Our hiring spree includes:
    - 10 Senior Software Engineers (React, TypeScript, AWS)
    - 5 Data Scientists (Python, TensorFlow, PyTorch)
    - 3 DevOps Engineers (Kubernetes, Docker, Terraform)
    
    We announced our new CTO, Jane Smith, who joined from Google.
    Our team is growing from 50 to 200 employees by Q4.
    
    Stack: Node.js, PostgreSQL, Redis, GraphQL, Next.js, Python, scikit-learn
    
    Join our fast-paced, ambitious team building the future of AI!
    """
    
    # Sample job posts
    sample_jobs = [
        {'title': 'Senior Backend Engineer', 'posted_date': datetime.now().isoformat()},
        {'title': 'ML Engineer', 'posted_date': (datetime.now() - timedelta(hours=12)).isoformat()},
        {'title': 'Frontend Developer', 'posted_date': (datetime.now() - timedelta(hours=36)).isoformat()}
    ]
    
    # Run analysis
    result = engine.calculate_pulse_score(
        sec_funding_detected=True,
        text_content=sample_text,
        job_posts=sample_jobs
    )
    
    # Output JSON
    print(json.dumps(result, indent=2))
    print("\n✅ Pulse Intelligence analysis complete!")
    print(f"   Score: {result['pulse_score']}/100")
    print(f"   Level: {result['desperation_level']}")
    print(f"   Recommendation: {result['recommendation']}")


if __name__ == '__main__':
    main()
