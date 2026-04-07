#!/usr/bin/env python3
"""
SynapseOS - Recovery & Alternative Setup Script
Configura OpenAI como alternativa mientras resuelves el problema de Google Cloud
"""

import os
import json
import asyncio
from pathlib import Path

def setup_openai_credentials():
    """Configura las credenciales de OpenAI"""
    print("🔧 Configuración de OpenAI como alternativa")
    print("=" * 50)

    # Verificar si ya existe configuración
    env_file = Path(".env")
    if env_file.exists():
        print("✅ Archivo .env encontrado")
        with open(env_file, 'r') as f:
            content = f.read()
            if "OPENAI_CLIENT_ID" in content:
                print("⚠️  OpenAI ya parece estar configurado")
                return True

    print("\n📋 PASOS PARA CONFIGURAR OPENAI:")
    print("1. Ve a: https://platform.openai.com/api-keys")
    print("2. Crea una nueva API Key")
    print("3. Copia la API Key")

    api_key = input("\n🔑 Pega tu OpenAI API Key (o presiona Enter para saltar): ").strip()

    if not api_key:
        print("⏭️  Saltando configuración de OpenAI")
        return False

    # Crear/actualizar .env
    env_content = f"""
# OpenAI Configuration
OPENAI_API_KEY={api_key}
OPENAI_CLIENT_ID=openai_client
OPENAI_CLIENT_SECRET=openai_secret

# Google Cloud (suspendido temporalmente)
GEMINI_API_KEY={os.getenv('GEMINI_API_KEY', '')}
"""

    with open(env_file, 'w') as f:
        f.write(env_content.strip())

    print("✅ OpenAI configurado exitosamente")
    return True

async def test_alternative_providers():
    """Prueba los proveedores alternativos"""
    print("\n🧪 Probando proveedores alternativos...")
    print("=" * 40)

    try:
        # Importar el sistema de proveedores
        from core.ai_providers import AIProviderManager

        manager = AIProviderManager()
        await manager.initialize_providers()

        # Verificar proveedores disponibles
        available = await manager.get_available_providers()
        print(f"📊 Proveedores disponibles: {len(available)}")

        for provider in available:
            print(f"  ✅ {provider}")

        if available:
            print("\n🎉 ¡Sistema operativo con alternativas!")
            return True
        else:
            print("\n❌ No hay proveedores alternativos disponibles")
            return False

    except Exception as e:
        print(f"❌ Error probando proveedores: {e}")
        return False

def create_recovery_plan():
    """Crea un plan de recuperación"""
    print("\n📋 PLAN DE RECUPERACIÓN")
    print("=" * 30)

    plan = {
        "problema": "Cuenta Google Cloud suspendida por violación de ToS",
        "pasos_inmediatos": [
            "Detener TODOS los requests a Google Cloud APIs",
            "Enviar appeal formal a Google Cloud Support",
            "Configurar OpenAI como proveedor alternativo"
        ],
        "tiempo_espera": "2-7 días hábiles para respuesta del appeal",
        "alternativas": [
            "OpenAI Codex (ya configurado)",
            "Otros proveedores: Anthropic Claude, etc."
        ],
        "acciones_post_appeal": [
            "Verificar restablecimiento de cuenta Google Cloud",
            "Re-habilitar Gemini en SynapseOS",
            "Probar funcionamiento completo del sistema"
        ]
    }

    # Guardar plan como JSON
    with open("recovery_plan.json", 'w') as f:
        json.dump(plan, f, indent=2, ensure_ascii=False)

    print("✅ Plan de recuperación guardado en recovery_plan.json")

    # Mostrar plan
    print("\n🚨 ACCIONES INMEDIATAS:")
    for i, paso in enumerate(plan["pasos_inmediatos"], 1):
        print(f"{i}. {paso}")

    print(f"\n⏱️  TIEMPO DE ESPERA: {plan['tiempo_espera']}")

def main():
    """Función principal"""
    print("🩺 SYNAPSEOS - RECOVERY & ALTERNATIVE SETUP")
    print("=" * 50)

    # Configurar OpenAI
    openai_configured = setup_openai_credentials()

    # Probar proveedores
    if openai_configured:
        asyncio.run(test_alternative_providers())

    # Crear plan de recuperación
    create_recovery_plan()

    print("\n" + "=" * 50)
    print("🎯 PRÓXIMOS PASOS:")
    print("1. ENVÍA el appeal a Google Cloud INMEDIATAMENTE")
    print("2. REINICIA SynapseOS para usar OpenAI")
    print("3. MONITOREA el estado de tu cuenta Google Cloud")
    print("4. ESPERA la respuesta del appeal (2-7 días hábiles)")
    print("\n💡 RECUERDA: El appeal es tu mejor opción para recuperar Gemini")

if __name__ == "__main__":
    main()