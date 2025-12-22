"""
NLP Entity Recognition for Regional Expansion
==============================================
Links US/Canadian funding events with LATAM delivery center mentions.
Uses advanced pattern matching and entity extraction.

Critical Score: 95% if US company + LATAM expansion detected
"""

import re
from typing import Dict, List, Tuple, Optional
from collections import Counter


class RegionalEntityRecognizer:
    """
    NLP-based entity recognition for cross-border expansion signals.
    """
    
    # US/Canadian company indicators
    US_CANADA_INDICATORS = [
        r'\b(Silicon Valley|San Francisco|SF|Bay Area|NYC|New York|Boston|Seattle|Austin|Toronto|Vancouver|Montreal)-based\b',
        r'\b(Silicon Valley|San Francisco|SF|Bay Area|NYC|New York|Boston|Seattle|Austin|Toronto|Vancouver|Montreal) based\b',
        r'\bUS-based\b',
        r'\bU\.S\.-based\b',
        r'\bAmerican company\b',
        r'\bCanadian (company|startup|firm)\b',
    ]
    
    # LATAM-based company indicators (to exclude from US/Canada)
    LATAM_BASED_INDICATORS = [
        r'\b(Buenos Aires|Bogotá|Bogota|Mexico City|Santiago|Montevideo|San José|Lima|São Paulo|Sao Paulo)-based\b',
        r'\b(Argentina|Colombia|Mexico|Chile|Uruguay|Costa Rica|Peru|Brazil)-based\b',
    ]
    
    # LATAM delivery center patterns
    DELIVERY_CENTER_PATTERNS = [
        # Direct mentions
        r'\b(delivery center|development center|engineering center|tech hub|innovation hub)\s+in\s+(Colombia|Argentina|Costa Rica|Uruguay|Chile|Mexico)\b',
        r'\b(Colombia|Argentina|Costa Rica|Uruguay|Chile|Mexico)\s+(delivery center|development center|engineering center)\b',
        
        # Operations/offices
        r'\b(opening|launching|establishing|expanding|setting up)\s+(operations|office|presence|team)\s+in\s+(Colombia|Argentina|Costa Rica|Uruguay|Chile|Mexico)\b',
        r'\b(expanding|growing|building)\s+(operations|presence)\s+in\s+(Colombia|Argentina|Costa Rica|Uruguay|Chile|Mexico)\b',
        
        # Hiring patterns
        r'\b(hiring|recruiting|building team)\s+in\s+(Colombia|Argentina|Costa Rica|Uruguay|Chile|Mexico)\b',
        r'\b(remote|distributed)\s+team\s+in\s+(Colombia|Argentina|Costa Rica|Uruguay|Chile|Mexico)\b',
        
        # Nearshore/offshore
        r'\b(nearshore|offshore)\s+(partner|team|development)\s+in\s+(Colombia|Argentina|Costa Rica|Uruguay|Chile|Mexico)\b',
        r'\b(Colombia|Argentina|Costa Rica|Uruguay|Chile|Mexico)\s+as\s+(nearshore|offshore)\b',
    ]
    
    # Expansion intent keywords
    EXPANSION_INTENT = [
        'expanding operations', 'international expansion', 'global expansion',
        'regional expansion', 'scaling internationally', 'growing presence',
        'establishing presence', 'entering market', 'new market',
        'expandiendo operaciones', 'expansión internacional', 'expansión regional'
    ]
    
    # Funding event patterns
    FUNDING_PATTERNS = [
        r'\$(\d+(?:\.\d+)?)\s*(M|million|B|billion)',
        r'raised\s+\$?(\d+(?:\.\d+)?)\s*(M|million|B|billion)',
        r'secured\s+\$?(\d+(?:\.\d+)?)\s*(M|million|B|billion)',
        r'closed\s+\$?(\d+(?:\.\d+)?)\s*(M|million|B|billion)',
        r'(Series [A-D]|Seed|Pre-seed)\s+round',
    ]
    
    def __init__(self):
        """Initialize entity recognizer."""
        pass
    
    def analyze_text(self, text: str, company_name: str = None) -> Dict[str, any]:
        """
        Analyze text for funding + LATAM expansion signals.
        
        Args:
            text: Content to analyze (news article, company description, etc.)
            company_name: Optional company name for context
            
        Returns:
            Analysis results with critical hiring score
        """
        # Detect entities
        is_us_canada_company = self._detect_us_canada(text)
        funding_amount = self._extract_funding_amount(text)
        latam_regions = self._detect_latam_expansion(text)
        has_expansion_intent = self._detect_expansion_intent(text)
        delivery_centers = self._extract_delivery_centers(text)
        
        # Calculate critical hiring score
        critical_score = self._calculate_critical_score(
            is_us_canada_company,
            funding_amount,
            latam_regions,
            has_expansion_intent,
            delivery_centers
        )
        
        # Determine if this is a CRITICAL opportunity (95%)
        is_critical = critical_score >= 95
        
        return {
            'company_name': company_name,
            'is_us_canada_company': is_us_canada_company,
            'funding_amount': funding_amount,
            'latam_expansion_detected': len(latam_regions) > 0,
            'latam_regions': latam_regions,
            'delivery_centers': delivery_centers,
            'has_expansion_intent': has_expansion_intent,
            'critical_hiring_score': critical_score,
            'is_critical_opportunity': is_critical,
            'entity_confidence': self._calculate_confidence(
                is_us_canada_company,
                latam_regions,
                delivery_centers
            ),
            'recommendation': self._generate_recommendation(critical_score, latam_regions)
        }
    
    def _detect_us_canada(self, text: str) -> bool:
        """Detect if company is US or Canadian."""
        # First check if it's LATAM-based (exclude these)
        for pattern in self.LATAM_BASED_INDICATORS:
            if re.search(pattern, text, re.IGNORECASE):
                return False
        
        # Then check for US/Canada indicators
        for pattern in self.US_CANADA_INDICATORS:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        return False
    
    def _extract_funding_amount(self, text: str) -> Optional[float]:
        """Extract funding amount in USD."""
        for pattern in self.FUNDING_PATTERNS:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    amount = float(match.group(1))
                    unit = match.group(2).lower() if len(match.groups()) > 1 else 'm'
                    
                    if 'b' in unit:
                        return amount * 1_000_000_000
                    else:  # million
                        return amount * 1_000_000
                except (IndexError, ValueError):
                    continue
        
        return None
    
    def _detect_latam_expansion(self, text: str) -> List[str]:
        """Detect mentioned LATAM countries."""
        latam_countries = ['Colombia', 'Argentina', 'Costa Rica', 'Uruguay', 'Chile', 'Mexico']
        detected = []
        
        for country in latam_countries:
            if re.search(r'\b' + re.escape(country) + r'\b', text, re.IGNORECASE):
                detected.append(country)
        
        return detected
    
    def _detect_expansion_intent(self, text: str) -> bool:
        """Detect expansion intent keywords."""
        text_lower = text.lower()
        return any(keyword in text_lower for keyword in self.EXPANSION_INTENT)
    
    def _extract_delivery_centers(self, text: str) -> List[Dict[str, str]]:
        """Extract delivery center mentions with location."""
        centers = []
        
        for pattern in self.DELIVERY_CENTER_PATTERNS:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                # Extract location from match groups
                location = None
                for group in match.groups():
                    if group in ['Colombia', 'Argentina', 'Costa Rica', 'Uruguay', 'Chile', 'Mexico']:
                        location = group
                        break
                
                if location:
                    centers.append({
                        'type': 'delivery_center',
                        'location': location,
                        'context': match.group(0)
                    })
        
        # Deduplicate by location
        unique_locations = {}
        for center in centers:
            loc = center['location']
            if loc not in unique_locations:
                unique_locations[loc] = center
        
        return list(unique_locations.values())
    
    def _calculate_critical_score(
        self,
        is_us_canada: bool,
        funding_amount: Optional[float],
        latam_regions: List[str],
        has_expansion_intent: bool,
        delivery_centers: List[Dict]
    ) -> int:
        """
        Calculate critical hiring score (0-100).
        
        Critical = 95% if:
        - US/Canada company (required)
        - Funding $10M+ (required)
        - Mentions LATAM expansion (required)
        - Has expansion intent OR delivery centers
        """
        if not is_us_canada:
            return 40  # Not US/Canada, lower score
        
        score = 50  # Base score for US/Canada company
        
        # Funding boost
        if funding_amount:
            if funding_amount >= 50_000_000:  # $50M+
                score += 20
            elif funding_amount >= 20_000_000:  # $20M+
                score += 15
            elif funding_amount >= 10_000_000:  # $10M+
                score += 10
            else:
                score += 5
        
        # LATAM expansion boost
        if latam_regions:
            score += 10 * len(latam_regions)  # +10 per region (max +30)
            score = min(score, 95)  # Cap before intent check
        
        # Expansion intent boost
        if has_expansion_intent:
            score += 10
        
        # Delivery center boost (explicit mention = strong signal)
        if delivery_centers:
            score += 15
        
        # CRITICAL: If all conditions met, set to 95%
        if (is_us_canada and 
            funding_amount and funding_amount >= 10_000_000 and
            latam_regions and
            (has_expansion_intent or delivery_centers)):
            score = 95
        
        return min(100, max(0, score))
    
    def _calculate_confidence(
        self,
        is_us_canada: bool,
        latam_regions: List[str],
        delivery_centers: List[Dict]
    ) -> str:
        """Calculate confidence level of entity extraction."""
        signals = sum([
            is_us_canada,
            len(latam_regions) > 0,
            len(delivery_centers) > 0
        ])
        
        if signals >= 3 or (signals == 2 and delivery_centers):
            return 'high'
        elif signals == 2:
            return 'medium'
        else:
            return 'low'
    
    def _generate_recommendation(self, score: int, regions: List[str]) -> str:
        """Generate actionable recommendation."""
        if score >= 95:
            return f"🔥 CRITICAL: US company expanding to {', '.join(regions)} - Contact immediately!"
        elif score >= 80:
            return f"⚡ HIGH PRIORITY: Strong expansion signal to {', '.join(regions) if regions else 'LATAM'}"
        elif score >= 60:
            return f"📊 MODERATE: Potential LATAM opportunity - Monitor closely"
        else:
            return f"📋 LOW: Limited expansion signals detected"
    
    def batch_analyze(self, items: List[Dict]) -> List[Dict]:
        """
        Analyze multiple items (news articles, company descriptions).
        
        Args:
            items: List of dicts with 'text' and optional 'company_name'
            
        Returns:
            List of analysis results
        """
        results = []
        
        for item in items:
            text = item.get('text', '') or item.get('content', '')
            company_name = item.get('company_name') or item.get('title', 'Unknown')
            
            analysis = self.analyze_text(text, company_name)
            
            # Merge with original item
            result = {**item, **analysis}
            results.append(result)
        
        return results
    
    def filter_critical(self, analyzed_items: List[Dict]) -> List[Dict]:
        """Filter for critical opportunities (95% score)."""
        return [
            item for item in analyzed_items
            if item.get('is_critical_opportunity', False)
        ]


