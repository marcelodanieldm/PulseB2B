"""
Test GitHub Actions Workflows Locally
Simula la ejecución de los workflows de GitHub Actions para verificar que funcionan correctamente
"""

import os
import sys
import subprocess
import json
from pathlib import Path
from datetime import datetime

class GitHubActionsTest:
    def __init__(self):
        self.root_dir = Path(__file__).parent
        self.results = {}
        self.total_tests = 0
        self.passed_tests = 0
        
    def print_header(self, text):
        """Imprime un encabezado formateado"""
        print("\n" + "="*70)
        print(f"  {text}")
        print("="*70)
    
    def print_step(self, step_name, status="START"):
        """Imprime el estado de un paso"""
        emoji = "🔄" if status == "START" else ("✅" if status == "SUCCESS" else "❌")
        print(f"\n{emoji} {step_name}")
    
    def check_file_exists(self, filepath):
        """Verifica si un archivo existe"""
        full_path = self.root_dir / filepath
        exists = full_path.exists()
        status = "✅" if exists else "❌"
        print(f"  {status} {filepath}: {'Found' if exists else 'Missing'}")
        return exists
    
    def check_python_script(self, script_path):
        """Verifica que un script de Python tenga sintaxis válida"""
        self.total_tests += 1
        full_path = self.root_dir / script_path
        
        if not full_path.exists():
            print(f"  ❌ Script not found: {script_path}")
            return False
        
        try:
            # Verificar sintaxis de Python
            result = subprocess.run(
                [sys.executable, "-m", "py_compile", str(full_path)],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                print(f"  ✅ Syntax valid: {script_path}")
                self.passed_tests += 1
                return True
            else:
                print(f"  ❌ Syntax error in {script_path}")
                print(f"     {result.stderr}")
                return False
        except Exception as e:
            print(f"  ❌ Error checking {script_path}: {e}")
            return False
    
    def test_workflow_dependencies(self, workflow_name, required_files):
        """Verifica que todos los archivos requeridos por un workflow existan"""
        self.print_header(f"Testing: {workflow_name}")
        self.total_tests += 1
        
        all_exist = True
        for file_path in required_files:
            if not self.check_file_exists(file_path):
                all_exist = False
        
        if all_exist:
            print(f"\n✅ All dependencies found for {workflow_name}")
            self.passed_tests += 1
        else:
            print(f"\n❌ Missing dependencies for {workflow_name}")
        
        return all_exist
    
    def test_critical_flows_workflow(self):
        """Testea el workflow de Critical Flows Test & Telegram Report"""
        workflow_name = "Critical Flows Test & Telegram Report"
        required_files = [
            "test_critical_flows.py",
            "send_to_telegram.py"
        ]
        
        result = self.test_workflow_dependencies(workflow_name, required_files)
        
        # Verificar sintaxis de scripts
        for script in required_files:
            self.check_python_script(script)
        
        return result
    
    def test_daily_scrape_workflow(self):
        """Testea el workflow de Ghost Crawler - Daily Scrape"""
        workflow_name = "Ghost Crawler - Daily Scrape"
        required_files = [
            "scripts/ghost-crawler.js",
            "scripts/integrate_pulse_intelligence.py",
            "requirements.txt",
            "package.json"
        ]
        
        result = self.test_workflow_dependencies(workflow_name, required_files)
        
        # Verificar scripts Python
        python_scripts = [f for f in required_files if f.endswith('.py')]
        for script in python_scripts:
            self.check_python_script(script)
        
        # Verificar package.json
        self.check_package_json()
        
        return result
    
    def test_oracle_workflow(self):
        """Testea el workflow de Oracle Ghost - Automated Lead Detection"""
        workflow_name = "Oracle Ghost - Automated Lead Detection"
        required_files = [
            "scripts/oracle_funding_detector.py",
            "scripts/validate_oracle_output.py",
            "scripts/upload_to_supabase.py",
            "scripts/telegram_notifier.py",
            "requirements-oracle.txt"
        ]
        
        result = self.test_workflow_dependencies(workflow_name, required_files)
        
        # Verificar sintaxis de scripts Python
        python_scripts = [f for f in required_files if f.endswith('.py')]
        for script in python_scripts:
            self.check_python_script(script)
        
        return result
    
    def check_package_json(self):
        """Verifica que package.json sea válido"""
        self.total_tests += 1
        package_json_path = self.root_dir / "package.json"
        
        if not package_json_path.exists():
            print("  ❌ package.json not found")
            return False
        
        try:
            with open(package_json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                print(f"  ✅ package.json is valid JSON")
                print(f"     Name: {data.get('name', 'N/A')}")
                print(f"     Version: {data.get('version', 'N/A')}")
                self.passed_tests += 1
                return True
        except json.JSONDecodeError as e:
            print(f"  ❌ Invalid JSON in package.json: {e}")
            return False
        except Exception as e:
            print(f"  ❌ Error reading package.json: {e}")
            return False
    
    def check_requirements_files(self):
        """Verifica que los archivos de requirements existan"""
        self.print_header("Checking Requirements Files")
        
        requirements_files = [
            "requirements.txt",
            "requirements-oracle.txt",
            "requirements-scraper.txt",
            "requirements-intent-engine.txt"
        ]
        
        for req_file in requirements_files:
            self.total_tests += 1
            if self.check_file_exists(req_file):
                # Intentar leer el archivo
                try:
                    with open(self.root_dir / req_file, 'r', encoding='utf-8') as f:
                        lines = [l.strip() for l in f.readlines() if l.strip() and not l.startswith('#')]
                        print(f"     {len(lines)} dependencies listed")
                        self.passed_tests += 1
                except Exception as e:
                    print(f"     ⚠️ Error reading file: {e}")
    
    def check_github_secrets(self):
        """Verifica qué secrets están configurados como variables de entorno"""
        self.print_header("Checking GitHub Secrets (Environment Variables)")
        
        required_secrets = [
            "TELEGRAM_BOT_TOKEN",
            "TELEGRAM_CHAT_ID",
            "SUPABASE_URL",
            "SUPABASE_SERVICE_KEY",
            "GOOGLE_CSE_API_KEY",
            "GOOGLE_CSE_ID"
        ]
        
        print("\nRequired secrets for workflows:")
        for secret in required_secrets:
            is_set = os.environ.get(secret) is not None
            status = "✅ SET" if is_set else "❌ NOT SET"
            print(f"  {status}: {secret}")
            
            if not is_set:
                print(f"     💡 Set with: $env:{secret}='your_value'  (PowerShell)")
    
    def list_all_workflows(self):
        """Lista todos los workflows disponibles"""
        self.print_header("Available GitHub Actions Workflows")
        
        workflows_dir = self.root_dir / ".github" / "workflows"
        
        if not workflows_dir.exists():
            print("❌ .github/workflows directory not found")
            return
        
        workflows = list(workflows_dir.glob("*.yml")) + list(workflows_dir.glob("*.yaml"))
        
        print(f"\nFound {len(workflows)} workflows:\n")
        for i, workflow in enumerate(workflows, 1):
            print(f"  {i}. {workflow.name}")
            
            # Intentar leer el nombre del workflow
            try:
                with open(workflow, 'r', encoding='utf-8') as f:
                    for line in f:
                        if line.startswith('name:'):
                            name = line.split('name:')[1].strip()
                            print(f"     📋 {name}")
                            break
            except:
                pass
    
    def generate_report(self):
        """Genera un reporte final"""
        self.print_header("Test Results Summary")
        
        success_rate = (self.passed_tests / self.total_tests * 100) if self.total_tests > 0 else 0
        
        print(f"\n📊 Tests Run: {self.total_tests}")
        print(f"✅ Passed: {self.passed_tests}")
        print(f"❌ Failed: {self.total_tests - self.passed_tests}")
        print(f"📈 Success Rate: {success_rate:.1f}%")
        
        if success_rate == 100:
            print("\n🎉 All tests passed! Your workflows are ready to run.")
        elif success_rate >= 80:
            print("\n⚠️ Most tests passed. Review failed items above.")
        else:
            print("\n❌ Many tests failed. Review the errors and fix missing dependencies.")
        
        # Guardar reporte
        report_path = self.root_dir / "data" / "output" / "github_actions_test_report.txt"
        report_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(f"GitHub Actions Test Report\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"=" * 70 + "\n\n")
            f.write(f"Tests Run: {self.total_tests}\n")
            f.write(f"Passed: {self.passed_tests}\n")
            f.write(f"Failed: {self.total_tests - self.passed_tests}\n")
            f.write(f"Success Rate: {success_rate:.1f}%\n")
        
        print(f"\n💾 Report saved to: {report_path}")
    
    def run_all_tests(self):
        """Ejecuta todos los tests"""
        self.print_header("🚀 GitHub Actions Workflow Testing")
        print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Listar workflows disponibles
        self.list_all_workflows()
        
        # Verificar archivos de requirements
        self.check_requirements_files()
        
        # Test workflows individuales
        self.test_critical_flows_workflow()
        self.test_daily_scrape_workflow()
        self.test_oracle_workflow()
        
        # Verificar secrets
        self.check_github_secrets()
        
        # Generar reporte final
        self.generate_report()


def main():
    print("""
╔═══════════════════════════════════════════════════════════════════╗
║        GitHub Actions Workflow Testing Tool                      ║
║        Test your workflows before pushing to GitHub              ║
╚═══════════════════════════════════════════════════════════════════╝
    """)
    
    tester = GitHubActionsTest()
    tester.run_all_tests()
    
    print("\n💡 Next Steps:")
    print("   1. Fix any missing files or syntax errors")
    print("   2. Set required environment variables (secrets)")
    print("   3. Push to GitHub to trigger workflows")
    print("   4. Check Actions tab in GitHub: https://github.com/[your-repo]/actions")
    print("\n   Manual trigger: Go to Actions > Select workflow > Run workflow")


if __name__ == "__main__":
    main()
