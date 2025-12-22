"""
Merge Regional Results
======================
Combines scraped data from 4 regional crawlers into unified dataset.

Handles:
- CSV merging from artifacts
- Duplicate detection
- Data normalization
- Missing region handling

Author: PulseB2B Senior Backend Engineer
"""

import csv
import os
from pathlib import Path
from typing import List, Dict
from datetime import datetime


def load_regional_csv(file_path: str) -> List[Dict]:
    """Load regional CSV file."""
    results = []
    
    if not os.path.exists(file_path):
        print(f"⚠️ File not found: {file_path}")
        return results
    
    with open(file_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            results.append(row)
    
    return results


def merge_regional_results():
    """
    Merge all regional scraping results into single CSV.
    """
    print("🔄 Merging Regional Results")
    print("="*80)
    
    # Define regions
    regions = ['north_america', 'central_america', 'andean_region', 'southern_cone']
    
    all_results = []
    region_stats = {}
    
    # Load each region
    for region in regions:
        file_path = f'artifacts/scraped-{region}/scraped_{region}.csv'
        
        print(f"\n📥 Loading {region}...")
        results = load_regional_csv(file_path)
        
        if results:
            all_results.extend(results)
            region_stats[region] = len(results)
            print(f"   ✅ {len(results)} records loaded")
        else:
            region_stats[region] = 0
            print(f"   ⚠️ No data found")
    
    # Remove duplicates (same company + country)
    print(f"\n🔍 Removing duplicates...")
    seen = set()
    unique_results = []
    
    for result in all_results:
        key = (result['company_name'], result['country_code'])
        if key not in seen:
            seen.add(key)
            unique_results.append(result)
    
    duplicates_removed = len(all_results) - len(unique_results)
    print(f"   ✅ Removed {duplicates_removed} duplicates")
    print(f"   📊 Unique records: {len(unique_results)}")
    
    # Save merged results
    output_path = 'data/output/merged_global_scraped.csv'
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    
    fieldnames = [
        'company_name', 'country', 'country_code', 'region',
        'job_count', 'job_urls', 'timezone_match', 'currency_type',
        'scraped_at', 'funding_amount', 'original_region'
    ]
    
    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(unique_results)
    
    print(f"\n✅ Merged results saved to {output_path}")
    
    # Print summary
    print("\n" + "="*80)
    print("📊 MERGE SUMMARY")
    print("="*80)
    
    for region, count in region_stats.items():
        print(f"   {region:20} {count:>5} records")
    
    print(f"\n   {'TOTAL':<20} {len(all_results):>5} records")
    print(f"   {'UNIQUE':<20} {len(unique_results):>5} records")
    print(f"   {'DUPLICATES REMOVED':<20} {duplicates_removed:>5} records")
    
    # Country breakdown
    print(f"\n📍 Country Breakdown:")
    country_counts = {}
    for result in unique_results:
        country = result['country_code']
        country_counts[country] = country_counts.get(country, 0) + 1
    
    for country, count in sorted(country_counts.items(), key=lambda x: x[1], reverse=True)[:10]:
        print(f"   {country:5} {count:>5} records")
    
    print(f"\n🎉 Merge complete!")


if __name__ == '__main__':
    merge_regional_results()
