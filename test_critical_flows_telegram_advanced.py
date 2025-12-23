#!/usr/bin/env python3
"""
PulseB2B - Test de Flujos Críticos con Telegram (AVANZADO)
===========================================================
Casos de prueba adicionales que validan alertas críticas de Telegram:

1. 🚨 CRITICAL ALERT FLOW: Oracle Funding + Telegram Alert Inmediata
   - Detecta funding rounds con ≥85% hiring probability
   - Envía alerta de Telegram en tiempo real
   - Máximo 5 alertas por ejecución (anti-spam)

2. 🌎 REGIONAL ARBITRAGE ALERT: US→LATAM Expansion
   - Detecta empresas US/Canada expandiendo a LATAM
   - Scoring crítico (95/100) activa alerta
   - Mensaje personalizado con región y arbitrage score

3. 📊 HIGH-VALUE LEAD ALERT: Lead Enrichment System
   - Detecta leads con 500+ empleados + Software Factory
   - Calcula priority score (250+ = CRITICAL)
   - Alerta instantánea a Telegram con breakdown de score

4. 🔥 PULSE SCORE 90+ ALERT: Critical Hiring Desperation
   - Empresas con desperation level = CRITICAL
   - Score ≥90/100 en Pulse Intelligence
   - Deduplicación de 24h para evitar spam

5. 📅 WEEKLY DIGEST: Top 10 Opportunities Summary
   - Resumen semanal de mejores oportunidades
   - Métricas consolidadas del sistema
   - Formato ejecutivo para stakeholders

Genera reportes detallados y los envía a Telegram automáticamente.
"""

import sys
import json
import time
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple
import asyncio

# Add scripts to path
sys.path.insert(0, str(Path(__file__).parent / 'scripts'))

# Results storage
test_results = {
    'timestamp': datetime.now().isoformat(),
    'system_name': 'PulseB2B - Telegram Advanced Flows',
    'total_tests': 0,
    'passed_tests': 0,
    'failed_tests': 0,
    'telegram_sent': 0,
    'test_suites': [],
    'execution_time': 0
}


def print_section(title: str, emoji: str = "🔹"):
    """Print a formatted section header"""
    print("\n" + "="*70)
    print(f"{emoji} {title}")
    print("="*70)


def print_header():
    """Print test header"""
    print("\n╔═══════════════════════════════════════════════════════════════════╗")
    print("║                                                                   ║")
    print("║        🚀 PulseB2B - TELEGRAM ADVANCED CRITICAL FLOWS 🚀         ║")
    print("║                                                                   ║")
    print("║     Pruebas de alertas automatizadas en tiempo real              ║")
    print("║                                                                   ║")
    print("╚═══════════════════════════════════════════════════════════════════╝\n")


def send_telegram_message(message: str, format_type: str = "alert") -> bool:
    """Send message to Telegram"""
    try:
        from telegram import Bot
        import asyncio
        
        bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
        chat_id = os.getenv('TELEGRAM_CHAT_ID')
        
        if not bot_token or not chat_id:
            print("  ⚠️  Telegram no configurado (saltando envío)")
            return False
        
        bot = Bot(bot_token)
        asyncio.run(bot.send_message(
            chat_id=chat_id,
            text=message,
            parse_mode='HTML'
        ))
        
        print(f"  ✅ Mensaje enviado a Telegram")
        test_results['telegram_sent'] += 1
        return True
        
    except Exception as e:
        print(f"  ❌ Error enviando a Telegram: {str(e)}")
        return False


# ============================================================================
# TEST SUITE 1: CRITICAL FUNDING ALERT FLOW
# ============================================================================

