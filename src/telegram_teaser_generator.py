"""
=====================================================
TELEGRAM TEASER GENERATOR
=====================================================
Purpose: Generate punchy 3-line summaries for Telegram
Author: Senior Data Scientist
Date: December 22, 2025
=====================================================

NLP-driven summarization that extracts only the most
impactful data points for Telegram messages.

Output Format:
Line 1: 🏢 Company Name + Location
Line 2: 💰 Funding Status + Tech Stack (3 main)
Line 3: 🔥 Hiring Probability + Why

Selection: Highest Hiring Probability + Arbitrage Score
=====================================================
"""

import os
import re
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from supabase import create_client, Client

# =====================================================
# CONFIGURATION
# =====================================================

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_SERVICE_ROLE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")

if not SUPABASE_URL or not SUPABASE_SERVICE_ROLE_KEY:
    raise ValueError("Missing Supabase credentials")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)

# =====================================================
# NLP HELPER FUNCTIONS
# =====================================================

def extract_top_techs(tech_stack: List[str], limit: int = 3) -> List[str]:
    """
    Extract the most relevant technologies from tech stack.
    Prioritizes: Frameworks > Languages > Cloud > Databases
    """
    if not tech_stack:
        return []
    
    # Priority weights for tech categories
    priority_map = {
        # Frameworks (highest priority)
        'react': 10, 'vue': 10, 'angular': 10, 'spring': 10, 'django': 10,
        'flask': 10, 'express': 10, 'next.js': 10, 'springboot': 10,
        
        # Languages
        'python': 8, 'java': 8, 'javascript': 8, 'typescript': 8, 'go': 8,
        'kotlin': 8, 'swift': 8, 'rust': 8,
        
        # Cloud platforms
        'aws': 7, 'azure': 7, 'gcp': 7, 'kubernetes': 7, 'docker': 7,
        
        # Databases
        'postgresql': 6, 'mongodb': 6, 'redis': 6, 'mysql': 6,
        
        # Default
        'default': 5
    }
    
    # Score each tech
    scored_techs = []
    for tech in tech_stack[:10]:  # Only consider first 10
        tech_lower = tech.lower()
        score = priority_map.get(tech_lower, priority_map['default'])
        scored_techs.append((tech, score))
    
    # Sort by score (descending) and return top N
    scored_techs.sort(key=lambda x: x[1], reverse=True)
    return [tech for tech, _ in scored_techs[:limit]]


def format_funding_status(funding_stage: str, funding_amount: Optional[float]) -> str:
    """
    Format funding status in punchy way.
    Examples:
    - "Series A ($5M)"
    - "Series B ($25M+)"
    - "Well-funded (Series C)"
    """
    if not funding_stage:
        return "Privately funded"
    
    stage_emoji = {
        'Seed': '🌱',
        'Series A': '💵',
        'Series B': '💰',
        'Series C': '💎',
        'Series C+': '💎',
        'Series D+': '🚀',
    }
    
    emoji = stage_emoji.get(funding_stage, '💰')
    
    if funding_amount:
        if funding_amount < 1_000_000:
            amount_str = f"${int(funding_amount / 1000)}K"
        elif funding_amount < 10_000_000:
            amount_str = f"${funding_amount / 1_000_000:.1f}M"
        else:
            amount_str = f"${int(funding_amount / 1_000_000)}M+"
        
        return f"{emoji} {funding_stage} ({amount_str})"
    else:
        return f"{emoji} {funding_stage}"


