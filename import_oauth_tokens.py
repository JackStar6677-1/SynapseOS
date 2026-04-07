#!/usr/bin/env python3
"""
Importar tokens OAuth de openclaw a SynapseOS
Transfiere la sesión activa de ChatGPT Codex 5.4
"""

import os
import json
import shutil
from pathlib import Path

def import_oauth_tokens():
    """Importa los tokens OAuth de openclaw"""
    print("🔄 Importando tokens OAuth de openclaw...")

    # Rutas
    openclaw_auth_file = Path.home() / ".openclaw" / "agents" / "main" / "agent" / "auth-profiles.json"
    synapseos_memory_dir = Path("data") / "memory"

    # Verificar que existe el archivo de openclaw
    if not openclaw_auth_file.exists():
        print(f"❌ No se encuentra el archivo de auth de openclaw: {openclaw_auth_file}")
        return False

    # Leer tokens de openclaw
    with open(openclaw_auth_file, 'r') as f:
        openclaw_auth = json.load(f)

    openai_profile = openclaw_auth["profiles"].get("openai-codex:default")
    if not openai_profile:
        print("❌ No se encontró el perfil openai-codex:default en openclaw")
        return False

    # Extraer información del token
    access_token = openai_profile["access"]
    refresh_token = openai_profile["refresh"]
    expires = openai_profile["expires"]
    account_id = openai_profile["accountId"]

    print("✅ Tokens encontrados:")
    print(f"  Account ID: {account_id}")
    print(f"  Expires: {expires}")
    print(f"  Access Token: {access_token[:50]}...")
    print(f"  Refresh Token: {refresh_token[:20]}...")

    # Crear directorio de memoria si no existe
    synapseos_memory_dir.mkdir(parents=True, exist_ok=True)

    # Crear estructura de memoria para OAuth
    oauth_memory = {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "expires_at": expires,
        "account_id": account_id,
        "client_id": "app_EMoamEEZ73f0CkXaXp7hrann",
        "token_type": "Bearer",
        "scope": "openid profile email offline_access api.connectors.read api.connectors.invoke"
    }

    # Guardar en archivo de memoria
    memory_file = synapseos_memory_dir / "oauth_openai.json"
    with open(memory_file, 'w') as f:
        json.dump(oauth_memory, f, indent=2)

    print(f"✅ Tokens importados a: {memory_file}")

    # Verificar que el .env esté configurado
    env_file = Path(".env")
    if env_file.exists():
        with open(env_file, 'r') as f:
            env_content = f.read()

        if "OPENAI_CLIENT_ID=app_EMoamEEZ73f0CkXaXp7hrann" in env_content:
            print("✅ .env ya configurado correctamente")
        else:
            print("⚠️  Revisa el .env - debería tener OPENAI_CLIENT_ID=app_EMoamEEZ73f0CkXaXp7hrann")

    return True

def test_import():
    """Prueba que la importación funcionó"""
    print("\n🧪 Probando importación...")

    memory_file = Path("data") / "memory" / "oauth_openai.json"
    if not memory_file.exists():
        print("❌ Archivo de memoria no encontrado")
        return False

    with open(memory_file, 'r') as f:
        memory = json.load(f)

    required_fields = ["access_token", "refresh_token", "expires_at", "account_id"]
    for field in required_fields:
        if field not in memory:
            print(f"❌ Falta campo requerido: {field}")
            return False

    print("✅ Todos los campos requeridos presentes")
    print(f"✅ Token expira: {memory['expires_at']} (timestamp)")

    # Verificar que no está expirado (fecha actual aproximada)
    import time
    current_time = int(time.time() * 1000)  # timestamp en ms
    if current_time > memory['expires_at']:
        print("⚠️  Token parece expirado - necesitarás refrescarlo")
    else:
        print("✅ Token válido")

    return True

def main():
    """Función principal"""
    print("🔄 IMPORTADOR DE TOKENS OAUTH")
    print("=" * 40)
    print("Importando sesión ChatGPT Codex 5.4 de openclaw a SynapseOS")
    print()

    # Importar tokens
    if not import_oauth_tokens():
        print("❌ Falló la importación de tokens")
        return

    # Probar importación
    if test_import():
        print("\n🎉 ¡Importación exitosa!")
        print("Ahora puedes usar ChatGPT Codex 5.4 en SynapseOS")
        print("sin necesidad de re-autenticarte")
    else:
        print("\n❌ La importación falló las pruebas")

if __name__ == "__main__":
    main()