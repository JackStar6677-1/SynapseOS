#!/usr/bin/env python3
"""
SynapseOS Recovery Script - Google Cloud Suspension
Helps recover from Google Cloud API suspension
"""

import asyncio
import logging
import os
from pathlib import Path
import json

# Add the project root to Python path
import sys
sys.path.insert(0, str(Path(__file__).parent))

from main import SynapseOS

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def diagnose_google_cloud_issue():
    """Diagnose the Google Cloud suspension issue"""

    print("🔍 SynapseOS - Diagnóstico de Problema Google Cloud")
    print("=" * 60)

    # Check current configuration
    print("\n📋 Configuración Actual:")
    gemini_key = os.getenv('GEMINI_API_KEY', 'NOT_SET')
    print(f"   Gemini API Key: {'***' + gemini_key[-4:] if gemini_key != 'NOT_SET' else 'NOT_SET'}")

    openai_id = os.getenv('OPENAI_CLIENT_ID', 'NOT_SET')
    openai_secret = os.getenv('OPENAI_CLIENT_SECRET', 'NOT_SET')
    print(f"   OpenAI Client ID: {'***' + openai_id[-4:] if openai_id != 'NOT_SET' else 'NOT_SET'}")
    print(f"   OpenAI Client Secret: {'***' + openai_secret[-4:] if openai_secret != 'NOT_SET' else 'NOT_SET'}")

    # Test system initialization
    print("\n🚀 Probando Inicialización del Sistema:")
    try:
        system = SynapseOS()
        await system.initialize()

        print("   ✅ Sistema inicializado correctamente")
        print(f"   📊 Device ID: {system.identity.device_id[:16]}...")
        print(f"   🤖 Current Provider: {system.ai_manager.get_current_provider_name() or 'None'}")
        print(f"   📋 Available Providers: {system.ai_manager.list_available_providers()}")

    except Exception as e:
        print(f"   ❌ Error inicializando sistema: {e}")
        return

    # Test provider availability
    print("\n🔍 Probando Disponibilidad de Proveedores:")
    for provider_name in system.ai_manager.list_available_providers():
        print(f"   Testing {provider_name}...")
        try:
            provider = system.ai_manager.get_provider(provider_name)
            available = await system.ai_manager._test_provider_availability(provider)
            status = "✅ Available" if available else "❌ Not Available"
            print(f"      {provider_name}: {status}")
        except Exception as e:
            print(f"      {provider_name}: ❌ Error - {e}")

    # Show recovery options
    print("\n🛠️ Opciones de Recuperación:")
    print("   1. 🚨 APPEAL A GOOGLE (RECOMENDADO)")
    print("      - Ve a: https://support.google.com/cloud/answer/6281720")
    print("      - Explica que eres desarrollador legítimo")
    print("      - Menciona que usas la API para proyectos personales")
    print("      - Tiempo estimado: 2-7 días hábiles")
    print()
    print("   2. 🔄 USAR SOLO OPENAI CODEX")
    print("      - Configura OPENAI_CLIENT_ID y OPENAI_CLIENT_SECRET")
    print("      - El sistema funcionará con OpenAI únicamente")
    print()
    print("   3. 🆕 CREAR NUEVA CUENTA GOOGLE")
    print("      - Crea nueva cuenta Gmail")
    print("      - Activa Google Cloud con nueva cuenta")
    print("      - Genera nueva API key")
    print()
    print("   4. ⏳ ESPERAR Y REINTENTAR")
    print("      - Algunos usuarios reportan recuperación automática")
    print("      - Revisa el estado en 24-48 horas")

    # Test refresh functionality
    print("\n🔄 Probando Funcionalidad de Refresh:")
    try:
        print("   Refrescando proveedores...")
        await system.refresh_ai_providers()
        print("   ✅ Refresh completado")
    except Exception as e:
        print(f"   ❌ Error en refresh: {e}")

    print("\n💡 RECOMENDACIÓN INMEDIATA:")
    print("   1. Detén TODOS los requests a Google Cloud APIs")
    print("   2. Envía el appeal a Google inmediatamente")
    print("   3. Configura OpenAI como alternativa temporal")
    print("   4. Monitorea el estado de tu cuenta Cloud")

    print("\n📞 CONTACTO DE SOPORTE:")
    print("   - Google Cloud Support: https://cloud.google.com/support")
    print("   - Terms of Service Appeals: https://support.google.com/cloud/answer/6281720")

    print("\n🎯 PRÓXIMOS PASOS:")
    print("   Una vez resuelto el appeal, ejecuta:")
    print("   python recovery_script.py --test-gemini")

if __name__ == "__main__":
    asyncio.run(diagnose_google_cloud_issue())