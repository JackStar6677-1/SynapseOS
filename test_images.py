#!/usr/bin/env python3
"""
Probar generación de imágenes con Gemini en SynapseOS
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

async def test_image_generation():
    """Prueba la generación de imágenes con Gemini"""
    print("🎨 Probando generación de imágenes con Gemini...")
    print("=" * 50)

    try:
        from core.ai_providers import AIProviderManager
        from core.memory import MemorySystem

        # Initialize memory system
        memory = MemorySystem()

        # Initialize provider manager
        manager = AIProviderManager(memory)

        # Initialize providers (this should load the imported tokens)
        await manager.initialize_providers()

        # Check available providers
        available = await manager.get_available_providers()
        print(f"📊 Proveedores disponibles: {len(available)}")

        for provider in available:
            print(f"  ✅ {provider}")

        # Test image generation with Gemini
        if "gemini" in available:
            print("\n🎨 Probando generación de imagen...")

            test_prompt = "Un paisaje montañoso con un lago al atardecer, estilo realista"
            result = await manager.generate_image(test_prompt, filename="test_gemini_image.png")

            if result and Path(result).exists():
                print(f"✅ Imagen generada exitosamente: {result}")
                print(f"   Tamaño del archivo: {Path(result).stat().st_size} bytes")
            else:
                print("❌ Falló la generación de imagen")
                print(f"   Resultado: {result}")
        else:
            print("\n❌ Gemini no está disponible para generación de imágenes")

        return "gemini" in available

    except Exception as e:
        error_msg = str(e)
        if "expired" in error_msg.lower() or "invalid" in error_msg.lower() or "404" in error_msg or "not found" in error_msg.lower():
            print(f"❌ API key expirada, inválida o modelo no disponible: {error_msg}")
            print("💡 Solución: Ejecuta 'python configure_keys.py' para actualizar la API key de imágenes")
        else:
            print(f"❌ Error desconocido: {error_msg}")
            import traceback
            traceback.print_exc()
        return False

def check_api_keys():
    """Verifica las API keys disponibles"""
    print("🔑 Verificando API keys...")
    print("=" * 30)

    gemini_key = os.getenv("GEMINI_API_KEY")
    image_key = os.getenv("GEMINI_IMAGE_API_KEY")

    print(f"Gemini API Key (texto): {'✅ SET' if gemini_key else '❌ NOT_SET'}")
    print(f"Gemini Image API Key: {'✅ SET' if image_key else '❌ NOT_SET'}")

    if gemini_key and image_key:
        print(f"🔍 Las keys son {'iguales' if gemini_key == image_key else 'diferentes'}")

    return bool(image_key)

def main():
    """Función principal"""
    print("🖼️ SYNAPSEOS - PRUEBA DE GENERACIÓN DE IMÁGENES")
    print("=" * 50)

    # Verificar API keys
    keys_ok = check_api_keys()
    print()

    if not keys_ok:
        print("❌ No hay API key configurada para imágenes")
        return

    # Probar generación de imágenes
    success = asyncio.run(test_image_generation())

    print("\n" + "=" * 50)
    if success:
        print("🎯 RESULTADO: ¡Generación de imágenes funcionando!")
        print("Gemini puede generar imágenes usando la API key específica")
    else:
        print("🎯 RESULTADO: La generación de imágenes necesita ajustes")
        print("💡 Ejecuta 'python configure_keys.py' para configurar API keys válidas")

if __name__ == "__main__":
    main()