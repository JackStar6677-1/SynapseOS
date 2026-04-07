from datetime import datetime
from typing import Dict, Optional

from fastapi import APIRouter, Header, HTTPException, status
from pydantic import BaseModel

from config.settings import VALID_API_KEYS
from core.task_queue import TaskQueue

router = APIRouter(prefix="/api/v1/tasks", tags=["tasks"])
queue = TaskQueue()


class TaskCreateRequest(BaseModel):
    description: str
    priority: Optional[int] = 5
    provider: Optional[str] = None
    metadata: Optional[Dict] = None


class TaskResponse(BaseModel):
    id: str
    description: str
    status: str
    priority: int
    provider: Optional[str] = None
    created_at: str
    updated_at: str
    attempts: int
    result: Optional[str] = None
    error: Optional[str] = None
    metadata: Optional[Dict] = None


def verify_api_key(x_api_key: Optional[str] = Header(None)) -> bool:
    if not VALID_API_KEYS or VALID_API_KEYS == [""]:
        return True
    if x_api_key and x_api_key.strip() in [key.strip() for key in VALID_API_KEYS if key]:
        return True
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or missing API key"
    )


@router.post("/", response_model=TaskResponse)
async def create_task(request: TaskCreateRequest, x_api_key: Optional[str] = Header(None)):
    verify_api_key(x_api_key)
    task_id = queue.enqueue_task(
        description=request.description,
        priority=request.priority,
        provider=request.provider,
        metadata=request.metadata,
    )
    task = queue.get_task(task_id)
    return task


@router.get("/", response_model=Dict[str, list])
async def list_tasks(status: Optional[str] = None, x_api_key: Optional[str] = Header(None)):
    verify_api_key(x_api_key)
    tasks = queue.list_tasks(status=status)
    return {"tasks": tasks}


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(task_id: str, x_api_key: Optional[str] = Header(None)):
    verify_api_key(x_api_key)
    task = queue.get_task(task_id)
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    return task


@router.post("/{task_id}/retry")
async def retry_task(task_id: str, x_api_key: Optional[str] = Header(None)):
    verify_api_key(x_api_key)
    task = queue.get_task(task_id)
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    queue.update_task(task_id, status="pending", error=None)
    return {"message": "Task requeued", "task_id": task_id}


@router.get("/health")
async def tasks_health(x_api_key: Optional[str] = Header(None)):
    verify_api_key(x_api_key)
    return {
        "status": "ok",
        "queue_size": len(queue.list_tasks()),
        "pending_tasks": len(queue.list_tasks(status="pending")),
        "updated_at": datetime.now().isoformat(),
    }
