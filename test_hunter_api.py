"""
Test script for Hunter.io API
Prueba las funcionalidades principales de Hunter.io
"""
import os
import requests
import json
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Configuración
HUNTER_API_KEY = os.getenv('HUNTER_API_KEY')
BASE_URL = 'https://api.hunter.io/v2'

def print_section(title):
    """Imprime un título de sección"""
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60)

def test_domain_search(domain):
    """
    1. Domain Search - Busca todos los emails de un dominio
    Encuentra emails asociados a una empresa
    """
    print_section(f"🔍 DOMAIN SEARCH: {domain}")
    
    if not HUNTER_API_KEY:
        print("❌ ERROR: HUNTER_API_KEY no configurada")
        print("   Obtén tu API key en: https://hunter.io/api")
        return None
    
    try:
        url = f"{BASE_URL}/domain-search"
        params = {
            'domain': domain,
            'api_key': HUNTER_API_KEY,
            'limit': 10  # Limitar resultados para testing
        }
        
        response = requests.get(url, params=params)
        response.raise_for_status()
        
        data = response.json()
        
        if data.get('data'):
            result = data['data']
            print(f"✅ Dominio: {result.get('domain')}")
            print(f"   Empresa: {result.get('organization', 'N/A')}")
            print(f"   Emails encontrados: {result.get('emails', 0)}")
            print(f"   Patrón de email: {result.get('pattern', 'N/A')}")
            
            # Mostrar algunos emails encontrados
            emails = result.get('emails', [])
            if emails:
                print(f"\n   📧 Primeros emails encontrados:")
                for i, email_data in enumerate(emails[:5], 1):
                    print(f"      {i}. {email_data.get('value')} ({email_data.get('type', 'N/A')})")
                    print(f"         Confianza: {email_data.get('confidence', 0)}%")
                    if email_data.get('first_name'):
                        print(f"         Nombre: {email_data.get('first_name')} {email_data.get('last_name')}")
                    if email_data.get('position'):
                        print(f"         Cargo: {email_data.get('position')}")
            
            return result
        else:
            print(f"⚠️  No se encontraron emails para {domain}")
            return None
            
    except requests.exceptions.HTTPError as e:
        print(f"❌ ERROR HTTP: {e}")
        if response.status_code == 401:
            print("   → API key inválida o no configurada")
        elif response.status_code == 429:
            print("   → Límite de requests excedido")
        return None
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        return None

def test_email_finder(domain, first_name, last_name):
    """
    2. Email Finder - Encuentra el email de una persona específica
    """
    print_section(f"🎯 EMAIL FINDER: {first_name} {last_name} @ {domain}")
    
    if not HUNTER_API_KEY:
        print("❌ ERROR: HUNTER_API_KEY no configurada")
        return None
    
    try:
        url = f"{BASE_URL}/email-finder"
        params = {
            'domain': domain,
            'first_name': first_name,
            'last_name': last_name,
            'api_key': HUNTER_API_KEY
        }
        
        response = requests.get(url, params=params)
        response.raise_for_status()
        
        data = response.json()
        
        if data.get('data'):
            result = data['data']
            print(f"✅ Email encontrado: {result.get('email')}")
            print(f"   Confianza: {result.get('score')}%")
            print(f"   Fuentes: {len(result.get('sources', []))}")
            
            return result
        else:
            print(f"⚠️  No se pudo encontrar el email")
            return None
            
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        return None

def test_email_verifier(email):
    """
    3. Email Verifier - Verifica si un email existe
    """
    print_section(f"✔️  EMAIL VERIFIER: {email}")
    
    if not HUNTER_API_KEY:
        print("❌ ERROR: HUNTER_API_KEY no configurada")
        return None
    
    try:
        url = f"{BASE_URL}/email-verifier"
        params = {
            'email': email,
            'api_key': HUNTER_API_KEY
        }
        
        response = requests.get(url, params=params)
        response.raise_for_status()
        
        data = response.json()
        
        if data.get('data'):
            result = data['data']
            status = result.get('status')
            score = result.get('score')
            
            # Interpretar el resultado
            status_emoji = {
                'valid': '✅',
                'invalid': '❌',
                'accept_all': '⚠️',
                'unknown': '❓'
            }
            
            print(f"{status_emoji.get(status, '❓')} Estado: {status}")
            print(f"   Score: {score}/100")
            print(f"   Resultado: {result.get('result', 'N/A')}")
            print(f"   SMTP Check: {result.get('smtp_check', 'N/A')}")
            print(f"   MX Records: {'✓' if result.get('mx_records') else '✗'}")
            
            return result
        else:
            print(f"⚠️  No se pudo verificar el email")
            return None
            
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        return None