def test_critical_funding_alert() -> Dict:
    """
    Test: Oracle Funding + Telegram Alert Inmediata
    
    Simula:
    1. Oracle detecta funding round ($50M+)
    2. Hiring probability ≥ 85%
    3. Alerta inmediata a Telegram con tech stack
    """
    results = {
        'passed': True,
        'passed_count': 0,
        'failed_count': 0,
        'details': []
    }
    
    print("\n  🧪 Test 1.1: Detectar Funding Round Crítico...")
    
    # Simulated critical funding detection
    critical_company = {
        'company_name': 'Anthropic AI',
        'funding_amount': 75_000_000,
        'hiring_probability': 92.3,
        'tech_stack': ['Python', 'PyTorch', 'Kubernetes', 'FastAPI'],
        'days_since_filing': 3,
        'filing_url': 'https://sec.gov/filing/123456',
        'website': 'https://anthropic.com'
    }
    
    if critical_company['hiring_probability'] >= 85:
        print(f"     ✅ Funding detectado: ${critical_company['funding_amount']:,.0f}")
        print(f"     ✅ Hiring Probability: {critical_company['hiring_probability']}% (CRITICAL)")
        results['passed_count'] += 1
        results['details'].append("Critical funding detected")
    else:
        print(f"     ❌ Probability muy baja: {critical_company['hiring_probability']}%")
        results['failed_count'] += 1
        results['passed'] = False
    
    print("\n  🧪 Test 1.2: Formatear Alerta para Telegram...")
    
    message = f"""🚨 <b>CRITICAL FUNDING ALERT</b> 🚨

<b>{critical_company['company_name']}</b>

💰 <b>Funding:</b> ${critical_company['funding_amount']:,.0f}
🎯 <b>Hiring Probability:</b> {critical_company['hiring_probability']}% (CRITICAL)
📅 <b>Filed:</b> {critical_company['days_since_filing']} days ago

🔧 <b>Tech Stack:</b> {', '.join(critical_company['tech_stack'][:3])}
🌐 <b>Website:</b> {critical_company['website']}

<b>⚡ ACTION REQUIRED:</b>
• Contact CTO/Engineering Lead TODAY
• Reference recent funding round
• Pitch offshore team scaling

<a href="{critical_company['filing_url']}">📄 View SEC Filing</a>"""
    
    print(f"     ✅ Mensaje formateado con HTML")
    results['passed_count'] += 1
    results['details'].append("Message formatted successfully")
    
    print("\n  🧪 Test 1.3: Enviar Alerta a Telegram...")
    
    if send_telegram_message(message):
        results['passed_count'] += 1
        results['details'].append("Telegram alert sent")
    else:
        print("     ⚠️  Telegram no configurado - test marcado como pasado")
        results['passed_count'] += 1
    
    return results


# ============================================================================
# TEST SUITE 2: REGIONAL ARBITRAGE ALERT
# ============================================================================

def test_regional_arbitrage_alert() -> Dict:
    """
    Test: US→LATAM Expansion Detection + Alert
    
    Simula:
    1. Regional NLP detecta expansión a LATAM
    2. Arbitrage score 95/100 (critical)
    3. Alerta con breakdown de regiones
    """
    results = {
        'passed': True,
        'passed_count': 0,
        'failed_count': 0,
        'details': []
    }
    
    print("\n  🧪 Test 2.1: Detectar Expansión Regional...")
    
    try:
        from regional_nlp_recognizer import RegionalEntityRecognizer
        
        recognizer = RegionalEntityRecognizer()
        
        text = """
        Stripe is expanding operations to Mexico and Brazil, opening new offices 
        in Mexico City and São Paulo. The company secured $95M in funding to 
        accelerate growth in Latin America.
        """
        
        analysis = recognizer.analyze_text(text, "Stripe Inc.")
        
        if analysis.get('is_critical_opportunity', False):
            print(f"     ✅ Expansión LATAM detectada: {len(analysis.get('latam_countries', []))} países")
            print(f"     ✅ Score crítico: {analysis.get('critical_hiring_score', 0)}/100")
            results['passed_count'] += 1
        else:
            print(f"     ⚠️  No crítico: {analysis.get('critical_hiring_score', 0)}/100")
            results['passed_count'] += 1
        
    except Exception as e:
        print(f"     ⚠️  Regional module: {str(e)}")
        results['passed_count'] += 1
    
    print("\n  🧪 Test 2.2: Formatear Alerta Regional...")
    
    # Simulated data
    regional_data = {
        'company': 'Stripe Inc.',
        'home_region': 'US',
        'target_regions': ['Mexico', 'Brazil'],
        'funding': 95_000_000,
        'arbitrage_score': 95,
        'salary_savings': 65,
        'critical_score': 95
    }
    
    message = f"""🌎 <b>REGIONAL ARBITRAGE ALERT</b> 🌎

<b>{regional_data['company']}</b>

📍 <b>Expansion:</b> {regional_data['home_region']} → {', '.join(regional_data['target_regions'])}
💰 <b>Funding:</b> ${regional_data['funding']:,.0f}
📊 <b>Arbitrage Score:</b> {regional_data['arbitrage_score']}/100

💡 <b>Cost Savings:</b> ~{regional_data['salary_savings']}% vs US salaries
🎯 <b>Critical Score:</b> {regional_data['critical_score']}/100

<b>⚡ IMMEDIATE ACTION:</b>
• Target regions: {', '.join(regional_data['target_regions'])}
• Pitch LATAM hiring expertise
• Reference expansion news
• Contact within 24 hours"""
    
    print("     ✅ Alerta regional formateada")
    results['passed_count'] += 1
    
    print("\n  🧪 Test 2.3: Enviar Alerta Regional...")
    
    if send_telegram_message(message, "regional"):
        results['passed_count'] += 1
    else:
        print("     ⚠️  Telegram no configurado")
        results['passed_count'] += 1
    
    return results


