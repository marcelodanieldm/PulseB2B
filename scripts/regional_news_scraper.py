"""
Regional News Scraper
=====================
RSS-based news scraper for Canada and LATAM tech ecosystems.
Detects funding events and regional expansion signals.

Sources:
- Canada: Betakit, TechVibes
- LATAM: PulsoSocial, Contxto, Forbes (Local editions)
"""

import feedparser
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import re
import time


class RegionalNewsScraper:
    """
    Scrapes regional tech news sources via RSS feeds.
    """
    
    # RSS Feed URLs
    RSS_FEEDS = {
        # Canada
        'canada_betakit': 'https://betakit.com/feed/',
        'canada_techvibes': 'https://techvibes.com/feed',
        
        # LATAM
        'latam_pulsosocial': 'https://www.pulsosocial.com/feed/',
        'latam_contxto': 'https://www.contxto.com/en/feed/',
        'latam_forbes_latam': 'https://www.forbes.com/innovation/feed/',  # General innovation feed
        
        # Regional specific
        'mexico_techcrunch': 'https://techcrunch.com/tag/mexico/feed/',
        'argentina_endeavor': 'https://endeavor.org.ar/feed/',
        'colombia_apps_co': 'https://apps.co/comunicaciones/feed/',
    }
    
    # Funding keywords (English and Spanish)
    FUNDING_KEYWORDS = [
        # English
        'raised', 'funding', 'investment', 'series a', 'series b', 'series c',
        'venture capital', 'vc', 'seed round', 'round', 'million', 'backed by',
        
        # Spanish
        'levantó', 'inversión', 'financiamiento', 'ronda', 'capital',
        'millones', 'respaldado por'
    ]
    
    # Regional expansion keywords
    EXPANSION_KEYWORDS = [
        # English
        'expanding', 'expansion', 'opening office', 'new office', 'delivery center',
        'nearshore', 'offshore', 'remote team', 'distributed team', 'hiring in',
        'operations in', 'presence in', 'establishing', 'launching in',
        
        # Spanish
        'expandiendo', 'expansión', 'abriendo oficina', 'nueva oficina',
        'centro de desarrollo', 'contratando en', 'operaciones en', 'presencia en'
    ]
    
    # LATAM countries and cities
    LATAM_LOCATIONS = {
        'Mexico': ['Mexico City', 'Guadalajara', 'Monterrey', 'Tijuana'],
        'Argentina': ['Buenos Aires', 'Córdoba', 'Rosario', 'Mendoza'],
        'Uruguay': ['Montevideo', 'Punta del Este'],
        'Chile': ['Santiago', 'Valparaíso'],
        'Colombia': ['Bogotá', 'Medellín', 'Cali', 'Barranquilla'],
        'Costa Rica': ['San José', 'Heredia']
    }
    
    def __init__(self, days_back: int = 7):
        """
        Initialize scraper.
        
        Args:
            days_back: How many days back to scrape (default 7)
        """
        self.days_back = days_back
        self.cutoff_date = datetime.now() - timedelta(days=days_back)
        self.results = []
        self.user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    
    def scrape_all_feeds(self) -> List[Dict]:
        """
        Scrape all RSS feeds and return unified results.
        
        Returns:
            List of news items with metadata
        """
        print(f"🔍 Scraping regional news (last {self.days_back} days)...\n")
        
        for feed_name, feed_url in self.RSS_FEEDS.items():
            print(f"📰 {feed_name}...", end=' ')
            
            try:
                items = self._scrape_feed(feed_name, feed_url)
                self.results.extend(items)
                print(f"✅ {len(items)} articles")
                time.sleep(1)  # Rate limiting
            except Exception as e:
                print(f"❌ Error: {e}")
        
        print(f"\n📊 Total articles scraped: {len(self.results)}")
        return self.results
    
    def _scrape_feed(self, feed_name: str, feed_url: str) -> List[Dict]:
        """Scrape individual RSS feed."""
        try:
            feed = feedparser.parse(feed_url)
            items = []
            
            for entry in feed.entries:
                # Parse date
                published = self._parse_date(entry)
                if published and published < self.cutoff_date:
                    continue  # Skip old articles
                
                # Extract content
                title = entry.get('title', '')
                summary = entry.get('summary', '') or entry.get('description', '')
                content = f"{title} {summary}"
                
                # Detect signals
                has_funding = self._detect_funding_signal(content)
                has_expansion = self._detect_expansion_signal(content)
                detected_regions = self._detect_regions(content)
                
                # Only keep relevant articles
                if has_funding or has_expansion or detected_regions:
                    items.append({
                        'source': feed_name,
                        'title': title,
                        'summary': summary,
                        'link': entry.get('link', ''),
                        'published': published.isoformat() if published else None,
                        'has_funding_signal': has_funding,
                        'has_expansion_signal': has_expansion,
                        'detected_regions': detected_regions,
                        'content': content
                    })
            
            return items
            
        except Exception as e:
            raise Exception(f"Failed to parse feed: {e}")
    
    def _parse_date(self, entry: Dict) -> Optional[datetime]:
        """Parse entry date."""
        date_fields = ['published_parsed', 'updated_parsed', 'created_parsed']
        
        for field in date_fields:
            if hasattr(entry, field):
                time_struct = getattr(entry, field)
                if time_struct:
                    return datetime(*time_struct[:6])
        
        return None
    
    def _detect_funding_signal(self, text: str) -> bool:
        """Detect funding-related keywords."""
        text_lower = text.lower()
        return any(keyword in text_lower for keyword in self.FUNDING_KEYWORDS)
    
    def _detect_expansion_signal(self, text: str) -> bool:
        """Detect expansion-related keywords."""
        text_lower = text.lower()
        return any(keyword in text_lower for keyword in self.EXPANSION_KEYWORDS)
    
    def _detect_regions(self, text: str) -> List[str]:
        """Detect mentioned LATAM regions."""
        detected = []
        
        for country, cities in self.LATAM_LOCATIONS.items():
            # Check country name
            if re.search(r'\b' + re.escape(country) + r'\b', text, re.IGNORECASE):
                detected.append(country)
                continue
            
            # Check cities
            for city in cities:
                if re.search(r'\b' + re.escape(city) + r'\b', text, re.IGNORECASE):
                    detected.append(country)
                    break
        
        return list(set(detected))  # Deduplicate
    
    def filter_critical_signals(self) -> List[Dict]:
        """
        Filter for critical signals: funding + expansion.
        
        Returns:
            Articles with both funding and expansion signals
        """
        critical = [
            item for item in self.results
            if item['has_funding_signal'] and item['has_expansion_signal']
        ]
        
        print(f"\n🔥 Critical signals (funding + expansion): {len(critical)}")
        return critical
    
    def get_regional_summary(self) -> Dict[str, any]:
        """Generate summary statistics by region."""
        summary = {
            'total_articles': len(self.results),
            'funding_signals': sum(1 for r in self.results if r['has_funding_signal']),
            'expansion_signals': sum(1 for r in self.results if r['has_expansion_signal']),
            'critical_signals': len(self.filter_critical_signals()),
            'by_region': {},
            'by_source': {}
        }
        
        # Count by region
        for item in self.results:
            for region in item['detected_regions']:
                if region not in summary['by_region']:
                    summary['by_region'][region] = 0
                summary['by_region'][region] += 1
        
        # Count by source
        for item in self.results:
            source = item['source']
            if source not in summary['by_source']:
                summary['by_source'][source] = 0
            summary['by_source'][source] += 1
        
        return summary
    
    def export_to_csv(self, output_path: str):
        """Export results to CSV."""
        import csv
        
        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            if not self.results:
                return
            
            fieldnames = ['source', 'title', 'link', 'published', 
                         'has_funding_signal', 'has_expansion_signal', 
                         'detected_regions']
            
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            
            for item in self.results:
                writer.writerow({
                    'source': item['source'],
                    'title': item['title'],
                    'link': item['link'],
                    'published': item['published'],
                    'has_funding_signal': item['has_funding_signal'],
                    'has_expansion_signal': item['has_expansion_signal'],
                    'detected_regions': ', '.join(item['detected_regions'])
                })


