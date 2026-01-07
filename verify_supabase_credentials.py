"""
Script de Verificación de Credenciales Supabase
Prueba la conexión a Supabase con tus credenciales
"""

import os
import sys

def check_credentials():
    """Verifica que las credenciales de Supabase estén configuradas"""
    
    print("=" * 60)
    print("🔍 VERIFICACIÓN DE CREDENCIALES SUPABASE")
    print("=" * 60)
    print()
    
    # Check environment variables
    url = os.environ.get("SUPABASE_URL")
    service_key = os.environ.get("SUPABASE_SERVICE_KEY")
    service_role_key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
    
    issues = []
    
    # Check SUPABASE_URL
    if not url:
        print("❌ SUPABASE_URL no está configurada")
        issues.append("SUPABASE_URL faltante")
    else:
        print(f"✅ SUPABASE_URL encontrada: {url[:30]}...")
        
        # Validate URL format
        if not url.startswith("https://"):
            print("   ⚠️  Advertencia: La URL debería empezar con https://")
            issues.append("URL inválida")
        if not "supabase.co" in url:
            print("   ⚠️  Advertencia: La URL debería contener 'supabase.co'")
            issues.append("URL sospechosa")
    
    # Check SUPABASE_SERVICE_KEY
    key = service_role_key or service_key
    
    if not key:
        print("❌ Ninguna clave de servicio encontrada")
        print("   Falta: SUPABASE_SERVICE_KEY o SUPABASE_SERVICE_ROLE_KEY")
        issues.append("Service key faltante")
    else:
        key_name = "SUPABASE_SERVICE_ROLE_KEY" if service_role_key else "SUPABASE_SERVICE_KEY"
        print(f"✅ {key_name} encontrada: {key[:20]}...")
        
        # Validate key format
        if not key.startswith("eyJ"):
            print("   ⚠️  Advertencia: La key debería empezar con 'eyJ'")
            issues.append("Key inválida")
        if len(key) < 100:
            print("   ⚠️  Advertencia: La key parece muy corta")
            issues.append("Key sospechosa")
    
    print()
    print("=" * 60)
    
    # Test connection if credentials are present
    if url and key:
        print("🔗 Probando conexión a Supabase...")
        try:
            from supabase import create_client
            
            supabase = create_client(url, key)
            
            # Try a simple query to verify connection
            result = supabase.table('lead_scores').select('id').limit(1).execute()
            
            print("✅ CONEXIÓN EXITOSA")
            print(f"   Respuesta de Supabase recibida correctamente")
            print()
            print("🎉 Todo está configurado correctamente!")
            print()
            return True
            
        except Exception as e:
            print(f"❌ ERROR DE CONEXIÓN: {str(e)}")
            print()
            print("Posibles causas:")
            print("  1. Las credenciales son incorrectas")
            print("  2. El proyecto de Supabase está pausado")
            print("  3. La tabla 'lead_scores' no existe")
            print("  4. La clave no tiene permisos suficientes")
            issues.append("Conexión fallida")
    else:
        print("⏭️  Omitiendo prueba de conexión (faltan credenciales)")
    
    print()
    print("=" * 60)
    
    if issues:
        print("❌ PROBLEMAS ENCONTRADOS:")
        for i, issue in enumerate(issues, 1):
            print(f"  {i}. {issue}")
        print()
        print("📖 Lee SUPABASE_SECRETS_SETUP.md para instrucciones detalladas")
        print()
        return False
    
    return True


def print_github_instructions():
    """Imprime instrucciones para configurar en GitHub Actions"""
    print()
    print("=" * 60)
    print("📝 CONFIGURACIÓN EN GITHUB ACTIONS")
    print("=" * 60)
    print()
    print("Para usar estas credenciales en GitHub Actions:")
    print()
    print("1. Ve a tu repositorio en GitHub")
    print("2. Settings → Secrets and variables → Actions")
    print("3. Agrega estos secrets:")
    print()
    print("   Name: SUPABASE_URL")
    print(f"   Value: {os.environ.get('SUPABASE_URL', '<tu-url-aquí>')}")
    print()
    print("   Name: SUPABASE_SERVICE_KEY")
    print(f"   Value: {os.environ.get('SUPABASE_SERVICE_KEY', '<tu-key-aquí>')[:20]}...")
    print()
    print("=" * 60)
    print()


if __name__ == "__main__":
    print()
    
    # Run verification
    success = check_credentials()
    
    # Print GitHub instructions
    print_github_instructions()
    
    # Exit with appropriate code
    if not success:
        print("❌ Verificación fallida. Configura tus credenciales e intenta de nuevo.")
        print()
        sys.exit(1)
    else:
        print("✅ Verificación exitosa. Tus credenciales están correctas.")
        print()
        sys.exit(0)
