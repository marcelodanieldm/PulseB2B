# 🎯 Intent Classification Engine - Implementation Summary

## Project Overview

Successfully built a comprehensive **Intent Classification Engine** for US Tech Market Intelligence that identifies offshore hiring opportunities using Open Source Intelligence (OSINT), SEC filings analysis, NLP-based intent classification, and financial scoring models.

## ✅ Components Delivered

### 1. SEC EDGAR Form D Scraper
**File:** [`src/sec_edgar_scraper.py`](../src/sec_edgar_scraper.py)

- ✅ Uses `sec-edgar-downloader` library
- ✅ Detects new Form D filings (Regulation D fundraising)
- ✅ Extracts company information and offering amounts
- ✅ Parses filing metadata and details
- ✅ Identifies companies in scaling phase after funding

**Key Features:**
- Monitors recent filings (last 30-90 days)
- Extracts total offering amounts
- Saves filing metadata to JSON
- Respects SEC API rate limits

### 2. OSINT Lead Scorer (Free Sentiment Analysis)
**File:** [`src/osint_lead_scorer.py`](../src/osint_lead_scorer.py)

- ✅ Uses `GoogleNews` for tech news scraping (free)
- ✅ Implements `TextBlob` and `NLTK VADER` for sentiment (free)
- ✅ Heuristic scoring system with business rules
- ✅ No paid APIs (OpenAI/Anthropic/etc.)

**Scoring Logic:**
| Signal | Points |
|--------|--------|
| Series A/B Funding | +50/+60 |
| Expansion | +50 |
| Hiring Signals | +40 |
| **Layoffs** | **-100** |
| Bankruptcy | -150 |
| Growth Mentions | +30 |

**Output Format:**
```json
{
  "company_name": "Acme Corp",
  "source_url": "https://techcrunch.com/...",
  "growth_score": 85,
  "predicted_hiring_window": "Next 1-2 months (High Priority)",
  "matched_signals": ["+series_a", "+expansion"],
  "outsourcing_potential": true
}
```

### 3. Outsourcing Intent Classifier (NLP)
**File:** [`src/intent_classifier.py`](../src/intent_classifier.py)

- ✅ HuggingFace transformers support (optional)
- ✅ Keyword-based classification (always available)
- ✅ Detects: 'Remote-friendly', 'Global team', 'Distributed', 'LATAM/EMEA timezones'
- ✅ Zero-shot classification with BART model
- ✅ Job posting analysis
- ✅ Company description analysis

**Keywords Detected:**
- **Remote Work:** remote-friendly, remote-first, work from anywhere, distributed
- **Global Team:** global team, international team, worldwide team
- **Timezone:** LATAM timezone, EMEA timezone, multiple timezones
- **Offshore:** offshore, nearshore, outsourcing (explicit mentions)

**Intent Score:** 0-100 with confidence levels

### 4. Global Hiring Score (GHS) Calculator
**File:** [`src/global_hiring_score.py`](../src/global_hiring_score.py)

- ✅ Formula: `GHS = (Funding Amount / US Median Salary) × Multipliers`
- ✅ Determines if companies MUST hire offshore
- ✅ Calculates optimal US/offshore team mix
- ✅ ROI analysis for offshore hiring
- ✅ Market salary data (US vs LATAM/EMEA)

**Market Data (2024-2025):**
| Role | US Salary | LATAM Salary | Savings |
|------|-----------|--------------|---------|
| Software Engineer | $120,000 | $45,000 | $75,000 |
| Senior Engineer | $160,000 | $60,000 | $100,000 |
| Staff Engineer | $200,000 | $70,000 | $130,000 |

**Example Output:**
```
Funding: $8M
Affordable US Engineers: 47
Must Hire Offshore: Yes
Recommended Mix: 60% offshore (6 US + 9 offshore)
Annual Savings: $675,000
```

### 5. Main Orchestrator Pipeline
**File:** [`src/intent_classification_engine.py`](../src/intent_classification_engine.py)

- ✅ Integrates all components
- ✅ Single company analysis
- ✅ Market-wide scanning
- ✅ Lead qualification and scoring
- ✅ Actionable recommendations

**Features:**
- Combines SEC data + news analysis + intent classification + GHS
- Generates qualification scores (0-100)
- Priority levels (Critical/High/Medium/Low)
- Recommended actions for sales team

## 📚 Documentation Delivered

1. **[Main Documentation](../docs/INTENT_CLASSIFICATION_ENGINE.md)** - Complete technical reference
2. **[Quick Start Guide](../docs/QUICK_START_INTENT_ENGINE.md)** - 5-minute setup
3. **[Requirements File](../requirements-intent-engine.txt)** - All dependencies
4. **[Example Pipeline](../examples/run_intent_classification_pipeline.py)** - Full workflow demo

## 🚀 Setup & Usage

### Installation (2 minutes)
```bash
# Windows
.\setup_intent_engine.bat

# Linux/Mac
chmod +x setup_intent_engine.sh
./setup_intent_engine.sh
```

