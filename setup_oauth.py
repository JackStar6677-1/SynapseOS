#!/usr/bin/env python3
"""
Configuración OAuth OpenAI para SynapseOS
Ayuda a configurar ChatGPT Codex 5.4 con OAuth
"""

import os
import json
from pathlib import Path

def check_current_config():
    """Verifica la configuración actual"""
    print("🔍 Verificando configuración OAuth actual...")
    print("=" * 50)

    env_file = Path(".env")
    if not env_file.exists():
        print("❌ No existe archivo .env")
        return False

    with open(env_file, 'r') as f:
        content = f.read()

    client_id = None
    client_secret = None

    for line in content.split('\n'):
        if line.startswith('OPENAI_CLIENT_ID='):
            client_id = line.split('=', 1)[1].strip()
        elif line.startswith('OPENAI_CLIENT_SECRET='):
            client_secret = line.split('=', 1)[1].strip()

    print(f"Client ID: {'✅ SET' if client_id and client_id != 'openai_client' else '❌ NOT_SET'}")
    print(f"Client Secret: {'✅ SET' if client_secret and client_secret != 'openai_secret' else '❌ NOT_SET'}")

    if client_id == 'openai_client' or client_secret == 'openai_secret':
        print("\n⚠️  Los valores están como placeholder")
        return False

    return bool(client_id and client_secret)

def setup_oauth_credentials():
    """Configura las credenciales OAuth de OpenAI"""
    print("\n🔧 Configuración OAuth OpenAI")
    print("=" * 40)

    print("Para usar ChatGPT Codex 5.4 con OAuth, necesitas:")
    print("1. Una aplicación OAuth registrada en OpenAI")
    print("2. Client ID y Client Secret de esa aplicación")
    print()

    print("📋 PASOS PARA OBTENER CREDENCIALES OAUTH:")
    print("1. Ve a: https://platform.openai.com/account/api-keys")
    print("2. Crea una nueva aplicación OAuth (si no tienes una)")
    print("3. Obtén el Client ID y Client Secret")
    print()

    # Verificar si ya están configurados
    if check_current_config():
        print("✅ OAuth ya está configurado correctamente")
        return True

    print("🔑 CONFIGURACIÓN MANUAL:")
    print("Edita el archivo .env y reemplaza los valores:")

    env_content = """# OpenAI OAuth Configuration
OPENAI_CLIENT_ID=tu_client_id_real_de_openai
OPENAI_CLIENT_SECRET=tu_client_secret_real_de_openai
OAUTH_REDIRECT_URI=http://localhost:8000/auth/callback

# Google Cloud (suspendido temporalmente)
GEMINI_API_KEY=AIzaSyBIl_5CEHmopNt0qCpqzRVYdADdthgIikA
"""

    print("\nContenido recomendado para .env:")
    print("-" * 40)
    print(env_content)

    # Preguntar si quiere actualizar automáticamente
    update_auto = input("\n¿Quieres que actualice el .env automáticamente? (s/n): ").strip().lower()

    if update_auto == 's':
        with open('.env', 'w') as f:
            f.write(env_content)
        print("✅ Archivo .env actualizado")
        print("⚠️  RECUERDA: Reemplaza 'tu_client_id_real_de_openai' y 'tu_client_secret_real_de_openai' con tus valores reales")

    return False

def test_oauth_setup():
    """Prueba la configuración OAuth"""
    print("\n🧪 Probando configuración OAuth...")
    print("=" * 40)

    try:
        # Importar y probar inicialización
        from core.oauth import OAuth2Config, OAuth2Client

        client_id = os.getenv("OPENAI_CLIENT_ID")
        client_secret = os.getenv("OPENAI_CLIENT_SECRET")

        if not client_id or not client_secret or client_id == 'openai_client' or client_secret == 'openai_secret':
            print("❌ Credenciales OAuth no configuradas correctamente")
            return False

        # Crear configuración
        config = OAuth2Config(
            client_id=client_id,
            client_secret=client_secret,
            redirect_uri=os.getenv("OAUTH_REDIRECT_URI", "http://localhost:8000/auth/callback")
        )

        print("✅ Configuración OAuth válida")
        print(f"Client ID: {client_id[:10]}...")
        print(f"Redirect URI: {config.redirect_uri}")

        return True

    except Exception as e:
        print(f"❌ Error probando OAuth: {e}")
        return False

def show_usage_instructions():
    """Muestra instrucciones de uso"""
    print("\n📖 INSTRUCCIONES DE USO")
    print("=" * 30)

    instructions = {
        "configuracion": [
            "1. Obtén Client ID y Client Secret de OpenAI",
            "2. Actualiza el archivo .env con los valores reales",
            "3. Reinicia SynapseOS"
        ],
        "primer_uso": [
            "1. Ejecuta: python main.py",
            "2. Ve a: http://localhost:8000/auth/openai",
            "3. Autoriza la aplicación en OpenAI",
            "4. SynapseOS tendrá acceso a ChatGPT Codex 5.4"
        ],
        "verificacion": [
            "Los tokens OAuth se guardan automáticamente",
            "La próxima vez no necesitarás re-autorizar",
            "El sistema detectará automáticamente OpenAI como disponible"
        ]
    }

    for section, steps in instructions.items():
        print(f"\n🔹 {section.upper()}:")
        for step in steps:
            print(f"   {step}")

def main():
    """Función principal"""
    print("🧠 SYNAPSEOS - CONFIGURACIÓN OAUTH OPENAI")
    print("=" * 50)
    print("Configuración para ChatGPT Codex 5.4 con OAuth")
    print("(No usa API keys directas, usa tu cuenta de OpenAI)")
    print()

    # Verificar configuración actual
    current_ok = check_current_config()

    if not current_ok:
        # Configurar OAuth
        setup_oauth_credentials()

        # Probar configuración
        test_oauth_setup()

    # Mostrar instrucciones
    show_usage_instructions()

    print("\n" + "=" * 50)
    print("🎯 RESUMEN:")
    print("- SynapseOS usa OAuth, no API keys directas")
    print("- Necesitas Client ID y Client Secret de OpenAI")
    print("- Una vez configurado, tendrás acceso a ChatGPT Codex 5.4")
    print("- El sistema es más seguro que usar API keys")

if __name__ == "__main__":
    main()