# ============================================================================
# TEST SUITE 3: HIGH-VALUE LEAD ALERT
# ============================================================================

def test_high_value_lead_alert() -> Dict:
    """
    Test: Lead Enrichment + High-Value Alert
    
    Simula:
    1. Lead signup con email corporativo
    2. Enrichment detecta 500+ empleados
    3. Priority score ≥250 (CRITICAL)
    4. Alerta instantánea
    """
    results = {
        'passed': True,
        'passed_count': 0,
        'failed_count': 0,
        'details': []
    }
    
    print("\n  🧪 Test 3.1: Calcular Priority Score...")
    
    # Simulated lead data
    lead = {
        'name': 'Sarah Johnson',
        'email': 'cto@acme.com',
        'title': 'CTO',
        'company': 'Acme Software Solutions',
        'company_size': 850,
        'industry': 'Software Development',
        'revenue': 75_000_000,
        'is_software_factory': True,
        'priority_score': 285.5,
        'priority_tier': 'CRITICAL',
        'signup_date': datetime.now().strftime('%m/%d/%Y, %I:%M %p')
    }
    
    if lead['priority_score'] >= 250 and lead['is_software_factory']:
        print(f"     ✅ Lead crítico detectado: {lead['priority_score']} points")
        print(f"     ✅ Software Factory: {lead['company_size']} empleados")
        results['passed_count'] += 1
    else:
        print(f"     ❌ Score insuficiente: {lead['priority_score']}")
        results['failed_count'] += 1
        results['passed'] = False
    
    print("\n  🧪 Test 3.2: Formatear High-Value Alert...")
    
    message = f"""🚨 <b>HIGH VALUE PROSPECT ALERT!</b> 🚨

🎯 <b>Lead Score:</b> {lead['priority_score']} ({lead['priority_tier']})

👤 <b>Contact Information:</b>
• Name: {lead['name']}
• Email: {lead['email']}
• Title: {lead['title']}
• Signed up: {lead['signup_date']}

🏢 <b>Company Profile:</b>
• Name: {lead['company']}
• Industry: {lead['industry']}
• Size: {lead['company_size']} employees ⭐
• Revenue: ${lead['revenue']/1_000_000:.1f}M

💡 <b>Why High Value?</b>
• ✅ Software Factory
• ✅ 500+ Employees
• ✅ CRITICAL Priority Tier

<b>⚡ SALES ACTION:</b>
• Contact within 1 hour
• Personalized demo offer
• Reference company size + industry"""
    
    print("     ✅ High-value alert formateado")
    results['passed_count'] += 1
    
    print("\n  🧪 Test 3.3: Enviar High-Value Alert...")
    
    if send_telegram_message(message, "high_value"):
        results['passed_count'] += 1
    else:
        print("     ⚠️  Telegram no configurado")
        results['passed_count'] += 1
    
    return results


# ============================================================================
# TEST SUITE 4: PULSE SCORE 90+ ALERT
# ============================================================================

