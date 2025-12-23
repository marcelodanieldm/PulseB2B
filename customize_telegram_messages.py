"""
Telegram Message Customizer
============================
Personaliza el formato y contenido de los mensajes de Telegram.
"""

from pathlib import Path
from datetime import datetime
from typing import Dict, List


class TelegramMessageFormatter:
    """Clase para personalizar mensajes de Telegram"""
    
    # Temas de color/emojis
    THEMES = {
        'default': {
            'success': '✅',
            'error': '❌',
            'warning': '⚠️',
            'info': 'ℹ️',
            'rocket': '🚀',
            'chart': '📊',
            'brain': '🧠',
            'globe': '🌎',
            'crystal': '🔮',
            'link': '🔗',
            'target': '🎯',
            'bulb': '💡',
            'clock': '⏱️'
        },
        'minimal': {
            'success': '✓',
            'error': '✗',
            'warning': '!',
            'info': 'i',
            'rocket': '→',
            'chart': '▪',
            'brain': '●',
            'globe': '○',
            'crystal': '◆',
            'link': '▸',
            'target': '◉',
            'bulb': '◐',
            'clock': '◷'
        },
        'professional': {
            'success': '✓',
            'error': '✗',
            'warning': '△',
            'info': '▪',
            'rocket': '▸',
            'chart': '■',
            'brain': '●',
            'globe': '◯',
            'crystal': '◆',
            'link': '▹',
            'target': '◉',
            'bulb': '◐',
            'clock': '⏲'
        }
    }
    
    def __init__(self, theme: str = 'default'):
        """Initialize formatter with theme"""
        self.theme = self.THEMES.get(theme, self.THEMES['default'])
    
    def format_simple_report(self, test_results: Dict, custom_title: str = None) -> str:
        """Formato simple y conciso"""
        
        total = test_results.get('total_tests', 0)
        passed = test_results.get('passed_tests', 0)
        success_rate = (passed / total * 100) if total > 0 else 0
        
        title = custom_title or "PULSEB2B - VALIDACIÓN DE SISTEMA"
        
        message = f"""{self.theme['rocket']} <b>{title}</b> {self.theme['rocket']}

{self.theme['clock']} <i>{datetime.now().strftime('%d/%m/%Y %H:%M')}</i>

━━━━━━━━━━━━━━━━━━━━━━━━━━━━

{self.theme['chart']} <b>RESULTADO:</b>
{self.theme['success']} Tests: <code>{passed}/{total}</code>
{self.theme['chart']} Éxito: <b>{success_rate:.1f}%</b>
{self.theme['target']} Estado: <b>{"OPERATIVO" if success_rate >= 90 else "EN DESARROLLO"}</b>

━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
        
        # Add suite summaries
        for suite in test_results.get('test_suites', []):
            status_icon = self.theme['success'] if suite['status'] == 'PASSED' else self.theme['error']
            message += f"\n{status_icon} {suite['name']}"
        
        message += f"\n\n{self.theme['bulb']} <i>Sistema de inteligencia de mercado</i>"
        
        return message
    
    def format_executive_summary(self, test_results: Dict) -> str:
        """Formato ejecutivo para stakeholders"""
        
        total = test_results.get('total_tests', 0)
        passed = test_results.get('passed_tests', 0)
        success_rate = (passed / total * 100) if total > 0 else 0
        
        message = f"""<b>📊 REPORTE EJECUTIVO - PULSEB2B</b>

<b>Fecha:</b> {datetime.now().strftime('%d %B %Y')}
<b>Sistema:</b> Market Intelligence Platform

━━━━━━━━━━━━━━━━━━━━━━━━━━━━

<b>🎯 RESUMEN:</b>

Estado del Sistema: <b>{"✅ OPERATIVO" if success_rate >= 90 else "⚠️ EN DESARROLLO"}</b>
Tasa de Éxito: <b>{success_rate:.1f}%</b>
Tests Ejecutados: <code>{total}</code>
Tests Pasados: <code>{passed}</code>

━━━━━━━━━━━━━━━━━━━━━━━━━━━━

<b>📈 MÓDULOS VALIDADOS:</b>
"""
        
        for suite in test_results.get('test_suites', []):
            if suite['status'] == 'PASSED':
                message += f"\n✅ {suite['name']}"
                if 'passed_count' in suite:
                    message += f" ({suite['passed_count']} tests)"
        
        message += f"""

━━━━━━━━━━━━━━━━━━━━━━━━━━━━

<b>💡 CONCLUSIÓN:</b>

Sistema listo para {"producción" if success_rate >= 90 else "testing"}. 
Todos los flujos críticos validados.

