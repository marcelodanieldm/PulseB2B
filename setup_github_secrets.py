"""
GitHub Secrets Configuration Helper
Ayuda a configurar los secrets requeridos para GitHub Actions
"""

import os
from pathlib import Path


REQUIRED_SECRETS = {
    'CRITICAL': {
        'TELEGRAM_BOT_TOKEN': 'Token del bot de Telegram',
        'TELEGRAM_CHAT_ID': 'ID del chat de Telegram',
        'SUPABASE_URL': 'URL de tu proyecto Supabase',
        'SUPABASE_SERVICE_KEY': 'Service key de Supabase'
    },
    'IMPORTANT': {
        'GOOGLE_CSE_API_KEY': 'API key de Google Custom Search',
        'GOOGLE_CSE_ID': 'ID del Custom Search Engine',
        'SENDGRID_API_KEY': 'API key de SendGrid',
        'EMAIL_USERNAME': 'Usuario de email',
        'EMAIL_PASSWORD': 'Contraseña de email'
    },
    'OPTIONAL': {
        'CLEARBIT_API_KEY': 'API key de Clearbit',
        'SLACK_WEBHOOK_URL': 'Webhook de Slack',
        'DISCORD_WEBHOOK_URL': 'Webhook de Discord',
        'TELEGRAM_ALERT_CHAT_ID': 'Chat ID para alertas',
        'SUPABASE_ANON_KEY': 'Anon key de Supabase',
        'SUPABASE_KEY': 'Key alternativa de Supabase',
        'SUPABASE_SERVICE_ROLE_KEY': 'Service role key',
        'WEBHOOK_URL': 'Webhook URL genérico',
        'ALERT_EMAIL': 'Email para alertas',
        'FROM_EMAIL': 'Email remitente',
        'BASE_URL': 'URL base de la aplicación',
        'FRONTEND_URL': 'URL del frontend',
        'GOOGLE_SEARCH_API_KEY': 'API key alternativa de Google'
    }
}


def print_header(text):
    """Imprime un encabezado"""
    print("\n" + "="*70)
    print(f"  {text}")
    print("="*70)


def check_current_secrets():
    """Verifica qué secrets están configurados"""
    print_header("🔍 Checking Current Environment Variables")
    
    all_secrets = []
    for category in REQUIRED_SECRETS.values():
        all_secrets.extend(category.keys())
    
    configured = []
    missing = []
    
    for secret in all_secrets:
        if os.environ.get(secret):
            configured.append(secret)
        else:
            missing.append(secret)
    
    print(f"\n✅ Configured: {len(configured)}/{len(all_secrets)}")
    print(f"❌ Missing: {len(missing)}/{len(all_secrets)}")
    
    if configured:
        print("\n✅ Currently configured:")
        for secret in configured:
            print(f"   • {secret}")
    
    return configured, missing


def generate_powershell_script():
    """Genera un script de PowerShell para configurar secrets"""
    print_header("📝 Generating PowerShell Setup Script")
    
    script_content = """# GitHub Actions Secrets Configuration
# Execute este script en PowerShell para configurar variables de entorno localmente

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "   GitHub Actions Secrets Setup" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# CRITICAL SECRETS (Requeridos)
Write-Host "CRITICAL SECRETS (Required):" -ForegroundColor Red
"""
    
    for category, secrets in REQUIRED_SECRETS.items():
        script_content += f'\n# {category} SECRETS\n'
        script_content += f'Write-Host "{category} SECRETS:" -ForegroundColor Yellow\n'
        
        for secret, description in secrets.items():
            script_content += f'\n# {description}\n'
            script_content += f'$env:{secret} = "YOUR_{secret}_HERE"\n'
            script_content += f'Write-Host "  Set: {secret}" -ForegroundColor Green\n'
    
    script_content += """
Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "   Configuration Complete!" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "💡 Verify configuration:" -ForegroundColor Yellow
Write-Host "   python check_workflow_status.py" -ForegroundColor White
Write-Host ""
Write-Host "📚 Next steps:" -ForegroundColor Yellow
Write-Host "   1. Replace 'YOUR_*_HERE' with actual values" -ForegroundColor White
Write-Host "   2. Run this script: .\\configure_secrets.ps1" -ForegroundColor White
Write-Host "   3. Configure same secrets in GitHub:" -ForegroundColor White
Write-Host "      Settings > Secrets and variables > Actions" -ForegroundColor White
"""
    
    script_path = Path("configure_secrets.ps1")
    with open(script_path, 'w', encoding='utf-8') as f:
        f.write(script_content)
    
    print(f"\n✅ Script created: {script_path}")
    print("\n📝 To use:")
    print(f"   1. Edit {script_path} and replace placeholders")
    print(f"   2. Run: .\\{script_path}")
    print("\n⚠️  This sets variables for current session only")
    print("   For permanent setup, configure in GitHub Settings")