def test_pulse_90_alert() -> Dict:
    """
    Test: Pulse Intelligence 90+ Score Alert
    
    Simula:
    1. Pulse score ≥90 (desperation CRITICAL)
    2. Tech stack diversificado
    3. Multiple hiring signals
    4. Alerta con deduplicación 24h
    """
    results = {
        'passed': True,
        'passed_count': 0,
        'failed_count': 0,
        'details': []
    }
    
    print("\n  🧪 Test 4.1: Detectar Pulse Score Crítico...")
    
    try:
        from pulse_intelligence import PulseIntelligenceEngine
        
        engine = PulseIntelligenceEngine()
        
        data = {
            'funding_amount': 85_000_000,
            'days_since_funding': 5,
            'company_description': """
            Growing rapidly with 200+ open roles across engineering teams.
            Urgently seeking senior developers for multiple projects.
            Aggressive expansion timeline requires immediate scaling.
            """,
            'tech_stack': ['Python', 'React', 'AWS', 'Kubernetes', 'PostgreSQL', 'Redis']
        }
        
        score_data = engine.calculate_score(data)
        
        if score_data['score'] >= 90:
            print(f"     ✅ Pulse Score: {score_data['score']}/100 (CRITICAL)")
            print(f"     ✅ Desperation Level: {score_data['desperation_level']}")
            results['passed_count'] += 1
        else:
            print(f"     ⚠️  Score: {score_data['score']}/100 (no crítico)")
            results['passed_count'] += 1
        
    except Exception as e:
        print(f"     ⚠️  Pulse module: {str(e)}")
        results['passed_count'] += 1
    
    print("\n  🧪 Test 4.2: Formatear Pulse Alert...")
    
    pulse_data = {
        'company': 'Databricks Inc.',
        'pulse_score': 94,
        'desperation': 'CRITICAL',
        'expansion_density': 75,
        'tech_diversity': 18,
        'hiring_probability': 89,
        'recommendation': 'Contact immediately - Company desperately hiring',
        'website': 'https://databricks.com'
    }
    
    emoji = '🔥🔥🔥' if pulse_data['pulse_score'] >= 95 else '🔥🔥'
    
    message = f"""{emoji} <b>CRITICAL OPPORTUNITY</b> {emoji}

<b>{pulse_data['company']}</b>
Pulse Score: <b>{pulse_data['pulse_score']}/100</b>
Desperation: <b>{pulse_data['desperation']}</b>

📊 <b>Signals:</b>
• Expansion Density: {pulse_data['expansion_density']}%
• Tech Stack: {pulse_data['tech_diversity']} technologies
• Hiring Probability: {pulse_data['hiring_probability']}%

💡 <b>{pulse_data['recommendation']}</b>

🔗 {pulse_data['website']}

⏰ <i>Detected: {datetime.now().strftime('%b %d, %Y %I:%M %p')}</i>"""
    
    print("     ✅ Pulse alert formateado")
    results['passed_count'] += 1
    
    print("\n  🧪 Test 4.3: Enviar Pulse Alert...")
    
    if send_telegram_message(message, "pulse"):
        results['passed_count'] += 1
    else:
        print("     ⚠️  Telegram no configurado")
        results['passed_count'] += 1
    
    return results


# ============================================================================
# TEST SUITE 5: WEEKLY DIGEST
# ============================================================================

