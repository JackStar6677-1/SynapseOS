#!/usr/bin/env python3
"""
SynapseOS Multi-Provider AI Demonstration
Shows how SynapseOS can adopt different AI providers dynamically
"""

import asyncio
import logging
import os
from pathlib import Path

# Add the project root to Python path
import sys
sys.path.insert(0, str(Path(__file__).parent))

from main import SynapseOS

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def demonstrate_multi_provider():
    """Demonstrate SynapseOS multi-provider capabilities"""

    print("🤖 SynapseOS Multi-Provider AI Demonstration")
    print("=" * 50)

    # Initialize SynapseOS
    system = SynapseOS()
    await system.initialize()

    print(f"\n📋 System Status:")
    print(f"   Device ID: {system.identity.device_id}")
    print(f"   Current Provider: {system.ai_manager.get_current_provider_name()}")
    print(f"   Available Providers: {', '.join(system.ai_manager.list_available_providers())}")

    # Test current provider
    print(f"\n🧪 Testing Current Provider ({system.ai_manager.get_current_provider_name()}):")
    test_prompt = "Hello! What AI provider are you and what can you do?"
    response = await system.generate_text(test_prompt)
    print(f"   Response: {response}")

    # Demonstrate provider adoption
    print(f"\n🔄 Demonstrating Provider Adoption:")

    available_providers = system.ai_manager.list_available_providers()
    for provider in available_providers:
        print(f"\n   Adopting provider: {provider}")

        # Adopt the provider
        success = await system.adopt_ai_provider(provider)
        if success:
            print(f"   ✅ Successfully adopted {provider}")

            # Test with the new provider
            test_response = await system.generate_text("What makes you unique as an AI?")
            print(f"   Response from {provider}: {test_response[:150]}...")
        else:
            print(f"   ❌ Failed to adopt {provider}")

    # Show final status
    print(f"\n📊 Final Status:")
    print(f"   Current Provider: {system.ai_manager.get_current_provider_name()}")
    print(f"   Total Providers Available: {len(system.ai_manager.list_available_providers())}")

    # Demonstrate conditional adoption
    print(f"\n🎯 Conditional Adoption Demo:")
    print("   Simulating task-based provider selection...")

    # Example: Use Gemini for creative tasks, OpenAI for coding tasks
    tasks = [
        ("Write a creative story about AI", "gemini"),
        ("Explain Python async/await", "openai-codex"),
        ("Generate a poem about technology", "gemini")
    ]

    for task, preferred_provider in tasks:
        print(f"\n   Task: {task}")
        print(f"   Preferred Provider: {preferred_provider}")

        if preferred_provider in system.ai_manager.list_available_providers():
            await system.adopt_ai_provider(preferred_provider)
            response = await system.generate_text(task)
            print(f"   ✅ Completed with {preferred_provider}: {response[:100]}...")
        else:
            print(f"   ⚠️  {preferred_provider} not available, using current provider")
            current = system.ai_manager.get_current_provider_name()
            response = await system.generate_text(task)
            print(f"   ✅ Completed with {current}: {response[:100]}...")

    print(f"\n🎉 Demonstration Complete!")
    print("SynapseOS can dynamically adopt different AI providers based on tasks and availability.")

if __name__ == "__main__":
    # Set up basic environment for demo
    os.environ.setdefault("GEMINI_API_KEY", "demo_key")
    os.environ.setdefault("LOG_LEVEL", "INFO")

    asyncio.run(demonstrate_multi_provider())