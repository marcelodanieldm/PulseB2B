#!/usr/bin/env python3
"""
Test Final de Workflows - Verificación Post-Debugging
Verifica que todos los workflows estén correctamente configurados
"""

import yaml
from pathlib import Path
import json

def test_all_workflows():
    """Prueba todos los workflows para YAML válido"""
    print("="*70)
    print("🧪 TEST FINAL DE WORKFLOWS")
    print("="*70 + "\n")
    
    workflows_dir = Path(".github/workflows")
    workflows = list(workflows_dir.glob("*.yml")) + list(workflows_dir.glob("*.yaml"))
    
    results = {
        'total': len(workflows),
        'valid': 0,
        'invalid': 0,
        'errors': []
    }
    
    for workflow_file in workflows:
        try:
            with open(workflow_file, 'r', encoding='utf-8') as f:
                content = f.read()
                data = yaml.safe_load(content)
                
                # Verificaciones básicas
                has_name = 'name' in data
                has_on = 'on' in data
                has_jobs = 'jobs' in data
                
                if has_name and has_on and has_jobs:
                    print(f"✅ {workflow_file.name} - VÁLIDO")
                    results['valid'] += 1
                else:
                    print(f"⚠️  {workflow_file.name} - INCOMPLETO")
                    results['invalid'] += 1
                    results['errors'].append({
                        'file': workflow_file.name,
                        'issue': 'Falta name, on, o jobs'
                    })
                    
        except yaml.YAMLError as e:
            print(f"❌ {workflow_file.name} - ERROR YAML: {str(e)[:100]}")
            results['invalid'] += 1
            results['errors'].append({
                'file': workflow_file.name,
                'issue': f'YAML Error: {str(e)[:100]}'
            })
        except Exception as e:
            print(f"❌ {workflow_file.name} - ERROR: {str(e)[:100]}")
            results['invalid'] += 1
            results['errors'].append({
                'file': workflow_file.name,
                'issue': f'Error: {str(e)[:100]}'
            })
    
    # Resumen
    print("\n" + "="*70)
    print("📊 RESUMEN")
    print("="*70)
    print(f"Total workflows: {results['total']}")
    print(f"✅ Válidos: {results['valid']}")
    print(f"❌ Con errores: {results['invalid']}")
    
    if results['invalid'] == 0:
        print("\n🎉 ¡TODOS LOS WORKFLOWS ESTÁN VÁLIDOS!")
        return True
    else:
        print("\n⚠️  Hay workflows con problemas:")
        for error in results['errors']:
            print(f"  - {error['file']}: {error['issue']}")
        return False

if __name__ == '__main__':
    success = test_all_workflows()
    exit(0 if success else 1)
