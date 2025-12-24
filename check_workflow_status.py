"""
GitHub Actions Status Checker
Verifica el estado y configuración de workflows después del deployment
"""

import os
import json
from pathlib import Path
from datetime import datetime


def check_workflow_files():
    """Verifica todos los archivos de workflow"""
    print("="*70)
    print("📁 Checking Workflow Files")
    print("="*70)
    
    workflows_dir = Path(".github/workflows")
    
    if not workflows_dir.exists():
        print("❌ .github/workflows directory not found!")
        return []
    
    workflows = list(workflows_dir.glob("*.yml")) + list(workflows_dir.glob("*.yaml"))
    
    print(f"\n✅ Found {len(workflows)} workflow files\n")
    
    workflow_info = []
    
    for workflow in workflows:
        print(f"📄 {workflow.name}")
        
        try:
            with open(workflow, 'r', encoding='utf-8') as f:
                content = f.read()
                
                # Extraer información básica
                info = {
                    'file': workflow.name,
                    'name': None,
                    'schedule': None,
                    'manual': False,
                    'on_push': False
                }
                
                for line in content.split('\n'):
                    if line.strip().startswith('name:'):
                        info['name'] = line.split('name:')[1].strip().strip('"\'')
                    elif 'workflow_dispatch' in line:
                        info['manual'] = True
                    elif 'cron:' in line:
                        cron = line.split('cron:')[1].strip().strip('"\'')
                        info['schedule'] = cron
                    elif line.strip().startswith('push:'):
                        info['on_push'] = True
                
                workflow_info.append(info)
                
                # Mostrar info
                if info['name']:
                    print(f"   📋 Name: {info['name']}")
                if info['schedule']:
                    print(f"   ⏰ Schedule: {info['schedule']}")
                if info['manual']:
                    print(f"   🎮 Manual trigger: ✅ Enabled")
                if info['on_push']:
                    print(f"   🔄 On push: ✅ Enabled")
                
                print()
                
        except Exception as e:
            print(f"   ⚠️ Error reading file: {e}\n")
    
    return workflow_info


def analyze_schedules(workflow_info):
    """Analiza los schedules configurados"""
    print("\n" + "="*70)
    print("⏰ Schedule Analysis")
    print("="*70)
    
    scheduled = [w for w in workflow_info if w['schedule']]
    manual = [w for w in workflow_info if w['manual']]
    on_push = [w for w in workflow_info if w['on_push']]
    
    print(f"\n📊 Summary:")
    print(f"   Total workflows: {len(workflow_info)}")
    print(f"   Scheduled: {len(scheduled)}")
    print(f"   Manual trigger: {len(manual)}")
    print(f"   On push: {len(on_push)}")
    
    if scheduled:
        print(f"\n⏰ Scheduled Workflows:")
        for w in scheduled:
            print(f"   • {w['name'] or w['file']}")
            print(f"     Cron: {w['schedule']}")
            print()


def check_required_secrets():
    """Lista los secrets requeridos por los workflows"""
    print("\n" + "="*70)
    print("🔑 Required Secrets Analysis")
    print("="*70)
    
    workflows_dir = Path(".github/workflows")
    all_secrets = set()
    
    for workflow in workflows_dir.glob("*.yml"):
        try:
            with open(workflow, 'r', encoding='utf-8') as f:
                content = f.read()
                
                # Buscar secrets.${{ secrets.NAME }}
                import re
                secrets = re.findall(r'\$\{\{\s*secrets\.(\w+)\s*\}\}', content)
                all_secrets.update(secrets)
                
        except:
            pass
    
    print(f"\n📋 Unique secrets required: {len(all_secrets)}\n")
    
    for secret in sorted(all_secrets):
        is_set = os.environ.get(secret) is not None
        status = "✅ SET (local)" if is_set else "❓ Unknown (check GitHub)"
        print(f"   {status}: {secret}")
    
    print("\n💡 To set in GitHub:")
    print("   Settings > Secrets and variables > Actions > New repository secret")


def generate_deployment_checklist():
    """Genera un checklist para deployment"""
    print("\n" + "="*70)
    print("📋 Deployment Checklist")
    print("="*70)
    
    checklist = [
        "All workflow YAML files are syntactically valid",
        "All Python scripts have valid syntax",
        "All required files referenced in workflows exist",
        "Requirements files are complete",
        "Package.json is valid",
        "All secrets are documented",
        "Cron schedules are verified (in UTC)",
        "Manual triggers are enabled for testing",
        "Repository is pushed to GitHub",
        "Secrets are configured in GitHub Settings",
        "First workflow run is monitored",
        "Logs are reviewed for errors"
    ]
    
    print("\n✅ Before deploying, verify:\n")
    for i, item in enumerate(checklist, 1):
        print(f"   [ ] {i}. {item}")
    
    print("\n🚀 After deployment:")
    print("   1. Go to: https://github.com/[your-repo]/actions")
    print("   2. Select a workflow")
    print("   3. Click 'Run workflow' for manual test")
    print("   4. Monitor execution and logs")
    print("   5. Verify Telegram notifications (if applicable)")


def check_workflow_outputs():
    """Verifica si hay outputs de workflows anteriores"""
    print("\n" + "="*70)
    print("📊 Previous Workflow Outputs")
    print("="*70)
    
    output_dirs = [
        "data/output",
        "data/output/oracle",
        "data/output/pulse_reports"
    ]
    
    found_outputs = False
    
    for dir_path in output_dirs:
        path = Path(dir_path)
        if path.exists():
            files = list(path.glob("*"))
            if files:
                found_outputs = True
                print(f"\n📁 {dir_path}:")
                for file in sorted(files)[:5]:  # Mostrar primeros 5
                    size = file.stat().st_size if file.is_file() else 0
                    modified = datetime.fromtimestamp(file.stat().st_mtime).strftime('%Y-%m-%d %H:%M')
                    print(f"   • {file.name}")
                    if file.is_file():
                        print(f"     Size: {size:,} bytes | Modified: {modified}")
                
                if len(files) > 5:
                    print(f"   ... and {len(files) - 5} more files")
    
    if not found_outputs:
        print("\n📭 No previous workflow outputs found")
        print("   This is normal for first deployment")


def main():
    print("""
╔═══════════════════════════════════════════════════════════════════╗
║          GitHub Actions Status & Deployment Checker               ║
║          Verify workflows before and after deployment             ║
╚═══════════════════════════════════════════════════════════════════╝
    """)
    
    # Check workflow files
    workflow_info = check_workflow_files()
    
    # Analyze schedules
    if workflow_info:
        analyze_schedules(workflow_info)
    
    # Check required secrets
    check_required_secrets()
    
    # Check previous outputs
    check_workflow_outputs()
    
    # Generate checklist
    generate_deployment_checklist()
    
    # Save report
    report_path = Path("data/output/workflow_status_report.txt")
    report_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write("GitHub Actions Status Report\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("="*70 + "\n\n")
        f.write(f"Total workflows: {len(workflow_info)}\n")
        f.write(f"Scheduled: {len([w for w in workflow_info if w['schedule']])}\n")
        f.write(f"Manual trigger: {len([w for w in workflow_info if w['manual']])}\n")
    
    print(f"\n💾 Report saved: {report_path}")
    
    print("\n" + "="*70)
    print("✅ Status check complete!")
    print("="*70)
    print("\n📚 Next: Read GITHUB_ACTIONS_TESTING.md for detailed guide")


if __name__ == "__main__":
    main()
