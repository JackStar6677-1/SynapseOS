#!/usr/bin/env python3
"""
Probar OAuth importado en SynapseOS
Verifica que ChatGPT Codex 5.4 esté disponible
"""

import asyncio
import os
import sys
from pathlib import Path

# Load .env file
from dotenv import load_dotenv
load_dotenv()

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

async def test_oauth_provider():
    """Prueba el proveedor OAuth de OpenAI"""
    print("🧪 Probando proveedor OAuth de OpenAI...")
    print("=" * 50)

    try:
        from core.ai_providers import AIProviderManager
        from core.memory import MemorySystem
        from core.oauth import OAuth2Config, OAuth2Client

        # Initialize memory system
        memory = MemorySystem()

        # Initialize OAuth client (like main.py does)
        oauth_config = None
        client_id = os.getenv("OPENAI_CLIENT_ID")
        client_secret = os.getenv("OPENAI_CLIENT_SECRET")

        if client_id and client_secret:
            oauth_config = OAuth2Config(
                client_id=client_id,
                client_secret=client_secret,
                redirect_uri=os.getenv("OAUTH_REDIRECT_URI", "http://localhost:8000/auth/callback")
            )
            oauth_client = OAuth2Client(oauth_config, memory)
        else:
            oauth_client = None
            print("❌ OAuth client not configured")

        # Initialize provider manager
        manager = AIProviderManager(memory)

        # Set OAuth client for AI providers (like main.py does)
        if oauth_client:
            manager.set_oauth_client(oauth_client)

        # Initialize providers (this should load the imported tokens)
        await manager.initialize_providers()
        
        # Check available providers
        available = await manager.get_available_providers()
        print(f"📊 Proveedores disponibles: {len(available)}")

        for provider in available:
            print(f"  ✅ {provider}")

        if "openai-codex" in available:
            print("\n🎉 ¡ChatGPT Codex 5.4 está disponible!")

            # Try to adopt the provider
            success = await manager.adopt_provider("openai-codex")
            if success:
                print("✅ Proveedor adoptado exitosamente")

                # Try a simple test generation
                print("\n🤖 Probando generación de texto...")
                test_prompt = "Hola, ¿puedes confirmar que eres ChatGPT Codex 5.4?"
                result = await manager.generate_text(test_prompt)

                if result:
                    print("✅ Generación exitosa:")
                    print(f"   Respuesta: {result[:100]}...")
                else:
                    print("❌ Falló la generación de texto")

            else:
                print("❌ No se pudo adoptar el proveedor")
        else:
            print("\n❌ ChatGPT Codex 5.4 no está disponible")
            print("Posibles causas:")
            print("  - Tokens expirados")
            print("  - Client Secret faltante")
            print("  - Problemas de configuración")

        return "openai-codex" in available

    except Exception as e:
        print(f"❌ Error probando OAuth: {e}")
        import traceback
        traceback.print_exc()
        return False

def check_configuration():
    """Verifica la configuración"""
    print("🔧 Verificando configuración...")
    print("=" * 30)

    # Check .env
    env_file = Path(".env")
    if env_file.exists():
        with open(env_file, 'r') as f:
            content = f.read()

        client_id_ok = "OPENAI_CLIENT_ID=app_EMoamEEZ73f0CkXaXp7hrann" in content
        client_secret_ok = "OPENAI_CLIENT_SECRET=" in content and "tu_client_secret" not in content

        print(f"Client ID: {'✅' if client_id_ok else '❌'}")
        print(f"Client Secret: {'✅' if client_secret_ok else '❌'}")
    else:
        print("❌ Archivo .env no encontrado")

    # Check imported tokens
    token_file = Path("data") / "memory" / "oauth_openai.json"
    if token_file.exists():
        print("✅ Tokens importados encontrados")
    else:
        print("❌ Tokens importados no encontrados")

def main():
    """Función principal"""
    print("🧠 SYNAPSEOS - PRUEBA OAUTH IMPORTADO")
    print("=" * 45)

    # Verificar configuración
    check_configuration()
    print()

    # Probar OAuth
    success = asyncio.run(test_oauth_provider())

    print("\n" + "=" * 45)
    if success:
        print("🎯 RESULTADO: ¡OAuth funcionando correctamente!")
        print("ChatGPT Codex 5.4 está listo para usar en SynapseOS")
    else:
        print("🎯 RESULTADO: OAuth necesita ajustes")
        print("Revisa la configuración y vuelve a intentar")

if __name__ == "__main__":
    main()