def generate_github_instructions():
    """Genera instrucciones para configurar en GitHub"""
    print_header("📋 GitHub Secrets Configuration Instructions")
    
    instructions = """
GITHUB SECRETS SETUP GUIDE
========================

1. Go to your GitHub repository
2. Click on "Settings" tab
3. Navigate to "Secrets and variables" > "Actions"
4. Click "New repository secret"

CRITICAL SECRETS (Configure these first):
"""
    
    for secret, description in REQUIRED_SECRETS['CRITICAL'].items():
        instructions += f"\n  • {secret}\n    Description: {description}\n    Click 'New repository secret' > Enter name and value > Add secret\n"
    
    instructions += "\nIMPORTANT SECRETS:"
    for secret, description in REQUIRED_SECRETS['IMPORTANT'].items():
        instructions += f"\n  • {secret}\n    Description: {description}\n"
    
    instructions += "\n\nOPTIONAL SECRETS (Configure as needed):"
    for secret, description in REQUIRED_SECRETS['OPTIONAL'].items():
        instructions += f"\n  • {secret} - {description}\n"
    
    instructions += """
TESTING:
--------
After configuring secrets in GitHub:
1. Go to "Actions" tab
2. Select a workflow (e.g., "Critical Flows Test & Telegram Report")
3. Click "Run workflow"
4. Select branch (usually "main")
5. Click "Run workflow" button
6. Monitor execution in real-time
7. Check logs for any errors

TROUBLESHOOTING:
---------------
If a workflow fails:
• Verify secret names match exactly (case-sensitive)
• Check secret values are correct (no extra spaces)
• Ensure all required secrets for that workflow are set
• Review workflow logs for specific error messages
• Test locally with: python simulate_github_workflow.py
"""
    
    guide_path = Path("data/output/github_secrets_guide.txt")
    guide_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(guide_path, 'w', encoding='utf-8') as f:
        f.write(instructions)
    
    print(f"\n✅ Guide saved: {guide_path}")
    print("\n📖 To view:")
    print(f"   type {guide_path}")


def print_secrets_summary():
    """Imprime un resumen de secrets"""
    print_header("📊 Secrets Summary")
    
    total = sum(len(secrets) for secrets in REQUIRED_SECRETS.values())
    
    print(f"\nTotal secrets required: {total}")
    print(f"\n  🔴 Critical: {len(REQUIRED_SECRETS['CRITICAL'])}")
    for secret in REQUIRED_SECRETS['CRITICAL']:
        print(f"     • {secret}")
    
    print(f"\n  🟡 Important: {len(REQUIRED_SECRETS['IMPORTANT'])}")
    for secret in REQUIRED_SECRETS['IMPORTANT']:
        print(f"     • {secret}")
    
    print(f"\n  ⚪ Optional: {len(REQUIRED_SECRETS['OPTIONAL'])}")
    print(f"     ({len(REQUIRED_SECRETS['OPTIONAL'])} secrets for advanced features)")


def generate_env_template():
    """Genera un template .env"""
    print_header("📄 Generating .env Template")
    
    env_content = "# GitHub Actions Secrets - Local Development Template\n"
    env_content += "# Copy this to .env and fill in your values\n"
    env_content += "# DO NOT commit .env to git!\n\n"
    
    for category, secrets in REQUIRED_SECRETS.items():
        env_content += f"\n# {category} SECRETS\n"
        for secret, description in secrets.items():
            env_content += f"# {description}\n"
            env_content += f"{secret}=\n"
    
    template_path = Path(".env.template")
    with open(template_path, 'w', encoding='utf-8') as f:
        f.write(env_content)
    
    print(f"\n✅ Template created: {template_path}")
    print("\n📝 Usage:")
    print(f"   1. Copy: copy {template_path} .env")
    print("   2. Edit .env and add your values")
    print("   3. Load with: python-dotenv or similar")
    print("\n⚠️  Add .env to .gitignore!")


def main():
    print("""
╔═══════════════════════════════════════════════════════════════════╗
║           GitHub Secrets Configuration Helper                     ║
║           Setup secrets for GitHub Actions workflows              ║
╚═══════════════════════════════════════════════════════════════════╝
    """)
    
    # Check current state
    configured, missing = check_current_secrets()
    
    # Print summary
    print_secrets_summary()
    
    # Generate helper files
    generate_powershell_script()
    generate_env_template()
    generate_github_instructions()
    
    print("\n" + "="*70)
    print("✅ Configuration helpers generated!")
    print("="*70)
    
    print("\n📚 Files created:")
    print("   • configure_secrets.ps1 - PowerShell setup script")
    print("   • .env.template - Environment variables template")
    print("   • data/output/github_secrets_guide.txt - GitHub setup guide")
    
    print("\n🚀 Next steps:")
    print("   1. Configure secrets locally:")
    print("      - Edit configure_secrets.ps1")
    print("      - Run: .\\configure_secrets.ps1")
    print("   2. Configure secrets in GitHub:")
    print("      - Read: data/output/github_secrets_guide.txt")
    print("      - Go to: Settings > Secrets and variables > Actions")
    print("   3. Test workflows:")
    print("      - Run: python test_github_actions.py")
    print("      - Go to GitHub Actions tab")


if __name__ == "__main__":
    main()