def generate_hiring_insight(
    hiring_velocity: int,
    hiring_probability: float,
    country: str,
    company_insight: Optional[str]
) -> str:
    """
    Generate the "why" explanation for hiring urgency.
    Uses NLP to extract key phrases from company_insight.
    """
    urgency_level = "🔥🔥🔥" if hiring_probability >= 0.9 else "🔥🔥" if hiring_probability >= 0.75 else "🔥"
    
    # Extract key phrases from company_insight
    reasons = []
    
    if company_insight:
        insight_lower = company_insight.lower()
        
        # Pattern matching for key signals
        if 'series' in insight_lower and ('raised' in insight_lower or 'funding' in insight_lower):
            reasons.append("fresh funding")
        
        if hiring_velocity > 20:
            reasons.append("rapid expansion")
        elif hiring_velocity > 10:
            reasons.append("aggressive hiring")
        
        if 'y combinator' in insight_lower or 'yc' in insight_lower:
            reasons.append("YC-backed")
        
        if 'international' in insight_lower or 'global' in insight_lower:
            reasons.append("going global")
        
        if 'colombia' in insight_lower or 'latam' in insight_lower or 'latin america' in insight_lower:
            reasons.append(f"expanding in {country}")
        
        # Tech stack signals
        if 'modern stack' in insight_lower or 'cutting edge' in insight_lower:
            reasons.append("modern tech stack")
    
    # Fallback reasons based on metrics
    if not reasons:
        if hiring_velocity > 15:
            reasons.append(f"hiring {hiring_velocity}+ engineers")
        elif hiring_velocity > 5:
            reasons.append(f"{hiring_velocity} open positions")
        else:
            reasons.append("active hiring")
    
    # Format: "95% likely • fresh funding + rapid expansion"
    probability_str = f"{int(hiring_probability * 100)}% likely"
    reasons_str = " + ".join(reasons[:2])  # Max 2 reasons to keep punchy
    
    return f"{urgency_level} {probability_str} • {reasons_str}"


def calculate_arbitrage_score(
    country: str,
    funding_stage: str,
    tech_stack: List[str],
    desperation_score: int
) -> float:
    """
    Calculate arbitrage score for LATAM outsourcing potential.
    Higher score = better opportunity for cost arbitrage.
    
    Factors:
    - US/Canada companies (high salaries)
    - Well-funded (can afford outsourcing)
    - Modern tech stack (matches LATAM talent)
    - High desperation (urgent need)
    """
    score = 0.0
    
    # Country factor (US/Canada = highest arbitrage potential)
    country_scores = {
        'US': 1.0,
        'CA': 1.0,
        'GB': 0.8,
        'AU': 0.7,
        'DE': 0.6,
        'NL': 0.6,
        'SE': 0.6,
    }
    score += country_scores.get(country, 0.3) * 30  # Max 30 points
    
    # Funding stage factor (more funding = can afford outsourcing)
    funding_scores = {
        'Series A': 0.6,
        'Series B': 0.8,
        'Series C': 1.0,
        'Series C+': 1.0,
        'Series D+': 0.9,  # Sometimes too enterprise
    }
    score += funding_scores.get(funding_stage, 0.4) * 25  # Max 25 points
    
    # Tech stack modernity (LATAM has strong modern tech talent)
    modern_techs = {'react', 'vue', 'angular', 'node.js', 'python', 'go', 'typescript', 'next.js', 'aws', 'docker', 'kubernetes'}
    if tech_stack:
        tech_set = {tech.lower() for tech in tech_stack}
        modern_count = len(tech_set.intersection(modern_techs))
        score += min(modern_count * 5, 20)  # Max 20 points
    
    # Desperation score (urgent need = higher arbitrage value)
    score += (desperation_score / 100) * 25  # Max 25 points
    
    return min(score, 100.0)  # Cap at 100


# =====================================================
# MAIN TEASER GENERATOR
# =====================================================

