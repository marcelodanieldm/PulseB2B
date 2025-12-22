"""
Oracle Quick Demo
=================
Demonstrates the Oracle Funding Detector with sample data.
Perfect for testing before running the full scraper.
"""

import pandas as pd
from datetime import datetime, timedelta
import random


def generate_mock_data(num_companies: int = 10) -> pd.DataFrame:
    """Generate realistic mock data for testing Oracle output format."""
    
    companies = [
        "Anthropic Inc.",
        "Stripe Inc.",
        "Databricks Inc.",
        "Canva Inc.",
        "Figma Inc.",
        "Notion Labs Inc.",
        "Scale AI Inc.",
        "Weights & Biases Inc.",
        "Hugging Face Inc.",
        "Vercel Inc.",
        "Supabase Inc.",
        "Render Inc.",
        "Fly.io Inc.",
        "Railway Corp.",
        "Deno Land Inc."
    ]
    
    tech_stacks = [
        "Python, PyTorch, Kubernetes, AWS, PostgreSQL",
        "Ruby, React, Go, PostgreSQL, Redis",
        "Scala, Python, Spark, Delta Lake, Kubernetes",
        "React, TypeScript, Next.js, PostgreSQL",
        "TypeScript, React, WebAssembly, Rust",
        "TypeScript, Next.js, React, Node.js",
        "Python, TensorFlow, Kubernetes, GCP",
        "Python, PyTorch, React, PostgreSQL",
        "Python, PyTorch, FastAPI, Docker",
        "Next.js, React, TypeScript, Edge Functions",
        "PostgreSQL, TypeScript, Deno, Rust",
        "Elixir, PostgreSQL, Docker, Kubernetes",
        "Go, Kubernetes, Docker, PostgreSQL",
        "Go, PostgreSQL, Docker, Kubernetes",
        "TypeScript, Rust, WebAssembly, Deno"
    ]
    
    data = []
    
    for i in range(min(num_companies, len(companies))):
        company = companies[i]
        
        # Random funding amount (realistic for 2025)
        funding = random.choice([
            15.0, 25.0, 45.0, 80.0, 120.0, 200.0, 350.0, 450.0
        ])
        
        # Random date (last 30 days)
        days_ago = random.randint(1, 30)
        funding_date = (datetime.now() - timedelta(days=days_ago)).strftime('%Y-%m-%d')
        
        # Tech stack
        tech = tech_stacks[i]
        tech_count = len(tech.split(', '))
        
        # Hiring signals (random but realistic)
        hiring_signals = random.randint(3, 15)
        
        # Calculate hiring probability (simple mock formula)
        funding_score = min(funding / 100, 10)
        tech_diversity = min(tech_count, 10)
        hiring_intent = min(hiring_signals, 10)
        recency = max(0, 10 - (days_ago / 30))
        
        hiring_prob = (
            (funding_score * 0.35) +
            (tech_diversity * 0.25) +
            (hiring_intent * 0.30) +
            (recency * 0.10)
        ) * 10
        
        data.append({
            'Company Name': company,
            'Funding Date': funding_date,
            'Days Since Filing': days_ago,
            'Estimated Amount (M)': f'${funding:.1f}M',
            'Funding Source': f'Form D filing - ${funding}M Series B',
            'Tech Stack': tech,
            'Tech Count': tech_count,
            'Hiring Signals': hiring_signals,
            'Hiring Probability (%)': round(hiring_prob, 2),
            'Website': f'https://{company.lower().replace(" ", "").replace("inc.", "").replace("corp.", "").replace("labs", "")}.com',
            'Description': f'{company} is a rapidly growing technology company focused on innovation.',
            'CIK': f'{random.randint(1000000, 9999999):07d}',
            'Filing URL': f'https://www.sec.gov/cgi-bin/browse-edgar?CIK={random.randint(1000000, 9999999):07d}'
        })
    
    df = pd.DataFrame(data)
    df = df.sort_values('Hiring Probability (%)', ascending=False)
    
    return df


def print_summary(df: pd.DataFrame):
    """Print a beautiful summary report."""
    
    print("\n" + "="*60)
    print("🔮 ORACLE DEMO - SAMPLE OUTPUT")
    print("="*60)
    print(f"Total Companies: {len(df)}")
    print(f"High Probability (70%+): {len(df[df['Hiring Probability (%)'] >= 70])}")
    print(f"Medium Probability (40-70%): {len(df[(df['Hiring Probability (%)'] >= 40) & (df['Hiring Probability (%)'] < 70)])}")
    print(f"Low Probability (<40%): {len(df[df['Hiring Probability (%)'] < 40])}")
    print(f"Average Hiring Probability: {df['Hiring Probability (%)'].mean():.1f}%")
    print(f"Average Tech Stack Size: {df['Tech Count'].mean():.1f}")
    print("\n🏆 TOP 5 HIRING OPPORTUNITIES:")
    
    for idx, row in df.head(5).iterrows():
        print(f"  {idx+1}. {row['Company Name']:30s} - {row['Hiring Probability (%)']:5.1f}% | ${row['Estimated Amount (M)']:>8s} | Tech: {row['Tech Count']}")
    
    print("\n" + "="*60)
    print("📊 DETAILED VIEW (Top 3):")
    print("="*60)
    
    for idx, row in df.head(3).iterrows():
        print(f"\n{idx+1}. {row['Company Name']}")
        print(f"   Score: {row['Hiring Probability (%)']}%")
        print(f"   Funding: {row['Estimated Amount (M)']} ({row['Days Since Filing']} days ago)")
        print(f"   Tech: {row['Tech Stack']}")
        print(f"   Website: {row['Website']}")
        print(f"   Signals: {row['Hiring Signals']} hiring indicators detected")
    
    print("\n" + "="*60)
    print("✅ This is SAMPLE DATA - Run oracle_funding_detector.py for real data!")
    print("="*60 + "\n")


def export_demo_csv():
    """Export demo data to CSV."""
    df = generate_mock_data(15)
    
    import os
    output_dir = '../data/output/oracle'
    os.makedirs(output_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filepath = os.path.join(output_dir, f'oracle_demo_{timestamp}.csv')
    
    df.to_csv(filepath, index=False, encoding='utf-8')
    
    print(f"\n💾 Demo CSV exported to: {filepath}")
    
    return df, filepath


if __name__ == '__main__':
    print("\n🔮 Running Oracle Demo...\n")
    
    # Generate mock data
    df, csv_path = export_demo_csv()
    
    # Print summary
    print_summary(df)
    
    print("🎯 Next Steps:")
    print("  1. Review the demo CSV to understand the output format")
    print("  2. Run 'python scripts/oracle_funding_detector.py' for real SEC data")
    print("  3. Integrate with your CRM or sales workflow")
    print("\n📖 Full docs: docs/ORACLE_DETECTOR.md\n")
