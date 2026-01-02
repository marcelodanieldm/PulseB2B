#!/usr/bin/env python3
"""
GitHub Actions Helper Scripts
Scripts auxiliares para workflows de GitHub Actions
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path


def generate_lead_report():
    """Genera reporte de leads de alto valor"""
    try:
        with open('data/output/high_value_leads.json', 'r') as f:
            leads = json.load(f)
        
        report = f'''# High-Value Lead Report
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Summary
- Total Leads: {len(leads)}
- Threshold: {os.getenv('SCORE_THRESHOLD', '250')} points

## Top Leads
'''
        
        for i, lead in enumerate(leads[:10], 1):
            report += f"""{i}. **{lead.get('company_name', 'Unknown')}**
   - Score: {lead.get('priority_score', 0)} points
   - Size: {lead.get('company_size', 'N/A')} employees
   - Industry: {lead.get('industry', 'N/A')}

"""
        
        Path('data/output').mkdir(parents=True, exist_ok=True)
        with open('data/output/lead_report.md', 'w') as f:
            f.write(report)
        
        print('✅ Report generated')
    except Exception as e:
        print(f'⚠️  Error generating report: {e}')


def filter_pulse_90():
    """Filtra companies con Pulse score >= 90"""
    import glob
    import pandas as pd
    
    reports_dir = Path('data/output/pulse_reports')
    reports_dir.mkdir(parents=True, exist_ok=True)
    
    critical_files = list(reports_dir.glob('critical_opportunities_*.csv'))
    
    if not critical_files:
        print('No critical opportunities found')
        return
    
    latest_file = max(critical_files, key=lambda x: x.stat().st_mtime)
    df = pd.read_csv(latest_file)
    
    # Filter for 90+ score
    pulse_90 = df[df['pulse_score'] >= 90].copy()
    
    print(f'Found {len(pulse_90)} companies with Pulse score ≥90')
    
    # Save for Telegram
    pulse_90_list = pulse_90.to_dict('records')
    with open('data/output/pulse_90_critical.json', 'w') as f:
        json.dump(pulse_90_list, f, indent=2)
    
    print('✅ Filtered data saved')


def analyze_regional_expansion():
    """Analiza expansión regional"""
    sys.path.insert(0, 'scripts')
    from regional_nlp_recognizer import RegionalEntityRecognizer
    
    recognizer = RegionalEntityRecognizer()
    
    # Sample companies to analyze
    test_cases = [
        {
            'name': 'Tech Corp',
            'text': 'Company expanding to Mexico City and São Paulo. Opening offices in Latin America with $50M funding.'
        },
        {
            'name': 'Global Startup',
            'text': 'Scaling operations across Argentina, Chile, and Colombia. Hiring 100+ engineers in LATAM.'
        }
    ]
    
    critical_opportunities = []
    
    for case in test_cases:
        analysis = recognizer.analyze_text(case['text'], case['name'])
        if analysis.get('is_critical_opportunity', False):
            critical_opportunities.append({
                'company': case['name'],
                'score': analysis.get('critical_hiring_score', 0),
                'regions': analysis.get('latam_countries', []),
                'signals': len(analysis.get('expansion_signals', []))
            })
    
    # Save results
    Path('data/output').mkdir(parents=True, exist_ok=True)
    with open('data/output/regional_critical.json', 'w') as f:
        json.dump(critical_opportunities, f, indent=2)
    
    print(f'Found {len(critical_opportunities)} critical opportunities')


def generate_weekly_stats():
    """Genera estadísticas semanales"""
    import pandas as pd
    import glob
    
    stats = {
        'week': datetime.now().strftime('%Y-W%W'),
        'generated_at': datetime.now().isoformat(),
        'total_companies_analyzed': 0,
        'critical_alerts_sent': 0,
        'funding_alerts': 0,
        'regional_alerts': 0,
        'high_value_leads': 0,
        'pulse_90_alerts': 0,
        'avg_pulse_score': 0,
        'top_companies': []
    }
    
    # Collect from various sources
    output_dir = Path('data/output')
    
    # Count Oracle predictions
    oracle_files = list(output_dir.glob('oracle/oracle_predictions_*.csv'))
    if oracle_files:
        latest_oracle = max(oracle_files, key=lambda x: x.stat().st_mtime)
        df = pd.read_csv(latest_oracle)
        stats['total_companies_analyzed'] = len(df)
        
        # Count funding alerts (≥85% probability)
        if 'Hiring Probability (%)' in df.columns:
            stats['funding_alerts'] = len(df[df['Hiring Probability (%)'] >= 85])
    
    # Count Pulse reports
    pulse_dir = output_dir / 'pulse_reports'
    if pulse_dir.exists():
        critical_files = list(pulse_dir.glob('critical_opportunities_*.csv'))
        if critical_files:
            latest_pulse = max(critical_files, key=lambda x: x.stat().st_mtime)
            df_pulse = pd.read_csv(latest_pulse)
            
            if 'pulse_score' in df_pulse.columns:
                stats['avg_pulse_score'] = round(df_pulse['pulse_score'].mean(), 1)
                stats['pulse_90_alerts'] = len(df_pulse[df_pulse['pulse_score'] >= 90])
                
                # Get top companies
                top_companies = df_pulse.nlargest(10, 'pulse_score')
                stats['top_companies'] = [
                    {
                        'name': row.get('company_name', 'Unknown'),
                        'score': int(row.get('pulse_score', 0)),
                        'type': 'Pulse Intelligence'
                    }
                    for _, row in top_companies.iterrows()
                ]
    
    # Save stats
    output_dir.mkdir(parents=True, exist_ok=True)
    with open(output_dir / 'weekly_stats.json', 'w') as f:
        json.dump(stats, f, indent=2)
    
    print(json.dumps(stats, indent=2))


def send_pulse_90_alerts():
    """Envía alertas de Telegram para companies con Pulse ≥90"""
    import asyncio
    try:
        from telegram import Bot
    except ImportError:
        print("⚠️  python-telegram-bot not installed")
        print("Install with: pip install python-telegram-bot")
        return
    
    async def send_alerts():
        bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
        chat_id = os.getenv('TELEGRAM_CHAT_ID')
        
        if not bot_token or not chat_id:
            print('⚠️  Telegram not configured')
            return
        
        try:
            with open('data/output/pulse_90_critical.json', 'r') as f:
                companies = json.load(f)
        except:
            print('No critical companies found')
            return
        
        if len(companies) == 0:
            print('No companies with Pulse ≥90')
            return
        
        bot = Bot(bot_token)
        
        # Check alert log for deduplication
        alert_log_path = Path('data/output/alert_log.json')
        alert_log = {}
        
        if alert_log_path.exists():
            with open(alert_log_path, 'r') as f:
                alert_log = json.load(f)
        
        sent = 0
        
        for company in companies[:10]:  # Max 10 alerts
            company_name = company.get('company_name', 'Unknown')
            
            # Check if already alerted in last 24h
            if company_name in alert_log:
                print(f'⏭️  Skipping {company_name} (recently alerted)')
                continue
            
            score = company.get('pulse_score', 0)
            emoji = '🔥🔥🔥' if score >= 95 else '🔥🔥'
            
            message = f'''{emoji} <b>CRITICAL OPPORTUNITY</b> {emoji}

<b>{company_name}</b>
Pulse Score: <b>{score}/100</b>
Desperation: <b>{company.get('desperation_level', 'HIGH')}</b>

📊 <b>Signals:</b>
• Tech Stack: {company.get('tech_diversity_score', 0)} technologies
• Hiring Probability: {company.get('hiring_probability', 'N/A')}%

💡 <b>Contact immediately - Company desperately hiring</b>

🔗 {company.get('website', 'N/A')}

⏰ <i>Detected: {datetime.now().strftime('%b %d, %Y %I:%M %p')}</i>'''
            
            try:
                await bot.send_message(chat_id=chat_id, text=message, parse_mode='HTML')
                print(f'✅ Alert sent for {company_name} ({score}/100)')
                
                # Log alert
                alert_log[company_name] = datetime.now().isoformat()
                sent += 1
                
            except Exception as e:
                print(f'❌ Error sending alert for {company_name}: {e}')
        
        # Save alert log
        Path('data/output').mkdir(parents=True, exist_ok=True)
        with open(alert_log_path, 'w') as f:
            json.dump(alert_log, f, indent=2)
        
        print(f'\n✅ Sent {sent} Pulse 90+ alerts')
    
    asyncio.run(send_alerts())


def send_regional_alerts():
    """Envía alertas regionales a Telegram"""
    import asyncio
    try:
        from telegram import Bot
    except ImportError:
        print("⚠️  python-telegram-bot not installed")
        return
    
    async def send_alerts():
        bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
        chat_id = os.getenv('TELEGRAM_CHAT_ID')
        
        if not bot_token or not chat_id:
            print('⚠️  Telegram not configured')
            return
        
        try:
            with open('data/output/regional_critical.json', 'r') as f:
                opportunities = json.load(f)
        except:
            print('No regional opportunities found')
            return
        
        if len(opportunities) == 0:
            print('No regional opportunities')
            return
        
        bot = Bot(bot_token)
        sent = 0
        
        for opp in opportunities[:5]:  # Max 5 alerts
            message = f'''🌎 <b>REGIONAL EXPANSION ALERT</b> 🌎

<b>{opp['company']}</b>
Arbitrage Score: <b>{opp['score']}/100</b>

📍 <b>Expanding to:</b> {', '.join(opp['regions'])}
📊 <b>Expansion Signals:</b> {opp['signals']}

💡 <b>Perfect timing for B2B outreach!</b>

⏰ <i>Detected: {datetime.now().strftime('%b %d, %Y %I:%M %p')}</i>'''
            
            try:
                await bot.send_message(chat_id=chat_id, text=message, parse_mode='HTML')
                print(f'✅ Regional alert sent for {opp["company"]}')
                sent += 1
            except Exception as e:
                print(f'❌ Error: {e}')
        
        print(f'\n✅ Sent {sent} regional alerts')
    
    asyncio.run(send_alerts())


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python github_actions_helpers.py <function_name>")
        print("Available functions:")
        print("  - generate_lead_report")
        print("  - filter_pulse_90")
        print("  - analyze_regional_expansion")
        print("  - generate_weekly_stats")
        print("  - send_pulse_90_alerts")
        print("  - send_regional_alerts")
        sys.exit(1)
    
    function_name = sys.argv[1]
    
    if function_name == 'generate_lead_report':
        generate_lead_report()
    elif function_name == 'filter_pulse_90':
        filter_pulse_90()
    elif function_name == 'analyze_regional_expansion':
        analyze_regional_expansion()
    elif function_name == 'generate_weekly_stats':
        generate_weekly_stats()
    elif function_name == 'send_pulse_90_alerts':
        send_pulse_90_alerts()
    elif function_name == 'send_regional_alerts':
        send_regional_alerts()
    else:
        print(f"Unknown function: {function_name}")
        sys.exit(1)
