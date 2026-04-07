#!/usr/bin/env python3
"""
SynapseOS API Key Configuration Tool
Configure API keys for different AI providers
"""

import os
import sys
from pathlib import Path

def update_env_file(key_name: str, new_value: str, env_file: Path):
    """Update a specific key in the .env file"""
    if not env_file.exists():
        print(f"❌ .env file not found at {env_file}")
        return False

    content = env_file.read_text()
    lines = content.split('\n')

    updated = False
    for i, line in enumerate(lines):
        if line.startswith(f'{key_name}='):
            lines[i] = f'{key_name}={new_value}'
            updated = True
            break

    if not updated:
        # Add new key at the end
        lines.append(f'{key_name}={new_value}')

    env_file.write_text('\n'.join(lines))
    return True

def main():
    print("🔑 SYNAPSEOS - CONFIGURACIÓN DE API KEYS")
    print("=" * 50)

    env_file = Path(".env")
    if not env_file.exists():
        print("❌ No .env file found in current directory")
        sys.exit(1)

    print("Current API key status:")
    current_keys = {
        'GEMINI_API_KEY': os.getenv('GEMINI_API_KEY', 'NOT_SET'),
        'GEMINI_IMAGE_API_KEY': os.getenv('GEMINI_IMAGE_API_KEY', 'NOT_SET'),
        'OPENAI_CLIENT_ID': os.getenv('OPENAI_CLIENT_ID', 'NOT_SET'),
        'OPENAI_CLIENT_SECRET': os.getenv('OPENAI_CLIENT_SECRET', 'NOT_SET')
    }

    for key, value in current_keys.items():
        masked = f"***{value[-4:]}" if value != 'NOT_SET' and len(value) > 4 else value
        print(f"  {key}: {masked}")

    print("\nOptions:")
    print("1. Update Gemini API Key (text generation)")
    print("2. Update Gemini Image API Key (image generation)")
    print("3. Update OpenAI OAuth credentials")
    print("4. Test current configuration")
    print("5. Exit")

    choice = input("\nSelect option (1-5): ").strip()

    if choice == '1':
        new_key = input("Enter new Gemini API Key for text generation: ").strip()
        if new_key and update_env_file('GEMINI_API_KEY', new_key, env_file):
            print("✅ Gemini API Key updated successfully")
        else:
            print("❌ Failed to update Gemini API Key")

    elif choice == '2':
        new_key = input("Enter new Gemini API Key for image generation: ").strip()
        if new_key and update_env_file('GEMINI_IMAGE_API_KEY', new_key, env_file):
            print("✅ Gemini Image API Key updated successfully")
        else:
            print("❌ Failed to update Gemini Image API Key")

    elif choice == '3':
        client_id = input("Enter OpenAI Client ID: ").strip()
        client_secret = input("Enter OpenAI Client Secret: ").strip()
        if client_id and client_secret:
            update_env_file('OPENAI_CLIENT_ID', client_id, env_file)
            update_env_file('OPENAI_CLIENT_SECRET', client_secret, env_file)
            print("✅ OpenAI OAuth credentials updated")
        else:
            print("❌ Invalid OpenAI credentials")

    elif choice == '4':
        print("\n🔍 Testing configuration...")
        # Import and test the providers
        try:
            from core.ai_providers import AIProviderManager
            manager = AIProviderManager()
            available = manager.list_available_providers()
            print(f"✅ Available providers: {available}")
        except Exception as e:
            print(f"❌ Configuration test failed: {e}")

    elif choice == '5':
        print("👋 Goodbye!")
        sys.exit(0)

    else:
        print("❌ Invalid option")

    print("\n💡 Remember to restart SynapseOS after updating API keys!")

if __name__ == "__main__":
    main()