def generate_tg_teaser(company_data: Dict) -> str:
    """
    Generate a 3-line Telegram teaser from company data.
    
    Args:
        company_data: Dict with keys:
            - company_name
            - country
            - funding_stage
            - funding_amount
            - tech_stack
            - hiring_velocity
            - hiring_probability
            - company_insight
    
    Returns:
        3-line formatted string optimized for Telegram
    """
    # Extract data
    company_name = company_data.get('company_name', 'Unknown Company')
    country = company_data.get('country', 'US')
    funding_stage = company_data.get('funding_stage')
    funding_amount = company_data.get('funding_amount')
    tech_stack = company_data.get('tech_stack', [])
    hiring_velocity = company_data.get('hiring_velocity', 0)
    hiring_probability = company_data.get('hiring_probability', 0.0)
    company_insight = company_data.get('company_insight')
    
    # Line 1: 🏢 Company Name + Location
    country_flags = {
        'US': '🇺🇸', 'CA': '🇨🇦', 'GB': '🇬🇧', 'DE': '🇩🇪',
        'FR': '🇫🇷', 'AU': '🇦🇺', 'NL': '🇳🇱', 'SE': '🇸🇪',
        'SG': '🇸🇬', 'IN': '🇮🇳', 'BR': '🇧🇷', 'MX': '🇲🇽',
        'CO': '🇨🇴', 'AR': '🇦🇷', 'CL': '🇨🇱',
    }
    flag = country_flags.get(country, '🌍')
    line1 = f"🏢 {company_name} {flag}"
    
    # Line 2: 💰 Funding Status + Tech Stack (3 main)
    funding_str = format_funding_status(funding_stage, funding_amount)
    top_techs = extract_top_techs(tech_stack, limit=3)
    tech_str = ", ".join(top_techs) if top_techs else "Modern stack"
    line2 = f"{funding_str} • {tech_str}"
    
    # Line 3: 🔥 Hiring Probability + Why
    line3 = generate_hiring_insight(
        hiring_velocity,
        hiring_probability,
        country,
        company_insight
    )
    
    # Combine lines
    teaser = f"{line1}\n{line2}\n{line3}"
    
    return teaser


# =====================================================
# COMPANY OF THE DAY SELECTION
# =====================================================

def select_company_of_the_day() -> Optional[Dict]:
    """
    Select the "Company of the Day" based on:
    1. Highest Hiring Probability
    2. Highest Arbitrage Score (US/Canada with LATAM potential)
    
    Returns company data dict or None if no candidates found.
    """
    print("[Company of the Day] Fetching candidates from last 24 hours...")
    
    # Query signals from last 24 hours
    yesterday = (datetime.utcnow() - timedelta(hours=24)).isoformat()
    
    response = supabase.table('signals') \
        .select('*') \
        .gte('created_at', yesterday) \
        .gte('desperation_score', 70) \
        .order('desperation_score', desc=True) \
        .limit(50) \
        .execute()
    
    if not response.data or len(response.data) == 0:
        print("[Company of the Day] No candidates found in last 24 hours")
        return None
    
    candidates = response.data
    print(f"[Company of the Day] Found {len(candidates)} candidates")
    
    # Calculate composite score for each candidate
    scored_candidates = []
    for candidate in candidates:
        # Hiring probability (0-100 scale)
        hiring_prob = candidate.get('hiring_probability', 0.0)
        if isinstance(hiring_prob, (int, float)):
            hiring_score = hiring_prob * 100 if hiring_prob <= 1.0 else hiring_prob
        else:
            hiring_score = 0.0
        
        # Arbitrage score (0-100 scale)
        arbitrage_score = calculate_arbitrage_score(
            country=candidate.get('country', 'US'),
            funding_stage=candidate.get('funding_stage', ''),
            tech_stack=candidate.get('tech_stack', []),
            desperation_score=candidate.get('desperation_score', 0)
        )
        
        # Composite score: 60% hiring probability + 40% arbitrage
        composite_score = (hiring_score * 0.6) + (arbitrage_score * 0.4)
        
        scored_candidates.append({
            'candidate': candidate,
            'hiring_score': hiring_score,
            'arbitrage_score': arbitrage_score,
            'composite_score': composite_score
        })
    
    # Sort by composite score
    scored_candidates.sort(key=lambda x: x['composite_score'], reverse=True)
    
    # Get top candidate
    winner = scored_candidates[0]
    company_name = winner['candidate'].get('company_name')
    
    print(f"[Company of the Day] Winner: {company_name}")
    print(f"  - Hiring Score: {winner['hiring_score']:.1f}")
    print(f"  - Arbitrage Score: {winner['arbitrage_score']:.1f}")
    print(f"  - Composite Score: {winner['composite_score']:.1f}")
    
    return winner['candidate']