def test_email_count(domain):
    """
    4. Email Count - Cuenta cuántos emails tiene un dominio
    """
    print_section(f"📊 EMAIL COUNT: {domain}")
    
    if not HUNTER_API_KEY:
        print("❌ ERROR: HUNTER_API_KEY no configurada")
        return None
    
    try:
        url = f"{BASE_URL}/email-count"
        params = {
            'domain': domain,
            'api_key': HUNTER_API_KEY
        }
        
        response = requests.get(url, params=params)
        response.raise_for_status()
        
        data = response.json()
        
        if data.get('data'):
            result = data['data']
            print(f"✅ Total de emails: {result.get('total', 0)}")
            print(f"   Personal: {result.get('personal_emails', 0)}")
            print(f"   Genéricos: {result.get('generic_emails', 0)}")
            
            return result
        else:
            print(f"⚠️  No se pudo obtener el conteo")
            return None
            
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        return None

def check_api_usage():
    """
    5. Account Information - Revisa el uso de tu API
    """
    print_section("📈 USO DE API")
    
    if not HUNTER_API_KEY:
        print("❌ ERROR: HUNTER_API_KEY no configurada")
        return None
    
    try:
        url = f"{BASE_URL}/account"
        params = {
            'api_key': HUNTER_API_KEY
        }
        
        response = requests.get(url, params=params)
        response.raise_for_status()
        
        data = response.json()
        
        if data.get('data'):
            result = data['data']
            print(f"✅ Email: {result.get('email')}")
            print(f"   Plan: {result.get('plan_name', 'Free')}")
            print(f"   Requests usados: {result.get('requests', {}).get('used', 0)}/{result.get('requests', {}).get('available', 0)}")
            print(f"   Requests restantes: {result.get('requests', {}).get('available', 0) - result.get('requests', {}).get('used', 0)}")
            
            # Fecha de reset
            reset_date = result.get('reset_date')
            if reset_date:
                print(f"   Reset: {reset_date}")
            
            return result
        else:
            print(f"⚠️  No se pudo obtener información de la cuenta")
            return None
            
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        return None

def main():
    """Función principal para ejecutar todas las pruebas"""
    print("\n")
    print("╔════════════════════════════════════════════════════════════╗")
    print("║          HUNTER.IO API TEST SUITE                          ║")
    print("╚════════════════════════════════════════════════════════════╝")
    
    # Verificar configuración
    if not HUNTER_API_KEY:
        print("\n❌ ERROR: No se encontró HUNTER_API_KEY en .env")
        print("\n📋 PASOS PARA CONFIGURAR:")
        print("   1. Ve a https://hunter.io/users/sign_up")
        print("   2. Regístrate (plan gratuito: 50 requests/mes)")
        print("   3. Ve a API Dashboard: https://hunter.io/api")
        print("   4. Copia tu API key")
        print("   5. Agrégala a tu archivo .env:")
        print("      HUNTER_API_KEY=tu_api_key_aqui")
        return
    
    # Información de la cuenta
    check_api_usage()
    
    # PRUEBA 1: Domain Search - Buscar emails de una empresa
    print("\n\n🧪 PRUEBA 1: Domain Search")
    test_domain_search('stripe.com')  # Ejemplo con empresa conocida
    
    # PRUEBA 2: Email Finder - Encontrar email específico
    print("\n\n🧪 PRUEBA 2: Email Finder")
    test_email_finder('stripe.com', 'Patrick', 'Collison')
    
    # PRUEBA 3: Email Verifier - Verificar email
    print("\n\n🧪 PRUEBA 3: Email Verifier")
    test_email_verifier('patrick@stripe.com')
    
    # PRUEBA 4: Email Count
    print("\n\n🧪 PRUEBA 4: Email Count")
    test_email_count('stripe.com')
    
    # Resumen final
    print("\n")
    print("╔════════════════════════════════════════════════════════════╗")
    print("║                    PRUEBAS COMPLETADAS                     ║")
    print("╚════════════════════════════════════════════════════════════╝")
    print("\n📚 DOCUMENTACIÓN:")
    print("   → https://hunter.io/api-documentation/v2")
    print("\n💡 TIP: Cambia los dominios y nombres en el código para")
    print("   probar con tus propios casos de uso")
    
    # Verificar uso final
    print("\n")
    check_api_usage()

if __name__ == "__main__":
    main()
