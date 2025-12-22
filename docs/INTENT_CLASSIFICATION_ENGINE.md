# Intent Classification Engine for US Tech Market

## Overview

A comprehensive Python-based system for identifying offshore hiring opportunities in the US tech market using Open Source Intelligence (OSINT), SEC filings analysis, NLP-based intent classification, and financial scoring models.

## System Components

### 1. SEC EDGAR Form D Scraper (`sec_edgar_scraper.py`)
- **Purpose**: Detects new Form D filings from companies raising capital
- **Library**: `sec-edgar-downloader`
- **Key Features**:
  - Monitors recent funding rounds (Regulation D filings)
  - Extracts company information and offering amounts
  - Identifies companies in scaling phase (prime candidates for outsourcing)

### 2. OSINT Lead Scorer (`osint_lead_scorer.py`)
- **Purpose**: Free sentiment analysis of tech news using open-source libraries
- **Libraries**: `GoogleNews`, `TextBlob`, `NLTK`
- **Key Features**:
  - Scrapes US/EU tech news without paid APIs
  - Heuristic scoring system:
    - Series A/B + Expansion = +50 points
    - Layoffs = -100 points
  - Sentiment analysis for growth/shrinking detection
  - Outputs clean JSON with company scores and hiring windows

### 3. Outsourcing Intent Classifier (`intent_classifier.py`)
- **Purpose**: NLP analysis to detect outsourcing intent
- **Library**: `HuggingFace transformers` (optional, falls back to keyword matching)
- **Key Features**:
  - Detects keywords: 'Remote-friendly', 'Global team', 'Distributed', 'LATAM/EMEA timezones'
  - Zero-shot classification for company descriptions
  - Job posting analysis
  - Confidence scoring

### 4. Global Hiring Score Calculator (`global_hiring_score.py`)
- **Purpose**: Calculates offshore hiring necessity
- **Formula**: GHS = (Funding Amount / Median US Salary) × Multipliers
- **Key Features**:
  - Determines if companies MUST hire offshore
  - Calculates optimal US/offshore team mix
  - ROI analysis for offshore hiring
  - Market salary data (US vs LATAM/EMEA)

### 5. Main Orchestrator (`intent_classification_engine.py`)
- **Purpose**: Integrates all components into unified pipeline
- **Key Features**:
  - Single company analysis
  - Market-wide scanning
  - Lead qualification and scoring
  - Actionable recommendations

## Installation

### Required Dependencies

```bash
# Core dependencies
pip install sec-edgar-downloader
pip install GoogleNews
pip install textblob
pip install nltk

# Download NLTK data
python -c "import nltk; nltk.download('vader_lexicon')"
python -c "import nltk; nltk.download('punkt')"

# Optional: For advanced NLP (HuggingFace)
pip install transformers torch
```

### Requirements File

Add to your `requirements.txt`:
```
sec-edgar-downloader>=5.0.0
GoogleNews>=1.6.0
textblob>=0.17.1
nltk>=3.8.1
transformers>=4.30.0  # Optional
torch>=2.0.0  # Optional
```

## Usage Examples

### Example 1: Analyze a Single Company

```python
from src.intent_classification_engine import IntentClassificationEngine

# Initialize engine
engine = IntentClassificationEngine(
    company_name="Your Company Name",
    contact_email="your@email.com",
    use_transformers=False  # Set True if transformers installed
)

# Analyze specific company
result = engine.analyze_company(
    company_name="TechStartup Inc",
    company_ticker="TECH",  # Optional
    company_description="""
    We're a remote-first SaaS company with a global team.
    Recently raised $10M Series A and expanding our distributed
    engineering team across LATAM and EMEA timezones.
    """,
    funding_amount=10_000_000,
    funding_stage="series_a"
)

print(f"Qualification Score: {result['recommendation']['qualification_score']}")
print(f"Priority: {result['recommendation']['priority']}")
print(f"Action: {result['recommendation']['recommended_action']}")
```

### Example 2: Run Market-Wide Scan

