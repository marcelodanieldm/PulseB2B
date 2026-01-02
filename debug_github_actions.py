#!/usr/bin/env python3
"""
GitHub Actions Debugger y Analizador Completo
==============================================
Analiza todos los workflows, detecta errores comunes y genera reporte detallado
"""

import os
import sys
import yaml
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple

class WorkflowDebugger:
    def __init__(self):
        self.workflows_dir = Path(".github/workflows")
        self.results = {
            'timestamp': datetime.now().isoformat(),
            'total_workflows': 0,
            'workflows_with_errors': 0,
            'workflows_with_warnings': 0,
            'workflows_ok': 0,
            'issues': [],
            'recommendations': []
        }
        
    def analyze_all_workflows(self):
        """Analiza todos los workflows y genera reporte"""
        print("\n" + "="*80)
        print("🔍 ANÁLISIS COMPLETO DE GITHUB ACTIONS WORKFLOWS")
        print("="*80 + "\n")
        
        if not self.workflows_dir.exists():
            print("❌ ERROR: Directorio .github/workflows no encontrado")
            return
        
        workflows = list(self.workflows_dir.glob("*.yml")) + list(self.workflows_dir.glob("*.yaml"))
        self.results['total_workflows'] = len(workflows)
        
        print(f"📊 Total de workflows encontrados: {len(workflows)}\n")
        
        for workflow_path in workflows:
            self.analyze_workflow(workflow_path)
        
        self.print_summary()
        self.save_report()
    
    def analyze_workflow(self, workflow_path: Path):
        """Analiza un workflow individual"""
        print(f"\n{'─'*80}")
        print(f"📄 Analizando: {workflow_path.name}")
        print('─'*80)
        
        try:
            with open(workflow_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Intentar parsear YAML
            try:
                workflow_data = yaml.safe_load(content)
            except yaml.YAMLError as e:
                self.add_error(workflow_path.name, "YAML inválido", str(e))
                return
            
            # Análisis de estructura
            self.check_structure(workflow_path.name, workflow_data, content)
            self.check_secrets(workflow_path.name, content)
            self.check_dependencies(workflow_path.name, content)
            self.check_paths(workflow_path.name, content)
            self.check_best_practices(workflow_path.name, workflow_data, content)
            
        except Exception as e:
            self.add_error(workflow_path.name, "Error al leer archivo", str(e))
    
    def check_structure(self, workflow_name: str, data: dict, content: str):
        """Verifica estructura básica del workflow"""
        # Verificar que tenga nombre
        if 'name' not in data:
            self.add_warning(workflow_name, "Falta nombre del workflow", 
                           "Agregar: name: 'Nombre del Workflow'")
        
        # Verificar que tenga triggers (on)
        if 'on' not in data:
            self.add_error(workflow_name, "Falta definición de triggers", 
                         "Agregar sección 'on:' con schedule o workflow_dispatch")
        
        # Verificar que tenga jobs
        if 'jobs' not in data or not data['jobs']:
            self.add_error(workflow_name, "No hay jobs definidos", 
                         "Agregar al menos un job bajo 'jobs:'")
        
        # Verificar sintaxis de cron si existe
        if 'schedule' in data.get('on', {}):
            for schedule in data['on']['schedule']:
                if 'cron' in schedule:
                    cron = schedule['cron']
                    parts = cron.split()
                    if len(parts) != 5:
                        self.add_error(workflow_name, f"Sintaxis cron inválida: {cron}",
                                     "Formato: 'minuto hora día mes día_semana'")
    
    def check_secrets(self, workflow_name: str, content: str):
        """Detecta secretos hardcodeados y variables de entorno faltantes"""
        required_secrets = {
            'SUPABASE_URL': ['supabase', 'database'],
            'SUPABASE_KEY': ['supabase', 'database'],
            'SUPABASE_SERVICE_KEY': ['supabase', 'database'],
            'TELEGRAM_BOT_TOKEN': ['telegram'],
            'TELEGRAM_CHAT_ID': ['telegram'],
            'SENDGRID_API_KEY': ['sendgrid', 'email'],
            'GOOGLE_CSE_API_KEY': ['google', 'search'],
        }
        
        # Detectar uso de secretos
        used_secrets = []
        for line in content.split('\n'):
            if '${{ secrets.' in line:
                secret_name = line.split('secrets.')[1].split(' ')[0].split('}')[0]
                used_secrets.append(secret_name)
        
        # Buscar posibles secretos hardcodeados (patrones peligrosos)
        dangerous_patterns = [
            ('sk-', 'Posible API key de OpenAI'),
            ('xoxb-', 'Posible token de Slack'),
            ('ghp_', 'Posible token de GitHub'),
            ('postgres://', 'Posible URL de base de datos'),
            ('mongodb://', 'Posible URL de MongoDB'),
        ]
        
        for pattern, description in dangerous_patterns:
            if pattern in content and '${{ secrets.' not in content[content.find(pattern)-50:content.find(pattern)+50]:
                self.add_error(workflow_name, "Posible secreto hardcodeado", 
                             f"{description} - Mover a GitHub Secrets")
    
    def check_dependencies(self, workflow_name: str, content: str):
        """Verifica instalación de dependencias"""
        has_python = 'uses: actions/setup-python@' in content
        has_node = 'uses: actions/setup-node@' in content
        
        # Si usa Python, verificar instalación de dependencias
        if has_python:
            if 'pip install' not in content and 'requirements' not in content:
                self.add_warning(workflow_name, "Python configurado pero sin instalación de dependencias",
                               "Agregar: pip install -r requirements.txt")
        
        # Si usa Node, verificar instalación de dependencias
        if has_node:
            if 'npm install' not in content and 'npm ci' not in content:
                self.add_warning(workflow_name, "Node.js configurado pero sin instalación de dependencias",
                               "Agregar: npm ci o npm install")
        
        # Verificar versiones fijas
        if 'actions/checkout@' in content:
            if '@v4' not in content and '@v3' not in content:
                self.add_warning(workflow_name, "Usar versión específica de actions/checkout",
                               "Recomendado: actions/checkout@v4")
    
    def check_paths(self, workflow_name: str, content: str):
        """Verifica rutas de archivos y directorios"""
        # Buscar rutas comunes que podrían no existir
        common_paths = [
            'backend/',
            'frontend/',
            'scripts/',
            'data/output/',
            'requirements.txt',
            'requirements-oracle.txt',
            'requirements-scraper.txt',
        ]
        
        for path_str in common_paths:
            if path_str in content:
                path = Path(path_str)
                if not path.exists():
                    self.add_warning(workflow_name, f"Ruta potencialmente inexistente: {path_str}",
                                   f"Verificar que existe: {path_str}")
    
    def check_best_practices(self, workflow_name: str, data: dict, content: str):
        """Verifica mejores prácticas"""
        # Verificar timeout
        for job_name, job_data in data.get('jobs', {}).items():
            if isinstance(job_data, dict):
                if 'timeout-minutes' not in job_data:
                    self.add_info(workflow_name, f"Job '{job_name}' sin timeout definido",
                                "Agregar: timeout-minutes: 30 (recomendado)")
        
        # Verificar continue-on-error para jobs opcionales
        if 'continue-on-error' not in content and 'fail-fast' not in content:
            if any(keyword in content.lower() for keyword in ['alert', 'notification', 'telegram']):
                self.add_info(workflow_name, "Considerar agregar continue-on-error: true",
                            "Para notificaciones que no deberían fallar el workflow completo")
        
        # Verificar cache
        if 'setup-python' in content and 'cache:' not in content:
            self.add_info(workflow_name, "Agregar cache para Python",
                        "Agregar: cache: 'pip' en actions/setup-python")
        
        if 'setup-node' in content and 'cache:' not in content:
            self.add_info(workflow_name, "Agregar cache para Node.js",
                        "Agregar: cache: 'npm' en actions/setup-node")
    
    def add_error(self, workflow: str, issue: str, recommendation: str):
        """Agrega un error crítico"""
        self.results['issues'].append({
            'workflow': workflow,
            'severity': 'ERROR',
            'issue': issue,
            'recommendation': recommendation
        })
        self.results['workflows_with_errors'] += 1
        print(f"  ❌ ERROR: {issue}")
        print(f"     → {recommendation}")
    
    def add_warning(self, workflow: str, issue: str, recommendation: str):
        """Agrega una advertencia"""
        self.results['issues'].append({
            'workflow': workflow,
            'severity': 'WARNING',
            'issue': issue,
            'recommendation': recommendation
        })
        self.results['workflows_with_warnings'] += 1
        print(f"  ⚠️  WARNING: {issue}")
        print(f"     → {recommendation}")
    
    def add_info(self, workflow: str, issue: str, recommendation: str):
        """Agrega información/mejora sugerida"""
        self.results['issues'].append({
            'workflow': workflow,
            'severity': 'INFO',
            'issue': issue,
            'recommendation': recommendation
        })
        print(f"  💡 INFO: {issue}")
        print(f"     → {recommendation}")
    
    def print_summary(self):
        """Imprime resumen del análisis"""
        print("\n" + "="*80)
        print("📊 RESUMEN DEL ANÁLISIS")
        print("="*80 + "\n")
        
        print(f"Total de workflows: {self.results['total_workflows']}")
        
        errors = len([i for i in self.results['issues'] if i['severity'] == 'ERROR'])
        warnings = len([i for i in self.results['issues'] if i['severity'] == 'WARNING'])
        infos = len([i for i in self.results['issues'] if i['severity'] == 'INFO'])
        
        print(f"  ❌ Errores críticos: {errors}")
        print(f"  ⚠️  Advertencias: {warnings}")
        print(f"  💡 Sugerencias: {infos}")
        
        if errors == 0 and warnings == 0:
            print("\n✅ ¡Todos los workflows están correctamente configurados!")
        elif errors == 0:
            print("\n⚠️  Hay algunas advertencias, pero no errores críticos")
        else:
            print("\n❌ Se encontraron errores críticos que deben corregirse")
        
        # Recomendaciones generales
        print("\n" + "="*80)
        print("📋 RECOMENDACIONES GENERALES")
        print("="*80 + "\n")
        
        print("1. 🔐 Verificar que todos los secretos estén configurados en GitHub:")
        print("   Settings → Secrets and variables → Actions")
        print("\n2. 📦 Asegurar que existan todos los archivos de dependencias:")
        print("   requirements.txt, requirements-oracle.txt, package.json, etc.")
        print("\n3. 🧪 Probar workflows localmente antes de push:")
        print("   python simulate_github_workflow.py")
        print("\n4. 📊 Monitorear ejecuciones en GitHub:")
        print("   Actions tab → Ver logs y errores")
        print("\n5. 🔄 Usar workflow_dispatch para pruebas manuales:")
        print("   Todos los workflows deben tener workflow_dispatch habilitado")
    
    def save_report(self):
        """Guarda el reporte en archivo JSON"""
        output_dir = Path("data/output")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        report_file = output_dir / f"workflow_debug_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)
        
        print(f"\n📄 Reporte guardado en: {report_file}")


def main():
    """Función principal"""
    debugger = WorkflowDebugger()
    debugger.analyze_all_workflows()


if __name__ == "__main__":
    main()
