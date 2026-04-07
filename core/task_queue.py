import json
import os
import uuid
from datetime import datetime
from typing import Dict, List, Optional


class TaskQueue:
    """Simple JSON-backed task queue for SynapseOS."""

    def __init__(self, task_file: str = "tasks/tasks.json"):
        self.task_file = task_file
        os.makedirs(os.path.dirname(self.task_file), exist_ok=True)
        if not os.path.exists(self.task_file):
            with open(self.task_file, "w", encoding="utf-8") as f:
                json.dump({"tasks": []}, f, indent=2)

    def _load(self) -> Dict[str, List[Dict]]:
        try:
            with open(self.task_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {"tasks": []}

    def _save(self, data: Dict[str, List[Dict]]):
        with open(self.task_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    def enqueue_task(self, description: str, priority: int = 5, provider: str = None, metadata: Dict = None) -> str:
        tasks_data = self._load()
        task_id = uuid.uuid4().hex[:16]
        task = {
            "id": task_id,
            "description": description,
            "priority": priority,
            "provider": provider,
            "status": "pending",
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "attempts": 0,
            "result": None,
            "error": None,
            "metadata": metadata or {}
        }
        tasks_data["tasks"].append(task)
        self._save(tasks_data)
        return task_id

    def list_tasks(self, status: str = None) -> List[Dict]:
        tasks_data = self._load()
        tasks = tasks_data.get("tasks", [])
        if status:
            return [t for t in tasks if t.get("status") == status]
        return tasks

    def get_task(self, task_id: str) -> Optional[Dict]:
        tasks_data = self._load()
        for task in tasks_data.get("tasks", []):
            if task.get("id") == task_id:
                return task
        return None

    def get_next_task(self) -> Optional[Dict]:
        tasks = self.list_tasks(status="pending")
        if not tasks:
            return None
        tasks.sort(key=lambda t: (t.get("priority", 5), t.get("created_at", "")))
        return tasks[0]

    def update_task(self, task_id: str, **updates) -> bool:
        tasks_data = self._load()
        changed = False
        for task in tasks_data.get("tasks", []):
            if task.get("id") == task_id:
                task.update(updates)
                task["updated_at"] = datetime.now().isoformat()
                changed = True
        if changed:
            self._save(tasks_data)
        return changed

    def mark_task_completed(self, task_id: str, result: str) -> bool:
        return self.update_task(task_id, status="completed", result=result, error=None)

    def mark_task_failed(self, task_id: str, error: str) -> bool:
        return self.update_task(task_id, status="failed", error=error)

    def increment_attempts(self, task_id: str) -> bool:
        tasks_data = self._load()
        changed = False
        for task in tasks_data.get("tasks", []):
            if task.get("id") == task_id:
                task["attempts"] = task.get("attempts", 0) + 1
                task["updated_at"] = datetime.now().isoformat()
                changed = True
        if changed:
            self._save(tasks_data)
        return changed