```python
from src.intent_classification_engine import IntentClassificationEngine

engine = IntentClassificationEngine(
    company_name="Your Company",
    contact_email="your@email.com"
)

# Scan market for opportunities
results = engine.run_market_scan(
    target_tickers=["AAPL", "MSFT", "GOOGL"],  # Optional: SEC monitoring
    news_queries=[
        "tech startup series A funding",
        "SaaS company expansion",
        "remote-first company hiring"
    ],
    output_dir="data/output/market_intelligence"
)

# Results saved to JSON automatically
print(f"Found {results['summary']['qualified_leads']} qualified leads")
```

### Example 3: OSINT-Only Lead Scoring

```python
from src.osint_lead_scorer import OSINTLeadScorer

scorer = OSINTLeadScorer(use_nltk=True)

# Score recent tech news
leads = scorer.score_news_batch(
    query="tech startup funding OR expansion",
    regions=["US"],
    period="7d",  # Last 7 days
    max_results_per_region=50,
    min_score=30  # Minimum qualification score
)

# Save results
scorer.save_scored_leads(
    leads,
    "data/output/osint_leads/scored_leads.json"
)

# Output format:
# {
#   "company_name": "Acme Corp",
#   "source_url": "https://...",
#   "growth_score": 85,
#   "predicted_hiring_window": "Next 1-2 months (High Priority)"
# }
```

### Example 4: Calculate Global Hiring Score

```python
from src.global_hiring_score import GlobalHiringScoreCalculator

calculator = GlobalHiringScoreCalculator()

# Calculate for Series A startup
result = calculator.calculate_ghs(
    funding_amount=8_000_000,
    company_stage='series_a',
    urgency_level='expansion',
    stated_headcount_goal=15,
    current_team_size=5
)

print(f"GHS: {result['global_hiring_score']}")
print(f"Must Hire Offshore: {result['offshore_recommendation']['must_hire_offshore']}")
print(f"Offshore %: {result['offshore_recommendation']['offshore_percentage']}%")

# ROI Analysis
roi = calculator.calculate_roi_offshore(
    team_size=20,
    offshore_percentage=40,
    project_duration_months=12
)

print(f"Annual Savings: ${roi['annual_costs']['annual_savings']:,.0f}")
```

## Output Format

### JSON Output Structure

```json
{
  "company_name": "TechStartup Inc",
  "source_url": "https://techcrunch.com/...",
  "growth_score": 85,
  "predicted_hiring_window": "Next 1-2 months (High Priority)",
  "global_hiring_score": 47.5,
  "offshore_recommendation": {
    "must_hire_offshore": true,
    "offshore_percentage": 60,
    "reason": "Funding only covers 10 US engineers, but need to hire 15. Must hire 60% offshore.",
    "recommended_mix": {
      "us_engineers": 6,
      "offshore_engineers": 9,
      "total_engineers": 15
    }
  },
  "intent_classification": {
    "outsourcing_intent_detected": true,
    "intent_score": 75,
    "intent_level": "Very High - Strong outsourcing intent",
    "confidence": 0.85
  }
}
```

