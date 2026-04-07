import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List

class TaskMetrics:
    def __init__(self, task_id: str, task_type: str, duration_sec: float, success: bool, steps: int):
        self.task_id = task_id
        self.task_type = task_type
        self.duration_sec = duration_sec
        self.success = success
        self.steps = steps
        
    def to_dict(self):
        return {
            "task_id": self.task_id,
            "task_type": self.task_type,
            "duration": self.duration_sec,
            "success": self.success,
            "steps_taken": self.steps,
            "timestamp": datetime.now().isoformat()
        }

class MetricsEngine:
    """Motor que almacena las estadísticas reales de ejecución del host."""
    def __init__(self, db_path: str = "tasks/metrics.json"):
        self.db_path = Path("tasks") / "metrics.json"
        self.metrics = []
        self._load()
    
    def _load(self):
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        if self.db_path.exists():
            try:
                with open(self.db_path, "r") as f:
                    self.metrics = json.load(f)
            except:
                self.metrics = []
                
    def _save(self):
        with open(self.db_path, "w") as f:
            json.dump(self.metrics, f, indent=2)
            
    def record(self, metric: TaskMetrics):
        self.metrics.append(metric.to_dict())
        self._save()
        
    def get_pattern(self, task_type: str) -> Optional[Dict[str, Any]]:
        """Analiza histórico para este tipo de tarea, e.g. ver tasa de exito."""
        similar = [m for m in self.metrics if m.get("task_type") == task_type]
        if not similar: return None
        
        successes = [m for m in similar if m.get("success")]
        return {
            "total_attempts": len(similar),
            "success_rate": len(successes) / len(similar),
            "avg_duration": sum(m["duration"] for m in similar) / len(similar) if similar else 0
        }
