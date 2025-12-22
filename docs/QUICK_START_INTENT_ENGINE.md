# Quick Start: Intent Classification Engine

Get up and running with the Intent Classification Engine in 5 minutes.

## 1. Install Dependencies

```bash
# Install required packages
pip install sec-edgar-downloader GoogleNews textblob nltk

# Download NLTK data
python -c "import nltk; nltk.download('vader_lexicon'); nltk.download('punkt')"
```

## 2. Run Your First Analysis

Create a test script `test_engine.py`:

```python
from src.intent_classification_engine import IntentClassificationEngine

# Initialize
engine = IntentClassificationEngine(
    company_name="PulseB2B",
    contact_email="your@email.com",
    use_transformers=False
)

# Run market scan
results = engine.run_market_scan(
    news_queries=["tech startup series A funding"],
    output_dir="data/output/test"
)

print(f"\n✓ Found {results['summary']['qualified_leads']} qualified leads!")
print(f"✓ Results saved to: data/output/test/")
```

Run it:
```bash
python test_engine.py
```

## 3. View Results

Check the output directory:
```bash
# View the JSON file
cat data/output/test/market_scan_*.json

# Or open in your editor
code data/output/test/market_scan_*.json
```

## 4. Analyze a Specific Company

```python
from src.intent_classification_engine import IntentClassificationEngine

engine = IntentClassificationEngine(
    company_name="PulseB2B",
    contact_email="your@email.com"
)

result = engine.analyze_company(
    company_name="YourTargetCompany",
    company_description="""
    We're a remote-first startup with a distributed team.
    Recently raised Series A funding and expanding globally.
    """,
    funding_amount=10_000_000,
    funding_stage="series_a"
)

# Check the recommendation
print(f"Priority: {result['recommendation']['priority']}")
print(f"Score: {result['recommendation']['qualification_score']}/100")
print(f"Action: {result['recommendation']['recommended_action']}")
```

## 5. OSINT-Only Mode (Fastest)

For quick lead generation without SEC data:

```python
from src.osint_lead_scorer import OSINTLeadScorer

scorer = OSINTLeadScorer(use_nltk=True)

leads = scorer.score_news_batch(
    query="tech startup funding",
    regions=["US"],
    period="7d",
    max_results_per_region=30,
    min_score=30
)

scorer.save_scored_leads(leads, "data/output/quick_leads.json")

# Print top 5
for i, lead in enumerate(leads[:5], 1):
    print(f"{i}. {lead['company_name']} - Score: {lead['growth_score']}")
```

## Expected Output

```json
{
  "company_name": "Acme Corp",
  "source_url": "https://techcrunch.com/...",
  "growth_score": 85,
  "predicted_hiring_window": "Next 1-2 months (High Priority)",
  "matched_signals": ["+series_a", "+expansion", "+hiring"],
  "outsourcing_potential": true
}
```

## Next Steps

1. Read the full [Documentation](./INTENT_CLASSIFICATION_ENGINE.md)
2. Customize scoring rules in `osint_lead_scorer.py`
3. Add your target company tickers to SEC scraper
4. Set up automated daily scans with cron/Task Scheduler

## Troubleshooting

**Issue**: No results found
- Check your internet connection
- Try different search queries
- Increase `max_results_per_region`

**Issue**: NLTK errors
- Run: `python -c "import nltk; nltk.download('all')"`

**Issue**: SEC rate limiting
- Add delays between requests
- Reduce number of ticker symbols

## Common Use Cases

### Use Case 1: Daily Lead Generation
```bash
# Create a daily script
python src/osint_lead_scorer.py > daily_leads.log
```

### Use Case 2: Monitor Specific Companies
```python
target_companies = ["SNOW", "PLTR", "DDOG"]
results = engine.run_market_scan(target_tickers=target_companies)
```

### Use Case 3: Calculate Offshore Savings
```python
from src.global_hiring_score import GlobalHiringScoreCalculator

calc = GlobalHiringScoreCalculator()
roi = calc.calculate_roi_offshore(
    team_size=20,
    offshore_percentage=40,
    project_duration_months=12
)

print(f"Annual Savings: ${roi['annual_costs']['annual_savings']:,}")
```

That's it! You're ready to start finding offshore hiring opportunities. 🚀