def main():
    """
    Example usage of Regional News Scraper.
    """
    print("📰 Regional News Scraper - Test Run\n")
    
    # Initialize scraper (last 7 days)
    scraper = RegionalNewsScraper(days_back=7)
    
    # Scrape all feeds
    results = scraper.scrape_all_feeds()
    
    # Get critical signals
    critical = scraper.filter_critical_signals()
    
    # Print summary
    summary = scraper.get_regional_summary()
    
    print("\n" + "=" * 60)
    print("📊 REGIONAL NEWS SUMMARY")
    print("=" * 60)
    print(f"Total Articles: {summary['total_articles']}")
    print(f"Funding Signals: {summary['funding_signals']}")
    print(f"Expansion Signals: {summary['expansion_signals']}")
    print(f"Critical Signals (both): {summary['critical_signals']}")
    
    if summary['by_region']:
        print("\n🌎 By Region:")
        for region, count in sorted(summary['by_region'].items(), key=lambda x: x[1], reverse=True):
            print(f"  {region}: {count} mentions")
    
    if summary['by_source']:
        print("\n📰 By Source:")
        for source, count in sorted(summary['by_source'].items(), key=lambda x: x[1], reverse=True):
            print(f"  {source}: {count} articles")
    
    # Show critical examples
    if critical:
        print("\n🔥 Critical Signal Examples:")
        for i, item in enumerate(critical[:3], 1):
            print(f"\n{i}. {item['title']}")
            print(f"   Source: {item['source']}")
            print(f"   Regions: {', '.join(item['detected_regions'])}")
            print(f"   Link: {item['link']}")
    
    print("\n✅ Regional news scraping complete!")


if __name__ == '__main__':
    main()