### Quick Test (30 seconds)
```python
from src.osint_lead_scorer import OSINTLeadScorer

scorer = OSINTLeadScorer(use_nltk=True)
leads = scorer.score_news_batch(
    query="tech startup funding",
    regions=["US"],
    period="7d",
    min_score=30
)

print(f"Found {len(leads)} qualified leads!")
```

### Full Pipeline (5 minutes)
```bash
python examples/run_intent_classification_pipeline.py
```

## 🎯 Technical Requirements Met

### ✅ SEC EDGAR Integration
- [x] Uses `sec-edgar-downloader` library
- [x] Detects new Form D filings
- [x] Extracts funding amounts
- [x] Parses company information

### ✅ NLP Intent Classification
- [x] HuggingFace transformers support
- [x] Keyword detection: Remote-friendly, Global team, Distributed
- [x] LATAM/EMEA timezone detection
- [x] Job posting analysis

### ✅ Global Hiring Score
- [x] Formula: Funding / Median US Salary
- [x] Threshold logic for offshore necessity
- [x] Team mix recommendations
- [x] ROI calculations

### ✅ OSINT Lead Scoring
- [x] `pygooglenews` / `GoogleNews` scraping
- [x] `NLTK` / `TextBlob` sentiment analysis (free)
- [x] Heuristic scoring (Series A/B +50, Layoffs -100)
- [x] JSON output with hiring windows

### ✅ Code Quality
- [x] All comments in English
- [x] Documentation in English
- [x] Data schemas in English
- [x] Clean, readable code structure

### ✅ Constraints
- [x] Only open-source libraries
- [x] No OpenAI/Anthropic API calls
- [x] No paid services required
- [x] Runs for free

## 📊 Example Output

```json
{
  "metadata": {
    "generated_at": "2025-12-21T10:30:00",
    "total_leads": 15,
    "high_priority_leads": 3
  },
  "leads": [
    {
      "company_name": "TechStartup Inc",
      "source_url": "https://techcrunch.com/...",
      "growth_score": 110,
      "predicted_hiring_window": "Next 1-2 months (High Priority)",
      "global_hiring_score": 47.5,
      "must_hire_offshore": true,
      "offshore_percentage": 60,
      "intent_score": 75,
      "outsourcing_intent_detected": true,
      "recommendation": {
        "qualification_score": 85,
        "priority": "Critical - Immediate Outreach",
        "action": "Schedule discovery call within 48 hours"
      }
    }
  ]
}
```

## 🎓 Key Innovations

1. **Zero-Cost Intelligence:** Entire system runs on free open-source libraries
2. **Multi-Source Analysis:** Combines SEC filings + news + NLP + financial scoring
3. **Actionable Insights:** Not just data, but specific hiring windows and recommendations
4. **Scalable Architecture:** Modular design allows independent component usage
5. **Business Logic:** GHS formula provides mathematical justification for offshore hiring

## 📈 Business Value

- **For Sales Teams:** Pre-qualified leads with priority rankings
- **For Market Analysts:** Comprehensive company intelligence
- **For Recruiters:** Hiring window predictions
- **For Finance:** ROI calculations for offshore vs US hiring

## 🔮 Future Enhancements

- [ ] Add CrunchBase API integration
- [ ] Implement company website scraping
- [ ] Add LinkedIn job posting analysis
- [ ] Create real-time alerting system
- [ ] Build Supabase integration for lead storage
- [ ] Add email/Slack notifications

## 📝 Files Added

### Core Engine
- `src/sec_edgar_scraper.py` (390 lines)
- `src/osint_lead_scorer.py` (615 lines)
- `src/intent_classifier.py` (520 lines)
- `src/global_hiring_score.py` (480 lines)
- `src/intent_classification_engine.py` (510 lines)

### Documentation
- `docs/INTENT_CLASSIFICATION_ENGINE.md` (550 lines)
- `docs/QUICK_START_INTENT_ENGINE.md` (150 lines)

### Setup & Examples
- `setup_intent_engine.bat` (Windows setup script)
- `setup_intent_engine.sh` (Linux/Mac setup script)
- `examples/run_intent_classification_pipeline.py` (280 lines)
- `requirements-intent-engine.txt` (Dependencies)

### Configuration
- Updated `README.md` (Added Intent Engine section)
- Updated `requirements.txt` (Added Intent Engine dependencies)

**Total:** ~2,500 lines of production-ready code + comprehensive documentation

## ✨ Summary

Successfully delivered a complete **Intent Classification Engine** that:
- ✅ Scrapes SEC EDGAR for Form D filings
- ✅ Analyzes tech news with free sentiment analysis
- ✅ Detects outsourcing intent using NLP
- ✅ Calculates Global Hiring Score with financial logic
- ✅ Uses ONLY open-source libraries (no paid APIs)
- ✅ Produces clean JSON output in English
- ✅ Includes comprehensive documentation and examples

**Ready for production use!** 🚀