## Data Flow Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                   INPUT DATA SOURCES                        │
├─────────────────────────────────────────────────────────────┤
│  1. SEC EDGAR API (Form D)                                  │
│  2. Google News (Tech Articles)                             │
│  3. Company Descriptions                                    │
│  4. Job Postings                                            │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                   ANALYSIS ENGINES                          │
├─────────────────────────────────────────────────────────────┤
│  1. SEC Form D Parser → Extract Funding Data                │
│  2. OSINT Scorer → Sentiment + Heuristic Scoring            │
│  3. Intent Classifier → NLP Keyword Detection               │
│  4. GHS Calculator → Financial Analysis                     │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                   ORCHESTRATION LAYER                       │
├─────────────────────────────────────────────────────────────┤
│  - Combine all data sources                                 │
│  - Cross-reference findings                                 │
│  - Calculate qualification score                            │
│  - Generate recommendations                                 │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                   OUTPUT                                    │
├─────────────────────────────────────────────────────────────┤
│  - JSON: Structured lead data                               │
│  - CSV: Summary for easy viewing                            │
│  - Priority Rankings                                        │
│  - Actionable Recommendations                               │
└─────────────────────────────────────────────────────────────┘
```

## Configuration

### Market Salary Data

Default values in `global_hiring_score.py`:
- US Software Engineer: $120,000/year
- US Senior Engineer: $160,000/year
- LATAM Engineer: $45,000/year
- EMEA Engineer: $50,000/year

To customize, modify the `MarketSalaryData` class.

### Scoring Thresholds

In `osint_lead_scorer.py`:
- Series A/B funding: +50 points
- Expansion mentions: +50 points
- Layoffs: -100 points
- Hiring signals: +40 points

Adjust in `POSITIVE_KEYWORDS` and `NEGATIVE_KEYWORDS` dictionaries.

### Intent Keywords

In `intent_classifier.py`, modify `KEYWORD_PATTERNS`:
```python
'remote_work': [
    r'\bremote[-\s]friendly\b',
    r'\bremote[-\s]first\b',
    # Add more patterns...
],
```

## Constraints & Limitations

### ✅ Uses Only Open-Source Libraries
- No OpenAI/Anthropic API calls
- No paid services required
- All dependencies are free

### ⚠️ Known Limitations
1. **SEC EDGAR Rate Limiting**: Max 10 requests per second
2. **GoogleNews Accuracy**: May miss some articles or have outdated data
3. **NLP Accuracy**: Keyword matching is ~70-80% accurate without transformers
4. **Funding Data**: Form D filings may be delayed or incomplete

### 🚀 Performance Optimization
- Use `use_transformers=True` for better accuracy (requires more RAM)
- Adjust `max_results_per_region` to balance speed vs coverage
- Cache results to avoid re-scraping

## Testing

### Run Individual Components

```bash
# Test SEC scraper
python src/sec_edgar_scraper.py

# Test OSINT scorer
python src/osint_lead_scorer.py

# Test GHS calculator
python src/global_hiring_score.py

# Test intent classifier
python src/intent_classifier.py

# Run full pipeline
python src/intent_classification_engine.py
```

### Expected Output Locations

```
data/output/
├── form_d_analysis/
│   └── form_d_filings.json
├── osint_leads/
│   ├── scored_leads_YYYYMMDD_HHMMSS.json
│   └── scored_leads_YYYYMMDD_HHMMSS_summary.csv
└── market_intelligence/
    └── market_scan_YYYYMMDD_HHMMSS.json
```

## Troubleshooting

### Issue: GoogleNews not returning results
**Solution**: The library may have API changes. Alternative: Use `pygooglenews` instead:
```bash
pip install pygooglenews
```

### Issue: NLTK data missing
**Solution**: Download required data:
```python
import nltk
nltk.download('vader_lexicon')
nltk.download('punkt')
nltk.download('stopwords')
```

### Issue: SEC EDGAR blocking requests
**Solution**: Ensure proper user agent is set. The scraper automatically includes company name and email.

### Issue: Memory error with transformers
**Solution**: Use `use_transformers=False` to fall back to keyword matching, or reduce batch sizes.

## Best Practices

1. **Rate Limiting**: Add delays between API calls
2. **Caching**: Store results to avoid re-scraping
3. **Data Validation**: Always verify company names and funding amounts
4. **Regular Updates**: Run scans weekly to catch new opportunities
5. **Manual Review**: High-value leads should be manually verified

## Future Enhancements

- [ ] Add support for CrunchBase API
- [ ] Implement company website scraping
- [ ] Add LinkedIn job posting analysis
- [ ] Create Supabase integration for lead storage
- [ ] Build real-time alerting system
- [ ] Add company contact information enrichment

## License

All code uses open-source libraries and is provided as-is for educational and commercial use.

## Support

For questions or issues, refer to individual module docstrings or contact the development team.
