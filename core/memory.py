"""
Memory System for SynapseOS
Persistent memory management inspired by OpenClaw
"""

import sqlite3
import json
import os
from datetime import datetime, date
from typing import Dict, List, Any, Optional
import logging

logger = logging.getLogger(__name__)

class MemorySystem:
    """Persistent memory system with SQLite backend and daily logs"""

    def __init__(self, db_path: str = "memory/main.sqlite", workspace_path: str = "memory"):
        self.db_path = db_path
        self.workspace_path = workspace_path
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        os.makedirs(workspace_path, exist_ok=True)
        self._init_db()

    def _init_db(self):
        """Initialize SQLite database"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS memories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    key TEXT UNIQUE,
                    value TEXT,
                    category TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            conn.execute('''
                CREATE TABLE IF NOT EXISTS sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT UNIQUE,
                    data TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            conn.commit()

    def store(self, key: str, value: Any, category: str = "general"):
        """Store a memory item"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute('''
                    INSERT OR REPLACE INTO memories (key, value, category, updated_at)
                    VALUES (?, ?, ?, CURRENT_TIMESTAMP)
                ''', (key, json.dumps(value), category))
                conn.commit()
            logger.info(f"Stored memory: {key}")
        except Exception as e:
            logger.error(f"Failed to store memory: {e}")

    def retrieve(self, key: str) -> Optional[Any]:
        """Retrieve a memory item"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute('SELECT value FROM memories WHERE key = ?', (key,))
                row = cursor.fetchone()
                if row:
                    return json.loads(row[0])
        except Exception as e:
            logger.error(f"Failed to retrieve memory: {e}")
        return None

    def list_memories(self, category: str = None) -> List[Dict]:
        """List all memories, optionally filtered by category"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                if category:
                    cursor = conn.execute('SELECT key, value, category, updated_at FROM memories WHERE category = ?', (category,))
                else:
                    cursor = conn.execute('SELECT key, value, category, updated_at FROM memories')
                return [{
                    'key': row[0],
                    'value': json.loads(row[1]),
                    'category': row[2],
                    'updated_at': row[3]
                } for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Failed to list memories: {e}")
            return []

    def log_daily_event(self, event: str, details: Dict = None):
        """Log an event to today's daily file"""
        today = date.today().isoformat()
        filename = f"{today}.md"
        filepath = os.path.join(self.workspace_path, filename)

        timestamp = datetime.now().isoformat()
        log_entry = f"## {timestamp}\n{event}\n"
        if details:
            log_entry += f"Details: {json.dumps(details, indent=2)}\n"
        log_entry += "\n"

        try:
            with open(filepath, 'a', encoding='utf-8') as f:
                f.write(log_entry)
            logger.info(f"Logged daily event: {event[:50]}...")
        except Exception as e:
            logger.error(f"Failed to log daily event: {e}")

    def read_daily_log(self, date_str: str = None) -> str:
        """Read daily log for specified date (default: today)"""
        if not date_str:
            date_str = date.today().isoformat()
        filepath = os.path.join(self.workspace_path, f"{date_str}.md")

        try:
            if os.path.exists(filepath):
                with open(filepath, 'r', encoding='utf-8') as f:
                    return f.read()
        except Exception as e:
            logger.error(f"Failed to read daily log: {e}")
        return ""

    def update_long_term_memory(self, content: str):
        """Update the long-term MEMORY.md file"""
        filepath = os.path.join(self.workspace_path, "MEMORY.md")
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            logger.info("Updated long-term memory")
        except Exception as e:
            logger.error(f"Failed to update long-term memory: {e}")

    def read_long_term_memory(self) -> str:
        """Read the long-term MEMORY.md file"""
        filepath = os.path.join(self.workspace_path, "MEMORY.md")
        try:
            if os.path.exists(filepath):
                with open(filepath, 'r', encoding='utf-8') as f:
                    return f.read()
        except Exception as e:
            logger.error(f"Failed to read long-term memory: {e}")
        return ""

    def store_session(self, session_id: str, data: Dict):
        """Store session data"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute('''
                    INSERT OR REPLACE INTO sessions (session_id, data)
                    VALUES (?, ?)
                ''', (session_id, json.dumps(data)))
                conn.commit()
            logger.info(f"Stored session: {session_id}")
        except Exception as e:
            logger.error(f"Failed to store session: {e}")

    def retrieve_session(self, session_id: str) -> Optional[Dict]:
        """Retrieve session data"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute('SELECT data FROM sessions WHERE session_id = ?', (session_id,))
                row = cursor.fetchone()
                if row:
                    return json.loads(row[0])
        except Exception as e:
            logger.error(f"Failed to retrieve session: {e}")
        return None