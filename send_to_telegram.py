#!/usr/bin/env python3
"""
Enviar Informe de Tests a Telegram
===================================
Script para enviar automáticamente el informe de validación a Telegram.

Requisitos:
    pip install python-telegram-bot

Configuración:
    1. Crear bot con @BotFather
    2. Obtener token del bot
    3. Obtener tu chat_id (usa @userinfobot)
    4. Configurar variables de entorno o editar abajo

Uso:
    python send_to_telegram.py
    python send_to_telegram.py --detailed  # Envía informe detallado
"""

import sys
import os
from pathlib import Path
import asyncio

# Configuración (editar con tus valores)
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', 'TU_BOT_TOKEN_AQUI')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID', 'TU_CHAT_ID_AQUI')


async def send_telegram_message(message: str, parse_mode: str = 'HTML'):
    """Send message to Telegram"""
    try:
        # Try to import telegram
        try:
            from telegram import Bot
        except ImportError:
            print("❌ python-telegram-bot no instalado")
            print("\nInstalar con:")
            print("   pip install python-telegram-bot")
            return False
        
        # Check configuration
        if TELEGRAM_BOT_TOKEN == 'TU_BOT_TOKEN_AQUI':
            print("❌ ERROR: TELEGRAM_BOT_TOKEN no configurado")
            print("\n📝 Configuración necesaria:")
            print("   1. Crear bot con @BotFather en Telegram")
            print("   2. Copiar el token del bot")
            print("   3. Editar este script o configurar:")
            print("      export TELEGRAM_BOT_TOKEN='tu-token'")
            print("      export TELEGRAM_CHAT_ID='tu-chat-id'")
            return False
        
        if TELEGRAM_CHAT_ID == 'TU_CHAT_ID_AQUI':
            print("❌ ERROR: TELEGRAM_CHAT_ID no configurado")
            print("\n📝 Para obtener tu chat_id:")
            print("   1. Envía /start a @userinfobot en Telegram")
            print("   2. El bot te responderá con tu chat_id")
            print("   3. Edita este script o configura la variable de entorno")
            return False
        
        # Initialize bot
        bot = Bot(token=TELEGRAM_BOT_TOKEN)
        
        # Split message if too long (Telegram limit: 4096 chars)
        max_length = 4096
        if len(message) <= max_length:
            await bot.send_message(
                chat_id=TELEGRAM_CHAT_ID,
                text=message,
                parse_mode=parse_mode
            )
            print(f"✅ Mensaje enviado a Telegram (chat_id: {TELEGRAM_CHAT_ID})")
        else:
            # Split into chunks
            chunks = [message[i:i+max_length] for i in range(0, len(message), max_length)]
            for i, chunk in enumerate(chunks, 1):
                await bot.send_message(
                    chat_id=TELEGRAM_CHAT_ID,
                    text=chunk,
                    parse_mode=parse_mode
                )
                print(f"✅ Parte {i}/{len(chunks)} enviada")
                await asyncio.sleep(1)  # Avoid rate limiting
        
        return True
    
    except Exception as e:
        print(f"❌ Error enviando mensaje: {e}")
        return False


def main():
    """Main function"""
    print("="*60)
    print("📱 ENVIAR INFORME A TELEGRAM")
    print("="*60)
    print()
    
    # Check for custom format flag
    format_type = None
    for arg in sys.argv[1:]:
        if arg.startswith('--format='):
            format_type = arg.split('=')[1]
        elif arg == '--format' and sys.argv.index(arg) + 1 < len(sys.argv):
            format_type = sys.argv[sys.argv.index(arg) + 1]
    
    # Check which report to send
    detailed = '--detailed' in sys.argv or '-d' in sys.argv
    
    if format_type:
        report_file = Path(f'data/output/telegram_{format_type}_format.txt')
        print(f"📋 Enviando formato personalizado: {format_type}")
    elif detailed:
        report_file = Path('data/output/telegram_mensaje_completo.txt')
        print("📋 Enviando informe detallado...")
    else:
        report_file = Path('data/output/telegram_report.txt')
        print("📋 Enviando informe simple...")
    
    # Check if file exists
    if not report_file.exists():
        print(f"❌ Archivo no encontrado: {report_file}")
        print("\n💡 Ejecutar primero:")
        print("   python test_critical_flows.py")
        if format_type:
            print("   python customize_telegram_messages.py")
        return 1
    
    # Read message
    with open(report_file, 'r', encoding='utf-8') as f:
        message = f.read()
    
    print(f"📄 Archivo: {report_file}")
    print(f"📏 Tamaño: {len(message)} caracteres")
    print()
    
    # Send to Telegram
    success = asyncio.run(send_telegram_message(message))
    
    if success:
        print()
        print("="*60)
        print("✅ INFORME ENVIADO EXITOSAMENTE")
        print("="*60)
        return 0
    else:
        print()
        print("="*60)
        print("❌ ERROR AL ENVIAR INFORME")
        print("="*60)
        return 1


if __name__ == '__main__':
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n⚠️  Cancelado por el usuario")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
