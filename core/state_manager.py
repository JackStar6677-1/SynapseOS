import asyncio
import logging
import os
import shutil
from enum import Enum
from typing import Dict, Optional

logger = logging.getLogger(__name__)


class SystemState(str, Enum):
    IDLE = "IDLE"
    WORKING = "WORKING"
    THINKING = "THINKING"
    OVERLOADED = "OVERLOADED"


class StateManager:
    """Basic system state manager for SynapseOS."""

    def __init__(self):
        self.current_state = SystemState.IDLE
        self.metrics: Dict[str, Optional[float]] = {
            "cpu_percent": None,
            "memory_percent": None,
            "disk_percent": None,
        }
        self._psutil = self._import_psutil()

    def _import_psutil(self):
        try:
            import psutil
            return psutil
        except ImportError:
            logger.warning("psutil not installed; using fallback metrics")
            return None

    def _collect_metrics(self):
        if self._psutil:
            self.metrics["cpu_percent"] = self._psutil.cpu_percent(interval=0.1)
            memory = self._psutil.virtual_memory()
            self.metrics["memory_percent"] = memory.percent
            disk = self._psutil.disk_usage(os.getcwd())
            self.metrics["disk_percent"] = disk.percent
        else:
            self.metrics["cpu_percent"] = None
            self.metrics["memory_percent"] = None
            try:
                disk = shutil.disk_usage(os.getcwd())
                self.metrics["disk_percent"] = round(disk.used / disk.total * 100, 2)
            except Exception:
                self.metrics["disk_percent"] = None

    def _decide_state(self) -> SystemState:
        if self.metrics["memory_percent"] is not None and self.metrics["memory_percent"] > 90:
            return SystemState.OVERLOADED
        if self.metrics["cpu_percent"] is not None and self.metrics["cpu_percent"] > 80:
            return SystemState.THINKING
        if self.metrics["disk_percent"] is not None and self.metrics["disk_percent"] > 95:
            return SystemState.OVERLOADED
        return SystemState.IDLE

    async def monitor_loop(self, interval: float = 5.0):
        while True:
            try:
                self._collect_metrics()
                new_state = self._decide_state()
                if new_state != self.current_state:
                    logger.info(f"State changed: {self.current_state} -> {new_state}")
                    self.current_state = new_state
            except Exception as e:
                logger.error(f"Error collecting metrics: {e}")
            await asyncio.sleep(interval)

    def get_status(self) -> Dict[str, Optional[float]]:
        return {
            "state": self.current_state,
            "metrics": self.metrics,
        }

    def is_overloaded(self) -> bool:
        return self.current_state == SystemState.OVERLOADED
