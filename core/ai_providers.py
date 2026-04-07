"""
Multi-Provider AI System for SynapseOS
Supports multiple AI providers: Google Gemini, OpenAI Codex, etc.
"""

import os
import json
import asyncio
import logging
from typing import Optional, Dict, Any, List
from datetime import datetime
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)

class AIProvider(ABC):
    """Abstract base class for AI providers"""

    def __init__(self, name: str, config: Dict[str, Any]):
        self.name = name
        self.config = config
        self.authenticated = False

    @abstractmethod
    async def authenticate(self) -> bool:
        """Authenticate with the provider"""
        pass

    @abstractmethod
    async def generate_text(self, prompt: str, **kwargs) -> str:
        """Generate text using the provider"""
        pass

    @abstractmethod
    async def list_models(self) -> List[str]:
        """List available models"""
        pass

    @property
    @abstractmethod
    def is_available(self) -> bool:
        """Check if provider is available"""
        pass


class GeminiProvider(AIProvider):
    """Google Gemini provider"""

    def __init__(self, config: Dict[str, Any]):
        super().__init__("gemini", config)
        from .gemini_client import GeminiClient
        self.client = GeminiClient(
            api_key=config.get("api_key"),
            image_api_key=config.get("image_api_key")
        )

    async def authenticate(self) -> bool:
        """Authenticate with Gemini API"""
        return await self.client.authenticate()

    async def generate_text(self, prompt: str, **kwargs) -> str:
        """Generate text using Gemini"""
        return await self.client.generate_text(prompt, **kwargs)

    async def generate_image(self, prompt: str, **kwargs) -> str:
        """Generate image using Gemini"""
        return await self.client.generate_image(prompt, **kwargs)

    async def list_models(self) -> List[str]:
        """List Gemini models"""
        return await self.client.list_models()

    @property
    def is_available(self) -> bool:
        """Check if Gemini is available"""
        return self.client.is_available()


class OpenAIProvider(AIProvider):
    """OpenAI Codex provider"""

    def __init__(self, config: Dict[str, Any], oauth_client=None):
        super().__init__("openai-codex", config)
        from .openai_client import OpenAICodexClient
        self.client = OpenAICodexClient(oauth_client=oauth_client, base_url=config.get("base_url"))

    async def authenticate(self) -> bool:
        """Authenticate with OpenAI via OAuth"""
        return await self.client.authenticate()

    async def generate_text(self, prompt: str, **kwargs) -> str:
        """Generate text using OpenAI Codex"""
        return await self.client.generate_text(prompt, **kwargs)

    async def generate_image(self, prompt: str, **kwargs) -> str:
        """OpenAI Codex does not support image generation"""
        raise NotImplementedError("OpenAI Codex provider does not support image generation")

    async def list_models(self) -> List[str]:
        """List OpenAI models"""
        return await self.client.list_models()

    @property
    def is_available(self) -> bool:
        """Check if OpenAI is available"""
        return self.client.is_available()