# =====================================================
# DATABASE OPERATIONS
# =====================================================

def save_daily_teaser(signal_id: str, teaser_text: str) -> bool:
    """
    Save the generated teaser to the signals table.
    Updates the daily_teaser column.
    """
    try:
        response = supabase.table('signals') \
            .update({'daily_teaser': teaser_text}) \
            .eq('id', signal_id) \
            .execute()
        
        if response.data:
            print(f"[Save Teaser] Successfully saved for signal {signal_id}")
            return True
        else:
            print(f"[Save Teaser] Failed to save for signal {signal_id}")
            return False
    
    except Exception as e:
        print(f"[Save Teaser] Error: {str(e)}")
        return False


def get_daily_teaser_for_broadcast() -> Optional[Tuple[str, str]]:
    """
    Get the most recent daily teaser for Telegram broadcast.
    Returns (signal_id, teaser_text) or None.
    """
    try:
        response = supabase.table('signals') \
            .select('id, daily_teaser, company_name') \
            .not_.is_('daily_teaser', 'null') \
            .order('created_at', desc=True) \
            .limit(1) \
            .execute()
        
        if response.data and len(response.data) > 0:
            signal = response.data[0]
            return (signal['id'], signal['daily_teaser'])
        
        return None
    
    except Exception as e:
        print(f"[Get Teaser] Error: {str(e)}")
        return None


# =====================================================
# MAIN EXECUTION
# =====================================================

def run_daily_teaser_pipeline():
    """
    Main pipeline:
    1. Select Company of the Day
    2. Generate Telegram teaser
    3. Save to database
    """
    print("=" * 60)
    print("TELEGRAM TEASER GENERATOR - Daily Pipeline")
    print(f"Timestamp: {datetime.utcnow().isoformat()}")
    print("=" * 60)
    print()
    
    # Step 1: Select company
    company = select_company_of_the_day()
    
    if not company:
        print("\n❌ No suitable company found. Exiting.")
        return False
    
    print()
    
    # Step 2: Generate teaser
    print("[Generate Teaser] Creating 3-line summary...")
    teaser = generate_tg_teaser(company)
    
    print("\n" + "=" * 60)
    print("GENERATED TEASER:")
    print("=" * 60)
    print(teaser)
    print("=" * 60)
    print()
    
    # Step 3: Save to database
    signal_id = company['id']
    success = save_daily_teaser(signal_id, teaser)
    
    if success:
        print("✅ Daily teaser pipeline completed successfully")
        return True
    else:
        print("❌ Failed to save teaser to database")
        return False


# =====================================================
# CLI ENTRY POINT
# =====================================================

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        # Test mode: Generate teaser for sample data
        print("[TEST MODE] Generating teaser for sample data...\n")
        
        sample_data = {
            'company_name': 'TechCorp AI',
            'country': 'US',
            'funding_stage': 'Series B',
            'funding_amount': 25_000_000,
            'tech_stack': ['React', 'Python', 'AWS', 'PostgreSQL', 'Docker'],
            'hiring_velocity': 23,
            'hiring_probability': 0.92,
            'company_insight': 'TechCorp AI raised $25M Series B backed by Y Combinator. Rapidly expanding engineering team across LATAM.'
        }
        
        teaser = generate_tg_teaser(sample_data)
        print("=" * 60)
        print("SAMPLE TEASER:")
        print("=" * 60)
        print(teaser)
        print("=" * 60)
    
    else:
        # Production mode: Run full pipeline
        success = run_daily_teaser_pipeline()
        sys.exit(0 if success else 1)
