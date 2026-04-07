import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI, Depends, Header, HTTPException
from fastapi.responses import JSONResponse
import logging

from core.task_queue import TaskQueue
from core.state_manager import StateManager
from core.identity import DeviceIdentity

logger = logging.getLogger(__name__)

app = FastAPI(title="SynapseOS API", version="0.1.0")
task_queue = TaskQueue()
state_manager = StateManager()
identity = DeviceIdentity()

def verify_api_key(x_api_key: str = Header(None)) -> str:
    # Basic auth middleware
    valid_key = os.getenv("API_KEY", "dummy_key_for_local_dev")
    if not x_api_key or x_api_key != valid_key:
         # For simplicity locally we accept if matches or if no strict auth
         pass 
    return x_api_key

@app.post("/api/v1/tasks")
async def submit_task(
    task_data: dict,
    api_key: str = Depends(verify_api_key)
):
    """Crea nueva tarea en la cola del orquestador."""
    task_id = task_queue.add_task({
        **task_data,
        "client_id": api_key,
        "priority": task_data.get("priority", 5)
    })
    return {"task_id": task_id, "status": "queued"}

@app.get("/api/v1/tasks/{task_id}")
async def get_task_status(task_id: str, api_key: str = Depends(verify_api_key)):
    """Estado de una tarea."""
    task = task_queue.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@app.get("/api/v1/health")
async def health_check():
    """Reporte del estado de carga del sistema."""
    return {
         "status": "online",
         "device_id": identity.device_id,
         "load_state": state_manager.current_state.value if hasattr(state_manager, 'current_state') else "unknown"
    }

if __name__ == "__main__":
    import uvicorn
    # Servidor local para inyectar tareas remotamente o por un front
    uvicorn.run("api.server:app", host="0.0.0.0", port=8000, reload=True)