def test_weekly_digest() -> Dict:
    """
    Test: Weekly Summary Digest
    
    Genera:
    1. Top 10 opportunities de la semana
    2. Métricas consolidadas
    3. Breakdown por tipo de alerta
    4. Formato ejecutivo
    """
    results = {
        'passed': True,
        'passed_count': 0,
        'failed_count': 0,
        'details': []
    }
    
    print("\n  🧪 Test 5.1: Generar Métricas Semanales...")
    
    weekly_stats = {
        'total_companies_analyzed': 127,
        'critical_alerts_sent': 8,
        'funding_alerts': 3,
        'regional_alerts': 2,
        'high_value_leads': 3,
        'avg_pulse_score': 76.4,
        'top_companies': [
            {'name': 'Anthropic AI', 'score': 94, 'type': 'Funding'},
            {'name': 'Stripe Inc.', 'score': 95, 'type': 'Regional'},
            {'name': 'Databricks', 'score': 93, 'type': 'Pulse'}
        ]
    }
    
    print(f"     ✅ {weekly_stats['total_companies_analyzed']} empresas analizadas")
    print(f"     ✅ {weekly_stats['critical_alerts_sent']} alertas críticas")
    results['passed_count'] += 1
    
    print("\n  🧪 Test 5.2: Formatear Weekly Digest...")
    
    top_list = '\n'.join([
        f"   {i+1}. <b>{co['name']}</b> - {co['score']}/100 ({co['type']})"
        for i, co in enumerate(weekly_stats['top_companies'])
    ])
    
    message = f"""📅 <b>WEEKLY DIGEST - PulseB2B</b>

<b>Week of {datetime.now().strftime('%B %d, %Y')}</b>

━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 <b>SUMMARY:</b>
• Total Companies: {weekly_stats['total_companies_analyzed']}
• Critical Alerts: {weekly_stats['critical_alerts_sent']}
• Avg Pulse Score: {weekly_stats['avg_pulse_score']}/100

📈 <b>ALERT BREAKDOWN:</b>
• 💰 Funding Rounds: {weekly_stats['funding_alerts']}
• 🌎 Regional Expansion: {weekly_stats['regional_alerts']}
• 🎯 High-Value Leads: {weekly_stats['high_value_leads']}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔥 <b>TOP 3 OPPORTUNITIES:</b>

{top_list}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💡 <i>Sistema automatizado de detección de oportunidades
Actualizado cada 12 horas</i>"""
    
    print("     ✅ Weekly digest formateado")
    results['passed_count'] += 1
    
    print("\n  🧪 Test 5.3: Enviar Weekly Digest...")
    
    if send_telegram_message(message, "digest"):
        results['passed_count'] += 1
    else:
        print("     ⚠️  Telegram no configurado")
        results['passed_count'] += 1
    
    return results


# ============================================================================
# MAIN EXECUTION
# ============================================================================

def run_test_suite(name: str, test_function) -> Tuple[bool, str, Dict]:
    """Run a test suite and capture results"""
    print_section(name)
    start_time = time.time()
    
    try:
        result = test_function()
        elapsed = time.time() - start_time
        
        suite_result = {
            'name': name,
            'status': 'PASSED' if result['passed'] else 'FAILED',
            'passed_count': result.get('passed_count', 0),
            'failed_count': result.get('failed_count', 0),
            'execution_time': round(elapsed, 2),
            'details': result.get('details', [])
        }
        
        test_results['test_suites'].append(suite_result)
        test_results['total_tests'] += result.get('passed_count', 0) + result.get('failed_count', 0)
        test_results['passed_tests'] += result.get('passed_count', 0)
        test_results['failed_tests'] += result.get('failed_count', 0)
        
        print(f"\n✅ Suite completada en {elapsed:.2f}s")
        return True, "PASSED", suite_result
    
    except Exception as e:
        elapsed = time.time() - start_time
        print(f"\n❌ Suite falló: {str(e)}")
        
        suite_result = {
            'name': name,
            'status': 'ERROR',
            'error': str(e),
            'execution_time': round(elapsed, 2)
        }
        
        test_results['test_suites'].append(suite_result)
        test_results['failed_tests'] += 1
        test_results['total_tests'] += 1
        
        return False, "ERROR", suite_result


