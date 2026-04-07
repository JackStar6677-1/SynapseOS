"""
SynapseOS - Autonomous AI Operating Agent
Main entry point
"""

import asyncio
import os
import logging
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure basic logging (will be reconfigured in main with file handler)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Core components
from core.memory import MemorySystem
from core.identity import DeviceIdentity
from core.oauth import OAuth2Client, OAuth2Config
from core.ai_providers import AIProviderManager
from core.state_manager import StateManager
from core.task_queue import TaskQueue
from core.orchestrator import TaskOrchestrator


class SynapseOS:
    """Main orchestrator for autonomous AI system"""
    
    def __init__(self):
        self.version = "0.1.0"
        self.started_at = datetime.now()
        logger.info(f"Initializing SynapseOS v{self.version}")
        
        # Initialize core components
        self.memory = MemorySystem()
        self.identity = DeviceIdentity()
        
        # Initialize AI Provider Manager
        self.ai_manager = AIProviderManager(self.memory)
        
        # Initialize OAuth if configured
        oauth_config = None
        client_id = os.getenv("OPENAI_CLIENT_ID")
        client_secret = os.getenv("OPENAI_CLIENT_SECRET")
        
        # Check if we have imported tokens available
        imported_tokens_available = False
        try:
            from pathlib import Path
            token_file = Path("data") / "memory" / "oauth_openai.json"
            imported_tokens_available = token_file.exists()
        except:
            pass
        
        if client_id and (client_secret or imported_tokens_available):
            # Use a dummy client_secret if we have imported tokens but no real secret
            if not client_secret and imported_tokens_available:
                client_secret = "imported_tokens_mode"
                logger.info("Using imported tokens mode - client_secret not required")
            
            oauth_config = OAuth2Config(
                client_id=client_id,
                client_secret=client_secret,
                redirect_uri=os.getenv("OAUTH_REDIRECT_URI", "http://localhost:8000/auth/callback")
            )
            self.oauth = OAuth2Client(oauth_config, self.memory)
            # Set OAuth client for AI providers
            self.ai_manager.set_oauth_client(self.oauth)
        else:
            self.oauth = None
            logger.warning("OAuth not configured - OpenAI Codex will not be available")
        
        self.state_manager = StateManager()
        self.task_queue = TaskQueue()
        self.orchestrator = TaskOrchestrator(self.ai_manager, self.task_queue, self.state_manager)
    
    async def initialize(self):
        """Initialize system and log startup"""
        # Log system startup
        self.memory.log_daily_event("system_startup", {
            "version": self.version,
            "device_id": self.identity.device_id,
            "started_at": self.started_at.isoformat()
        })
        
        # Initialize AI providers
        await self.ai_manager.initialize()
        
        # Store system info in memory
        current_provider = self.ai_manager.get_current_provider_name()
        self.memory.store("system_info", {
            "version": self.version,
            "device_id": self.identity.device_id,
            "started_at": self.started_at.isoformat(),
            "current_ai_provider": current_provider,
            "available_providers": self.ai_manager.list_available_providers(),
            "oauth_configured": self.oauth is not None
        }, "system")
        
        logger.info(f"SynapseOS v{self.version} initialized with device ID: {self.identity.device_id}")
        logger.info(f"Current AI provider: {current_provider or 'None'}")
        logger.info(f"Available providers: {', '.join(self.ai_manager.list_available_providers())}")
        asyncio.create_task(self.state_manager.monitor_loop())
    
    async def adopt_ai_provider(self, provider_name: str) -> bool:
        """Adopt/switch to a different AI provider"""
        success = await self.ai_manager.adopt_provider(provider_name)
        if success:
            # Update system info
            current_provider = self.ai_manager.get_current_provider_name()
            self.memory.store("system_info", {
                "current_ai_provider": current_provider,
                "provider_switched_at": datetime.now().isoformat()
            }, "system")
            
            # Log the change
            self.memory.log_daily_event("provider_adoption", {
                "new_provider": provider_name,
                "timestamp": datetime.now().isoformat()
            })
            
            logger.info(f"Successfully adopted AI provider: {provider_name}")
        else:
            logger.error(f"Failed to adopt AI provider: {provider_name}")
        
        return success
    
    async def generate_text(self, prompt: str, provider: str = None, **kwargs) -> str:
        """Generate text using AI provider"""
        return await self.ai_manager.generate_text(prompt, provider, **kwargs)
    
    async def refresh_ai_providers(self):
        """Refresh and re-test all AI providers"""
        logger.info("Refreshing AI providers...")
        available_before = self.ai_manager.list_available_providers()
        
        new_available = await self.ai_manager.refresh_providers()
        
        logger.info(f"Provider refresh complete")
        logger.info(f"Before: {available_before}")
        logger.info(f"After: {new_available}")
        
        # Log the change
        self.memory.log_daily_event("provider_refresh", {
            "before": available_before,
            "after": new_available,
            "timestamp": datetime.now().isoformat()
        })
        
        return new_available
    
    async def test_providers(self):
        """Test all available AI providers"""
        logger.info("Testing AI providers...")
        
        test_prompt = "Hello, can you introduce yourself briefly?"
        
        for provider_name in self.ai_manager.list_available_providers():
            logger.info(f"Testing provider: {provider_name}")
            try:
                response = await self.generate_text(test_prompt, provider_name)
                logger.info(f"{provider_name} response: {response[:100]}...")
            except Exception as e:
                logger.error(f"Failed to test {provider_name}: {e}")
    
    async def demonstrate_adoption(self):
        """Demonstrate dynamic provider adoption"""
        logger.info("Demonstrating AI provider adoption...")
        
        # Show current provider
        current = self.ai_manager.get_current_provider_name()
        logger.info(f"Current provider: {current}")
        
        # Test generation with current provider
        response = await self.generate_text("What is your name?")
        logger.info(f"Response from {current}: {response}")
        
        # List all available providers
        available = self.ai_manager.list_available_providers()
        logger.info(f"Available providers: {', '.join(available)}")
        
        # Try to adopt each provider
        for provider in available:
            if provider != current:
                logger.info(f"Attempting to adopt provider: {provider}")
                success = await self.adopt_ai_provider(provider)
                if success:
                    new_response = await self.generate_text("What AI model are you?")
                    logger.info(f"Response from {provider}: {new_response}")
                else:
                    logger.error(f"Failed to adopt {provider}")
    
    async def run(self):
        """Main run loop - coordinator of all operations"""
        logger.info("SynapseOS started")
        
        try:
            while True:
                try:
                    if self.state_manager.is_overloaded():
                        logger.warning("System overloaded, deferring task execution")
                        await asyncio.sleep(10)
                        continue

                    task = self.task_queue.get_next_task()
                    if not task:
                        logger.debug("No pending tasks, sleeping")
                        await asyncio.sleep(5)
                        continue

                    logger.info(f"Picked up task: {task['id']} - {task['description']}")
                    result = await self.orchestrator.execute_task(task)
                    logger.info(f"Task {task['id']} result: {result}")
                    await asyncio.sleep(1)
                except Exception as e:
                    logger.error(f"Error in main loop: {e}", exc_info=True)
                    await asyncio.sleep(5)
        
        except KeyboardInterrupt:
            logger.info("Shutdown signal received")
        except Exception as e:
            logger.error(f"Fatal error: {e}", exc_info=True)
        finally:
            logger.info("SynapseOS shutdown")
    
    async def health_check(self) -> dict:
        """Return system health status"""
        return {
            "status": "running",
            "version": self.version,
            "uptime": (datetime.now() - self.started_at).total_seconds(),
            # TODO: Add actual metrics
        }


async def main():
    """Entry point"""
    # Ensure necessary directories exist
    Path("logs").mkdir(exist_ok=True)
    Path("tasks").mkdir(exist_ok=True)
    Path("config").mkdir(exist_ok=True)
    
    # Configure logging with file handler after directories are created
    file_handler = logging.FileHandler('logs/system.log')
    stream_handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    stream_handler.setFormatter(formatter)
    
    # Remove existing handlers and add new ones
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)
    logger.setLevel(logging.INFO)
    
    logger.info("=" * 50)
    logger.info("SynapseOS - Autonomous AI Operating Agent")
    logger.info("=" * 50)
    
    system = SynapseOS()
    await system.initialize()
    await system.run()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Interrupted by user")
    except Exception as e:
        logger.error(f"Unhandled exception: {e}", exc_info=True)
        exit(1)