def main():
    """
    Example usage of Regional Entity Recognizer.
    """
    print("🤖 Regional Entity Recognition - Test Run\n")
    
    recognizer = RegionalEntityRecognizer()
    
    # Test Case 1: Critical opportunity
    print("=" * 60)
    print("TEST CASE 1: US Company + Funding + LATAM Expansion")
    print("=" * 60)
    
    text1 = """
    TechCorp, a San Francisco-based AI startup, announced today that it
    raised $50M in Series B funding led by Sequoia Capital. The company
    plans to use the funds for expanding operations in Colombia and
    Argentina, establishing engineering centers in Bogotá and Buenos Aires.
    """
    
    result1 = recognizer.analyze_text(text1, "TechCorp")
    
    print(f"Company: {result1['company_name']}")
    print(f"US/Canada Company: {result1['is_us_canada_company']}")
    print(f"Funding: ${result1['funding_amount']:,.0f}" if result1['funding_amount'] else "No funding detected")
    print(f"LATAM Regions: {', '.join(result1['latam_regions'])}")
    print(f"Delivery Centers: {len(result1['delivery_centers'])}")
    print(f"Critical Score: {result1['critical_hiring_score']}/100")
    print(f"Is Critical: {result1['is_critical_opportunity']}")
    print(f"Recommendation: {result1['recommendation']}")
    
    # Test Case 2: No LATAM expansion
    print("\n" + "=" * 60)
    print("TEST CASE 2: US Company + Funding but NO LATAM")
    print("=" * 60)
    
    text2 = """
    StartupXYZ raised $30M Series A to expand its European operations.
    The New York-based company will open offices in London and Berlin.
    """
    
    result2 = recognizer.analyze_text(text2, "StartupXYZ")
    
    print(f"Company: {result2['company_name']}")
    print(f"US/Canada Company: {result2['is_us_canada_company']}")
    print(f"LATAM Expansion: {result2['latam_expansion_detected']}")
    print(f"Critical Score: {result2['critical_hiring_score']}/100")
    print(f"Recommendation: {result2['recommendation']}")
    
    print("\n✅ Entity recognition complete!")


if __name__ == '__main__':
    main()
