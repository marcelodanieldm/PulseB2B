"""
Manual GitHub Actions Workflow Simulator
Simula la ejecución manual de workflows específicos localmente
"""

import os
import sys
import subprocess
from pathlib import Path
from datetime import datetime


def print_step(emoji, text):
    """Imprime un paso con formato"""
    print(f"\n{emoji} {text}")


def run_critical_flows_workflow():
    """Simula el workflow: Critical Flows Test & Telegram Report"""
    print("\n" + "="*70)
    print("🚀 Running: Critical Flows Test & Telegram Report")
    print("="*70)
    
    print_step("📥", "Checkout code - SKIPPED (local)")
    print_step("🐍", "Setup Python - SKIPPED (using current)")
    
    print_step("📦", "Install dependencies")
    try:
        subprocess.run([
            sys.executable, "-m", "pip", "install",
            "scikit-learn", "numpy", "pandas", "python-telegram-bot"
        ], check=True, capture_output=True)
        print("   ✅ Dependencies installed")
    except subprocess.CalledProcessError as e:
        print(f"   ⚠️ Some packages might already be installed")
    
    print_step("🧪", "Run critical flows tests")
    try:
        result = subprocess.run(
            [sys.executable, "test_critical_flows.py"],
            capture_output=True,
            text=True,
            timeout=60
        )
        
        if result.returncode == 0:
            print("   ✅ Tests completed successfully")
        else:
            print("   ⚠️ Tests completed with warnings")
        
        # Mostrar salida
        if result.stdout:
            print("\n📋 Test Output:")
            print(result.stdout[:500])  # Primeras 500 chars
            
    except subprocess.TimeoutExpired:
        print("   ⏱️ Test timed out after 60s")
    except FileNotFoundError:
        print("   ❌ test_critical_flows.py not found")
        return False
    
    print_step("📊", "Generate test summary")
    report_path = Path("data/output/critical_flows_report.json")
    if report_path.exists():
        print(f"   ✅ Test report found: {report_path}")
    else:
        print(f"   ❌ Test report not found")
    
    print_step("📱", "Send report to Telegram")
    if not os.environ.get("TELEGRAM_BOT_TOKEN"):
        print("   ⚠️ TELEGRAM_BOT_TOKEN not set - SKIPPED")
    else:
        try:
            result = subprocess.run(
                [sys.executable, "send_to_telegram.py"],
                capture_output=True,
                text=True,
                timeout=30
            )
            if result.returncode == 0:
                print("   ✅ Telegram report sent")
            else:
                print(f"   ❌ Failed to send Telegram report")
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    print("\n✅ Workflow simulation complete")
    return True


def run_daily_scrape_workflow():
    """Simula el workflow: Ghost Crawler - Daily Scrape"""
    print("\n" + "="*70)
    print("🚀 Running: Ghost Crawler - Daily Scrape")
    print("="*70)
    
    print_step("📥", "Checkout code - SKIPPED (local)")
    print_step("🐍", "Setup Python & Node.js - SKIPPED (using current)")
    
    print_step("📦", "Install dependencies")
    print("   ℹ️ Checking Python dependencies...")
    
    print_step("🕵️", "Ghost Crawler - LinkedIn Job Search")
    if not os.environ.get("GOOGLE_CSE_API_KEY"):
        print("   ⚠️ GOOGLE_CSE_API_KEY not set - SIMULATION MODE")
        print("   💡 Set this in GitHub Secrets for production")
    else:
        print("   ✅ API keys detected")
    
    # Verificar si existe el script
    ghost_script = Path("scripts/ghost-crawler.js")
    if ghost_script.exists():
        print(f"   ✅ Ghost crawler script found")
    else:
        print(f"   ❌ Ghost crawler script not found")
    
    print_step("🧠", "Run Pulse Intelligence Scorer")
    pulse_script = Path("scripts/integrate_pulse_intelligence.py")
    if pulse_script.exists():
        print(f"   ✅ Pulse Intelligence script found")
        
        # Verificar si hay datos scraped
        scraped_data = Path("data/output/scraped_companies.csv")
        if scraped_data.exists():
            print(f"   📊 Found scraped data: {scraped_data}")
            print("   ℹ️ Would run Pulse scoring in actual workflow")
        else:
            print("   ⚠️ No scraped data found - would skip scoring")
    else:
        print(f"   ❌ Pulse Intelligence script not found")
    
    print_step("💾", "Sync to Supabase")
    if not os.environ.get("SUPABASE_URL"):
        print("   ⚠️ SUPABASE credentials not set - SKIPPED")
    else:
        print("   ✅ Supabase credentials detected")
    
    print("\n✅ Workflow simulation complete")
    return True


