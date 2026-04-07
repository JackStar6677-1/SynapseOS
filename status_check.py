#!/usr/bin/env python3
"""
SynapseOS - Quick Status Check
Verifica el estado actual del sistema y proveedores disponibles
"""

import os
import asyncio
import sys
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

async def check_providers():
    """Verifica proveedores disponibles"""
    print("🔍 Verificando proveedores AI...")
    print("=" * 40)

    try:
        from core.ai_providers import AIProviderManager

        manager = AIProviderManager()

        # Initialize providers
        await manager.initialize_providers()

        # Get available providers
        available = await manager.get_available_providers()
        print(f"📊 Proveedores disponibles: {len(available)}")

        for provider in available:
            print(f"  ✅ {provider}")

        if not available:
            print("  ❌ Ningún proveedor disponible")
            print("\n💡 Para configurar OpenAI:")
            print("   1. Ve a: https://platform.openai.com/api-keys")
            print("   2. Crea una API Key")
            print("   3. Agrega OPENAI_API_KEY=tu_key al archivo .env")

        return available

    except Exception as e:
        print(f"❌ Error verificando proveedores: {e}")
        return []

def check_environment():
    """Verifica variables de entorno"""
    print("\n🔧 Variables de entorno:")
    print("=" * 30)

    env_vars = {
        'GEMINI_API_KEY': 'Google Gemini',
        'OPENAI_API_KEY': 'OpenAI',
        'OPENAI_CLIENT_ID': 'OpenAI OAuth'
    }

    for var, desc in env_vars.items():
        status = "✅ SET" if os.getenv(var) else "❌ NOT_SET"
        print(f"{desc}: {status}")

def show_recovery_status():
    """Muestra estado de recuperación"""
    print("\n📋 ESTADO DE RECUPERACIÓN")
    print("=" * 30)

    recovery_file = Path("recovery_plan.json")
    if recovery_file.exists():
        print("✅ Plan de recuperación creado")
    else:
        print("❌ Plan de recuperación no encontrado")

    env_file = Path(".env")
    if env_file.exists():
        print("✅ Archivo de configuración .env existe")
    else:
        print("❌ Archivo .env no encontrado")

async def main():
    """Función principal"""
    print("🩺 SYNAPSEOS - QUICK STATUS CHECK")
    print("=" * 40)

    # Verificar entorno
    check_environment()

    # Verificar proveedores
    available = await check_providers()

    # Mostrar estado de recuperación
    show_recovery_status()

    print("\n" + "=" * 40)
    if available:
        print("🎉 ¡Sistema operativo y funcionando!")
        print(f"Proveedores activos: {', '.join(available)}")
    else:
        print("⚠️  Sistema necesita configuración de proveedores")
        print("Ejecuta: python setup_alternatives.py")

    print("\n🚨 RECUERDA: Google Cloud suspendido - envía appeal!")

if __name__ == "__main__":
    asyncio.run(main())