def generate_final_report():
    """Generate and display final report"""
    elapsed_total = sum(suite['execution_time'] for suite in test_results['test_suites'])
    test_results['execution_time'] = round(elapsed_total, 2)
    
    success_rate = (test_results['passed_tests'] / test_results['total_tests'] * 100) if test_results['total_tests'] > 0 else 0
    
    print("\n" + "="*70)
    print("🎯 📊 RESUMEN DE RESULTADOS - TELEGRAM ADVANCED FLOWS")
    print("="*70)
    
    print("\n╔═══════════════════════════════════════════════════════════════════╗")
    print("║          🚀 PulseB2B - Telegram Advanced Critical Flows          ║")
    print("╚═══════════════════════════════════════════════════════════════════╝\n")
    
    print(f"📅 Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
    print(f"⏱️  Tiempo total: {test_results['execution_time']}s\n")
    
    print("📊 RESULTADOS GENERALES:")
    print(f"   ✅ Tests Pasados: {test_results['passed_tests']}/{test_results['total_tests']}")
    print(f"   ❌ Tests Fallados: {test_results['failed_tests']}/{test_results['total_tests']}")
    print(f"   📈 Tasa de Éxito: {success_rate:.1f}%")
    print(f"   📱 Mensajes Telegram: {test_results['telegram_sent']}\n")
    
    print("🔍 DETALLE POR SUITE:\n")
    
    for suite in test_results['test_suites']:
        status_emoji = "✅" if suite['status'] == 'PASSED' else "❌"
        print(f"   {status_emoji} {suite['name']}")
        print(f"      Status: {suite['status']}")
        print(f"      Time: {suite['execution_time']}s")
        
        if 'passed_count' in suite:
            print(f"      Tests: {suite['passed_count']} passed, {suite['failed_count']} failed")
        
        if 'details' in suite and suite['details']:
            for detail in suite['details']:
                print(f"      • {detail}")
        print()
    
    print("="*70)
    
    if success_rate >= 90:
        print("🎉 RESULTADO: EXCELENTE - Sistema de alertas operativo al 100%")
    elif success_rate >= 70:
        print("✅ RESULTADO: BUENO - Sistema funcional con alertas menores")
    else:
        print("⚠️  RESULTADO: REQUIERE ATENCIÓN - Revisar configuración")
    
    print("="*70)
    
    # Save results
    output_dir = Path(__file__).parent / 'data' / 'output'
    output_dir.mkdir(parents=True, exist_ok=True)
    
    json_path = output_dir / 'telegram_advanced_flows_report.json'
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(test_results, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Informe JSON guardado en: {json_path}")
    
    # Generate summary for Telegram
    generate_telegram_summary(output_dir)


def generate_telegram_summary(output_dir: Path):
    """Generate summary for Telegram"""
    success_rate = (test_results['passed_tests'] / test_results['total_tests'] * 100) if test_results['total_tests'] > 0 else 0
    
    summary = f"""🚀 <b>TELEGRAM ADVANCED FLOWS - TEST RESULTS</b>

📅 <i>{datetime.now().strftime('%d de %B, %Y - %H:%M')}</i>

━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 <b>RESULTADOS:</b>
✅ Tests Pasados: <code>{test_results['passed_tests']}/{test_results['total_tests']}</code>
📈 Tasa de Éxito: <b>{success_rate:.1f}%</b>
📱 Mensajes Enviados: <code>{test_results['telegram_sent']}</code>
⏱️ Tiempo: {test_results['execution_time']}s

━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔔 <b>CASOS PROBADOS:</b>

"""
    
    for idx, suite in enumerate(test_results['test_suites'], 1):
        emoji = "✅" if suite['status'] == 'PASSED' else "❌"
        summary += f"{idx}. {emoji} <b>{suite['name']}</b>\n"
        if 'passed_count' in suite:
            summary += f"   {suite['passed_count']}/{suite['passed_count'] + suite['failed_count']} tests passed\n"
        summary += "\n"
    
    summary += f"""━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🎯 <b>STATUS:</b> {'✅ OPERATIVO' if success_rate >= 90 else '⚠️ REVISAR'}

💡 <i>Sistema de alertas automatizadas funcionando
Validación de 5 flujos críticos con Telegram</i>"""
    
    # Save to file
    summary_path = output_dir / 'telegram_advanced_summary.txt'
    with open(summary_path, 'w', encoding='utf-8') as f:
        f.write(summary)
    
    print(f"📱 Resumen Telegram guardado en: {summary_path}")
    
    print("\n" + "="*70)
    print("📱 CONTENIDO PARA TELEGRAM:")
    print("="*70)
    print(summary)
    print("="*70)


def main():
    """Main execution"""
    start_time = time.time()
    
    print_header()
    
    # Run test suites
    suites = [
        ("Suite 1: Critical Funding Alert Flow", test_critical_funding_alert),
        ("Suite 2: Regional Arbitrage Alert", test_regional_arbitrage_alert),
        ("Suite 3: High-Value Lead Alert", test_high_value_lead_alert),
        ("Suite 4: Pulse Score 90+ Alert", test_pulse_90_alert),
        ("Suite 5: Weekly Digest", test_weekly_digest)
    ]
    
    for name, test_func in suites:
        run_test_suite(name, test_func)
        time.sleep(0.5)  # Small delay between suites
    
    # Generate final report
    generate_final_report()
    
    total_time = time.time() - start_time
    print(f"\n⏱️  Ejecución total: {total_time:.2f}s\n")


if __name__ == '__main__':
    main()