class AIProviderManager:
    """Manages multiple AI providers"""

    def __init__(self, memory_system=None):
        self.providers: Dict[str, AIProvider] = {}
        self.memory = memory_system
        self.current_provider = None
        self._load_provider_configs()

    def _load_provider_configs(self):
        """Load provider configurations"""
        if self.memory:
            configs = self.memory.retrieve("ai_providers") or {}
        else:
            configs = {}

        # Default configurations
        default_configs = {
            "gemini": {
                "api_key": os.getenv("GEMINI_API_KEY"),
                "image_api_key": os.getenv("GEMINI_IMAGE_API_KEY"),
                "enabled": True
            },
            "openai-codex": {
                "base_url": "https://chatgpt.com/backend-api",
                "enabled": bool(os.getenv("OPENAI_CLIENT_ID"))
            }
        }

        # Merge with stored configs
        for name, config in default_configs.items():
            if name not in configs:
                configs[name] = config

        logger.info(f"Provider configs loaded: {configs}")
        self._save_provider_configs(configs)

        # Initialize providers
        self._initialize_providers(configs)

    def _initialize_providers(self, configs: Dict):
        """Initialize AI providers"""
        # Gemini provider (with error handling)
        if configs.get("gemini", {}).get("enabled"):
            gemini_provider = GeminiProvider(configs["gemini"])
            # Test if Gemini is actually available
            try:
                # Check if there's already an event loop running
                try:
                    loop = asyncio.get_running_loop()
                    # If we get here, there's already a loop running
                    # Create a task instead of running directly
                    import concurrent.futures
                    with concurrent.futures.ThreadPoolExecutor() as executor:
                        future = executor.submit(asyncio.run, self._test_provider_availability(gemini_provider))
                        available = future.result(timeout=10)
                except RuntimeError:
                    # No loop running, we can create one
                    available = asyncio.run(self._test_provider_availability(gemini_provider))
                
                if available:
                    self.register_provider(gemini_provider)
                    logger.info("Gemini provider registered and available")
                else:
                    logger.warning("Gemini provider not available (API suspended), skipping")
            except Exception as e:
                logger.warning(f"Gemini provider test failed: {e}, skipping")

        # OpenAI provider
        if configs.get("openai-codex", {}).get("enabled") and hasattr(self, 'oauth_client'):
            openai_provider = OpenAIProvider(configs["openai-codex"], self.oauth_client)
            self.register_provider(openai_provider)
            logger.info("OpenAI Codex provider registered")

    async def _test_provider_availability(self, provider):
        """Test if a provider is actually available"""
        try:
            # Quick test - try to authenticate
            result = await provider.authenticate()
            return result
        except Exception as e:
            logger.warning(f"Provider {provider.name} availability test failed: {e}")
            return False

    def set_oauth_client(self, oauth_client):
        """Set OAuth client for OpenAI provider"""
        self.oauth_client = oauth_client
        # Re-initialize providers with OAuth
        configs = self.memory.retrieve("ai_providers") or {}
        self._initialize_providers(configs)

    def _save_provider_configs(self, configs: Dict):
        """Save provider configurations"""
        if self.memory:
            self.memory.store("ai_providers", configs, "config")

    def register_provider(self, provider: AIProvider):
        """Register an AI provider"""
        self.providers[provider.name] = provider
        logger.info(f"Registered AI provider: {provider.name}")

    def get_provider(self, name: str) -> Optional[AIProvider]:
        """Get a provider by name"""
        return self.providers.get(name)

    def list_available_providers(self) -> List[str]:
        """List available providers"""
        return [name for name, provider in self.providers.items() if provider.is_available]

    async def adopt_provider(self, provider_name: str) -> bool:
        """Adopt/switch to a specific provider"""
        provider = self.get_provider(provider_name)
        if not provider:
            logger.error(f"Provider not found: {provider_name}")
            return False

        if not provider.is_available:
            logger.error(f"Provider not available: {provider_name}")
            return False

        # Authenticate if needed
        if not provider.authenticated:
            success = await provider.authenticate()
            if not success:
                return False

        self.current_provider = provider
        logger.info(f"Adopted AI provider: {provider_name}")

        # Store current provider preference
        if self.memory:
            self.memory.store("current_ai_provider", provider_name, "config")

        return True

    async def generate_text(self, prompt: str, provider: str = None, **kwargs) -> str:
        """Generate text using specified or current provider"""
        target_provider = self.current_provider

        if provider:
            target_provider = self.get_provider(provider)
            if not target_provider:
                logger.error(f"Requested provider not found: {provider}")
                return ""

        if not target_provider:
            logger.error("No active provider")
            return ""

        return await target_provider.generate_text(prompt, **kwargs)

    async def generate_image(self, prompt: str, provider: str = None, **kwargs) -> str:
        """Generate image using specified or current provider"""
        target_provider = self.current_provider

        if provider:
            target_provider = self.get_provider(provider)
            if not target_provider:
                logger.error(f"Requested provider not found: {provider}")
                return ""

        if not target_provider:
            logger.error("No active provider")
            return ""

        # Check if the provider supports image generation
        if not hasattr(target_provider, 'generate_image'):
            logger.error(f"Provider {target_provider.name} does not support image generation")
            return ""

        return await target_provider.generate_image(prompt, **kwargs)

    def get_current_provider_name(self) -> Optional[str]:
        """Get name of current provider"""
        return self.current_provider.name if self.current_provider else None

    async def initialize(self):
        """Initialize provider manager"""
        # Try to restore previous provider
        if self.memory:
            previous_provider = self.memory.retrieve("current_ai_provider")
            if previous_provider and previous_provider in self.providers:
                # Verify the provider is still available
                provider = self.get_provider(previous_provider)
                if await self._test_provider_availability(provider):
                    await self.adopt_provider(previous_provider)
                    return

        # Default to first available provider
        available = await self.get_available_providers_async()
        if available:
            await self.adopt_provider(available[0])
        else:
            logger.warning("No AI providers available. System will need manual provider setup.")

    async def get_available_providers_async(self):
        """Get list of actually available providers (async)"""
        available = []
        for name, provider in self.providers.items():
            if await self._test_provider_availability(provider):
                available.append(name)
        return available

    async def refresh_providers(self):
        """Refresh provider availability and return names of available providers"""
        available = []
        for name, provider in list(self.providers.items()):
            if await self._test_provider_availability(provider):
                available.append(name)
            else:
                logger.warning(f"Provider {name} not available during refresh")
        return available

    async def initialize_providers(self):
        """Initialize providers (public method)"""
        await self.initialize()

    async def get_available_providers(self):
        """Get list of available providers (public async method)"""
        return await self.get_available_providers_async()