<i>Próxima revisión: {(datetime.now().replace(day=1, month=datetime.now().month+1 if datetime.now().month < 12 else 1)).strftime('%d/%m/%Y')}</i>
"""
        
        return message
    
    def format_technical_detailed(self, test_results: Dict) -> str:
        """Formato técnico detallado"""
        
        message = """<b>🔧 REPORTE TÉCNICO DETALLADO</b>

━━━━━━━━━━━━━━━━━━━━━━━━━━━━

<b>📋 INFORMACIÓN DEL TEST:</b>

"""
        
        for suite in test_results.get('test_suites', []):
            status_icon = "✅" if suite['status'] == 'PASSED' else "❌"
            message += f"\n{status_icon} <b>{suite['name']}</b>\n"
            message += f"   Status: <code>{suite['status']}</code>\n"
            message += f"   Tiempo: {suite['execution_time']}s\n"
            
            if 'details' in suite:
                for detail in suite['details']:
                    message += f"   • {detail}\n"
        
        message += "\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        
        return message
    
    def format_alert_style(self, test_results: Dict, alert_level: str = 'info') -> str:
        """Formato de alerta para notificaciones importantes"""
        
        alert_emojis = {
            'critical': '🚨',
            'warning': '⚠️',
            'success': '✅',
            'info': 'ℹ️'
        }
        
        emoji = alert_emojis.get(alert_level, 'ℹ️')
        
        total = test_results.get('total_tests', 0)
        passed = test_results.get('passed_tests', 0)
        success_rate = (passed / total * 100) if total > 0 else 0
        
        message = f"""{emoji} <b>ALERTA DE SISTEMA</b>

<b>PulseB2B - Validación Automática</b>
{datetime.now().strftime('%d/%m/%Y %H:%M:%S')}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━

<b>Resultado:</b> {success_rate:.1f}% éxito

"""
        
        if success_rate >= 95:
            message += "✅ <b>Sistema operando perfectamente</b>\nTodos los componentes funcionando correctamente."
        elif success_rate >= 90:
            message += "✅ <b>Sistema operativo</b>\nAlgunos warnings menores detectados."
        elif success_rate >= 75:
            message += "⚠️ <b>Sistema funcional con issues</b>\nRequiere atención para algunos módulos."
        else:
            message += "🚨 <b>Sistema requiere atención inmediata</b>\nVarios componentes fallando."
        
        return message
    
    def format_compact(self, test_results: Dict) -> str:
        """Formato ultra compacto para móviles"""
        
        total = test_results.get('total_tests', 0)
        passed = test_results.get('passed_tests', 0)
        success_rate = (passed / total * 100) if total > 0 else 0
        
        return f"""<b>PulseB2B</b>

✅ {passed}/{total} tests
📊 {success_rate:.0f}% éxito
⏱ {test_results.get('execution_time', 0):.1f}s

{"🎯 OPERATIVO" if success_rate >= 90 else "🔧 EN DESARROLLO"}
"""


def generate_custom_reports():
    """Generate custom report variations"""
    
    # Load test results
    import json
    results_file = Path('data/output/critical_flows_report.json')
    
    if not results_file.exists():
        print("❌ No se encontraron resultados de tests")
        print("Ejecuta primero: python test_critical_flows.py")
        return
    
    with open(results_file, 'r', encoding='utf-8') as f:
        test_results = json.load(f)
    
    # Create formatter
    formatter = TelegramMessageFormatter(theme='default')
    
    # Generate different formats
    formats = {
        'simple': formatter.format_simple_report(test_results),
        'executive': formatter.format_executive_summary(test_results),
        'technical': formatter.format_technical_detailed(test_results),
        'alert': formatter.format_alert_style(test_results, 'success'),
        'compact': formatter.format_compact(test_results)
    }
    
    # Save each format
    output_dir = Path('data/output')
    output_dir.mkdir(parents=True, exist_ok=True)
    
    for name, content in formats.items():
        output_file = output_dir / f'telegram_{name}_format.txt'
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✅ Generado: {output_file.name}")
    
    print(f"\n📊 {len(formats)} formatos personalizados creados")
    print(f"📁 Ubicación: {output_dir}")
    
    # Show preview
    print("\n" + "="*60)
    print("📱 VISTA PREVIA - FORMATO COMPACTO:")
    print("="*60)
    print(formats['compact'])
    print("="*60)


if __name__ == '__main__':
    print("="*60)
    print("🎨 GENERADOR DE FORMATOS PERSONALIZADOS")
    print("="*60)
    print()
    
    generate_custom_reports()
    
    print("\n💡 Para enviar un formato específico:")
    print("   python send_to_telegram.py --format compact")
    print("   python send_to_telegram.py --format executive")
    print("   python send_to_telegram.py --format alert")