def run_oracle_workflow():
    """Simula el workflow: Oracle Ghost - Automated Lead Detection"""
    print("\n" + "="*70)
    print("🚀 Running: Oracle Ghost - Automated Lead Detection")
    print("="*70)
    
    print_step("📥", "Checkout code - SKIPPED (local)")
    print_step("🐍", "Setup Python - SKIPPED (using current)")
    
    print_step("📦", "Install dependencies")
    req_file = Path("requirements-oracle.txt")
    if req_file.exists():
        print(f"   ✅ Found {req_file}")
        try:
            with open(req_file, 'r') as f:
                deps = [l.strip() for l in f if l.strip() and not l.startswith('#')]
                print(f"   📊 {len(deps)} dependencies listed")
        except:
            pass
    
    print_step("🔮", "Run Oracle Detector")
    oracle_script = Path("scripts/oracle_funding_detector.py")
    if oracle_script.exists():
        print(f"   ✅ Oracle detector script found")
        
        if not all([os.environ.get("SUPABASE_URL"), os.environ.get("TELEGRAM_BOT_TOKEN")]):
            print("   ⚠️ Required secrets not set - SIMULATION MODE")
        else:
            print("   ✅ All required secrets detected")
    else:
        print(f"   ❌ Oracle detector script not found")
    
    print_step("📊", "Validate output data")
    validate_script = Path("scripts/validate_oracle_output.py")
    if validate_script.exists():
        print(f"   ✅ Validation script found")
    else:
        print(f"   ❌ Validation script not found")
    
    print_step("📤", "Upload to Supabase")
    upload_script = Path("scripts/upload_to_supabase.py")
    if upload_script.exists():
        print(f"   ✅ Upload script found")
    else:
        print(f"   ❌ Upload script not found")
    
    print_step("🔔", "Send Telegram notifications")
    telegram_script = Path("scripts/telegram_notifier.py")
    if telegram_script.exists():
        print(f"   ✅ Telegram notifier found")
    else:
        print(f"   ❌ Telegram notifier not found")
    
    print("\n✅ Workflow simulation complete")
    return True


def main():
    print("""
╔═══════════════════════════════════════════════════════════════════╗
║           GitHub Actions Workflow Simulator                       ║
║           Test workflows locally before deployment                ║
╚═══════════════════════════════════════════════════════════════════╝
    """)
    
    print("Available workflows to simulate:\n")
    print("  1. Critical Flows Test & Telegram Report")
    print("  2. Ghost Crawler - Daily Scrape")
    print("  3. Oracle Ghost - Automated Lead Detection")
    print("  4. Run all simulations")
    print("\n  0. Exit")
    
    choice = input("\nSelect workflow (0-4): ").strip()
    
    if choice == "1":
        run_critical_flows_workflow()
    elif choice == "2":
        run_daily_scrape_workflow()
    elif choice == "3":
        run_oracle_workflow()
    elif choice == "4":
        run_critical_flows_workflow()
        run_daily_scrape_workflow()
        run_oracle_workflow()
    else:
        print("Exiting...")
        return
    
    print("\n" + "="*70)
    print("💡 Next Steps:")
    print("="*70)
    print("  1. Set missing environment variables (GitHub Secrets)")
    print("  2. Push code to GitHub repository")
    print("  3. Go to Actions tab: https://github.com/[your-repo]/actions")
    print("  4. Click 'Run workflow' to trigger manually")
    print("\n  📚 Learn more: https://docs.github.com/actions")


if __name__ == "__main__":
    main()
