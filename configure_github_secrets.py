#!/usr/bin/env python3
"""
GitHub Secrets Configuration Helper
====================================
Ayuda a configurar los secretos de GitHub para los workflows de Telegram.

Uso:
    python configure_github_secrets.py
"""

import os
import json
import subprocess
from pathlib import Path

def print_header():
    print("\n╔═══════════════════════════════════════════════════════════════════╗")
    print("║                                                                   ║")
    print("║        🔐 GitHub Secrets Configuration Helper 🔐                 ║")
    print("║                                                                   ║")
    print("║     Configura secretos para workflows de Telegram                ║")
    print("║                                                                   ║")
    print("╚═══════════════════════════════════════════════════════════════════╝\n")


def check_gh_cli():
    """Check if GitHub CLI is installed"""
    try:
        result = subprocess.run(['gh', '--version'], capture_output=True, text=True)
        return result.returncode == 0
    except FileNotFoundError:
        return False


def load_local_env():
    """Load secrets from local .env file"""
    env_path = Path('.env')
    secrets = {}
    
    if env_path.exists():
        with open(env_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    secrets[key.strip()] = value.strip()
    
    return secrets


def set_github_secret(name, value):
    """Set a GitHub secret using gh CLI"""
    try:
        # Use gh secret set command
        process = subprocess.Popen(
            ['gh', 'secret', 'set', name],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        stdout, stderr = process.communicate(input=value)
        
        if process.returncode == 0:
            print(f"  ✅ {name} configurado")
            return True
        else:
            print(f"  ❌ Error configurando {name}: {stderr}")
            return False
            
    except Exception as e:
        print(f"  ❌ Error: {str(e)}")
        return False


def manual_instructions(secrets):
    """Show manual configuration instructions"""
    print("\n" + "="*70)
    print("📋 INSTRUCCIONES MANUALES")
    print("="*70 + "\n")
    
    print("Ve a tu repositorio en GitHub:")
    print("  Settings → Secrets and variables → Actions → New repository secret\n")
    
    print("Configura los siguientes secretos:\n")
    
    for name, value in secrets.items():
        print(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print(f"Nombre: {name}")
        print(f"Valor:  {value}")
        print()


def main():
    print_header()
    
    # Check if .env exists
    if not Path('.env').exists():
        print("❌ No se encontró archivo .env")
        print("\nPor favor, ejecuta primero:")
        print("  > setup_telegram_reports.bat\n")
        return
    
    # Load local secrets
    print("📥 Cargando configuración local...\n")
    secrets = load_local_env()
    
    if not secrets:
        print("❌ No se encontraron secretos en .env\n")
        return
    
    # Required secrets for workflows
    required_secrets = {
        'TELEGRAM_BOT_TOKEN': secrets.get('TELEGRAM_BOT_TOKEN', ''),
        'TELEGRAM_CHAT_ID': secrets.get('TELEGRAM_CHAT_ID', ''),
        'SUPABASE_URL': secrets.get('SUPABASE_URL', ''),
        'SUPABASE_SERVICE_KEY': secrets.get('SUPABASE_KEY', ''),
    }
    
    # Filter out empty values
    required_secrets = {k: v for k, v in required_secrets.items() if v}
    
    print("🔍 Secretos encontrados:")
    for name in required_secrets.keys():
        masked_value = required_secrets[name][:10] + "..." if len(required_secrets[name]) > 10 else "***"
        print(f"  • {name}: {masked_value}")
    print()
    
    # Check if GitHub CLI is installed
    if not check_gh_cli():
        print("⚠️  GitHub CLI no está instalado\n")
        print("Opciones:")
        print("  1. Instalar GitHub CLI: https://cli.github.com/")
        print("  2. Configurar manualmente en GitHub\n")
        
        choice = input("¿Mostrar instrucciones manuales? (S/N): ").strip().lower()
        if choice == 's':
            manual_instructions(required_secrets)
        return
    
    # Check if authenticated with GitHub
    try:
        result = subprocess.run(['gh', 'auth', 'status'], capture_output=True, text=True)
        if result.returncode != 0:
            print("❌ No estás autenticado en GitHub CLI\n")
            print("Ejecuta primero:")
            print("  > gh auth login\n")
            return
    except:
        print("❌ Error verificando autenticación de GitHub CLI\n")
        return
    
    print("✅ GitHub CLI detectado y autenticado\n")
    
    # Ask for confirmation
    print("="*70)
    print("¿Deseas configurar estos secretos en GitHub?")
    print("  - Se configurarán en el repositorio actual")
    print("  - Los workflows se activarán automáticamente")
    print("="*70 + "\n")
    
    choice = input("Continuar? (S/N): ").strip().lower()
    
    if choice != 's':
        print("\n❌ Operación cancelada\n")
        manual_instructions(required_secrets)
        return
    
    # Configure secrets
    print("\n🔐 Configurando secretos en GitHub...\n")
    
    success_count = 0
    for name, value in required_secrets.items():
        if set_github_secret(name, value):
            success_count += 1
    
    print("\n" + "="*70)
    print(f"✅ Configuración completa: {success_count}/{len(required_secrets)} secretos")
    print("="*70 + "\n")
    
    if success_count == len(required_secrets):
        print("🎉 ¡Todos los secretos configurados exitosamente!\n")
        print("Próximos pasos:")
        print("  1. Haz push de los workflows a GitHub")
        print("  2. Ve a Actions en tu repositorio")
        print("  3. Ejecuta un workflow manualmente para probar")
        print("  4. ¡Los workflows se ejecutarán automáticamente!\n")
    else:
        print("⚠️  Algunos secretos no se configuraron correctamente")
        print("Por favor, configúralos manualmente en GitHub\n")
        manual_instructions(required_secrets)


if __name__ == '__main__':
    main()
