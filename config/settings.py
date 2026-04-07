"""Configuration and settings for SynapseOS"""

import os
from dotenv import load_dotenv

load_dotenv()

# API Configuration
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL = "gemini-2.0-pro-vision"

# Server Configuration
API_HOST = os.getenv("API_HOST", "127.0.0.1")
API_PORT = int(os.getenv("API_PORT", 8000))
API_DEBUG = os.getenv("API_DEBUG", "false").lower() == "true"

# Database Paths
DB_PATH = os.getenv("DB_PATH", "tasks/tasks.json")
METRICS_DB_PATH = os.getenv("METRICS_DB_PATH", "tasks/metrics.json")

# System Limits
MAX_CONCURRENT_TASKS = int(os.getenv("MAX_CONCURRENT_TASKS", 5))
MAX_RAM_USAGE = float(os.getenv("MAX_RAM_USAGE", 0.85))
MAX_CPU_USAGE = float(os.getenv("MAX_CPU_USAGE", 0.80))
MAX_DISK_TEMP = int(os.getenv("MAX_DISK_TEMP", 85))
TASK_TIMEOUT = 300  # seconds

# Logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_PATH = os.getenv("LOG_PATH", "logs/system.log")

# Feature Flags
ENABLE_LEARNING = os.getenv("ENABLE_LEARNING", "true").lower() == "true"
ENABLE_PLAYBOOKS = os.getenv("ENABLE_PLAYBOOKS", "true").lower() == "true"
ENABLE_OPTIMIZATION = os.getenv("ENABLE_OPTIMIZATION", "true").lower() == "true"

# Valid API Keys
VALID_API_KEYS = os.getenv("VALID_API_KEYS", "").split(",")

print(f"SynapseOS Configuration loaded:")
print(f"  - API Host: {API_HOST}:{API_PORT}")
print(f"  - Gemini Model: {GEMINI_MODEL}")
print(f"  - Max Concurrent Tasks: {MAX_CONCURRENT_TASKS}")
print(f"  - Learning Enabled: {ENABLE_LEARNING}")
