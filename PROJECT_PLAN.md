# SynapseOS - Plan de Implementación Detallado

## Fase 0: Preparación Inicial (Day 1)

### ✅ Tareas
- [x] Crear estructura de carpetas
- [x] Definir arquitectura
- [x] Crear documentación inicial
- [ ] Configurar repositorio Git
- [ ] Crear archivo `.env.example`
- [ ] Instalar dependencias base

### Entregables
- Carpeta `SynapseOS/` con README, ARCHITECTURE, este archivo
- `requirements.txt` inicial

---

## Fase 1: Core Base (Días 1-5)

### Objetivo
Tener un sistema que pueda recibir comandos de Gemini y ejecutar acciones básicas

### 1.1 State Management (Día 1)

**Archivo**: `core/state_manager.py`

```python
# Crear clase SystemState con máquina de estados
# - IDLE → WORKING → THINKING → OVERLOADED → IDLE
# - Monitorear CPU, RAM, Disk continuamente
# - Transiciones automáticas basadas en umbrales

class StateManager:
    def __init__(self):
        self.current_state = SystemState.IDLE
        self.metrics = {}
        self.transition_callbacks = []
    
    async def monitor_loop(self, interval: float = 2.0):
        """Monitorea recursos cada 2 segundos"""
        
    async def transition_to(self, new_state: SystemState):
        """Cambia estado y notifica"""
```

**Tests**:
- Verificar transiciones según CPU/RAM
- Verificar que transiciones son thread-safe

### 1.2 Gemini Client (Día 2)

**Archivo**: `core/gemini_client.py`

```python
import google.generativeai as genai

class GeminiClient:
    def __init__(self, api_key: str):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(
            model_name="gemini-2.0-pro-vision",
            generation_config={
                "max_output_tokens": 500,
                "temperature": 0.1,  # Bajo = más determinístico
            }
        )
    
    async def ask_for_plan(self, task: str, system_state: dict) -> str:
        """
        Pregunta a Gemini qué hacer para completar tarea
        Retorna: JSON con lista de comandos
        """
        
    async def analyze_screenshot(self, image_bytes: bytes) -> str:
        """
        Pasa screenshot a Gemini para análisis visual
        """
        
    async def recover_from_error(self, error_msg: str, screenshot: bytes) -> str:
        """
        Pide a Gemini sugerencias para recuperarse de error
        """
```

**Tests**:
- Verificar que API key es válido
- Test de análisis de screenshot
- Test de generación de plan

### 1.3 Input Control - Básico (Día 3)

**Archivo**: `abilities/input_control.py`

```python
import pyautogui
import time

async def mouse_move(x: int, y: int, duration: float = 0.5):
    """Mueve mouse con trayectoria suave"""
    pyautogui.moveTo(x, y, duration=duration)
    return {"status": "success", "x": x, "y": y}

async def mouse_click(x: int, y: int, button: str = "left"):
    """Click en posición"""
    pyautogui.click(x, y, button=button)
    return {"status": "success"}

async def keyboard_type(text: str, interval: float = 0.05):
    """Escribe texto"""
    for char in text:
        pyautogui.typeKey(char)
        time.sleep(interval)
    return {"status": "success", "length": len(text)}

async def keyboard_hotkey(key1: str, key2: str = None):
    """Atajo (Ctrl+C, Alt+Tab, etc)"""
    if key2:
        pyautogui.hotkey(key1, key2)
    else:
        pyautogui.press(key1)
    return {"status": "success"}

async def screenshot() -> bytes:
    """Captura pantalla"""
    from PIL import ImageGrab
    import io
    
    img = ImageGrab.grab()
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    return buffer.getvalue()
```

**Dependencies**:
- `pip install pyautogui pil`

**Tests**:
- Test: Abrir Notepad
- Test: Escribir "Hola Mundo"
- Test: Capturar screenshot
- Test: Encontrar Notepad en pantalla

### 1.4 Window Management (Día 4)

**Archivo**: `abilities/window_management.py`

```python
import pygetwindow as pgw

async def list_windows() -> list:
    """Lista ventanas abiertas"""
    windows = []
    for w in pgw.getAllWindows():
        if w.title.strip():  # Ignorar ventanas sin título
            windows.append({
                "title": w.title,
                "x": w.left,
                "y": w.top,
                "width": w.width,
                "height": w.height,
                "active": w.isActive
            })
    return windows

async def get_active_window() -> dict:
    """Obtiene ventana actualmente enfocada"""
    active = pgw.getActiveWindow()
    if not active:
        return None
    return {
        "title": active.title,
        "x": active.left,
        "y": active.top,
        "width": active.width,
        "height": active.height
    }

async def activate_window(window_title: str) -> bool:
    """Trae ventana al frente"""
    for window in pgw.getAllWindows():
        if window_title.lower() in window.title.lower():
            window.activate()
            return True
    return False

async def close_window(window_title: str) -> bool:
    """Cierra ventana"""
    for window in pgw.getAllWindows():
        if window_title.lower() in window.title.lower():
            window.close()
            return True
    return False
```

**Tests**:
- Test: Listar ventanas abiertas
- Test: Activar ventana específica
- Test: Cerrar ventana

### 1.5 App Launcher (Día 5)

**Archivo**: `abilities/app_launcher.py`

```python
import subprocess
import shutil

async def launch_app(app_name: str, args: list = []) -> dict:
    """Abre aplicación"""
    try:
        # Busca ejecutable en PATH
        exe_path = shutil.which(app_name)
        if not exe_path and not app_name.endswith('.exe'):
            exe_path = shutil.which(app_name + '.exe')
        
        if exe_path:
            proc = subprocess.Popen([exe_path] + args)
            return {
                "status": "success",
                "pid": proc.pid,
                "app": app_name
            }
        else:
            # Buscar en programas instalados
            # (Implementar búsqueda en Program Files)
            return {"status": "error", "message": "App not found"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

async def close_app(app_name: str, force: bool = False) -> bool:
    """Cierra aplicación"""
    # Implementar búsqueda de proceso y terminación
    pass

async def is_app_running(app_name: str) -> bool:
    """Verifica si app está corriendo"""
    pass
```

**Tests**:
- Test: Abrir Notepad
- Test: Abrir Chrome
- Test: Cerrar aplicación

### Checkpoint 1: Integration Test

```python
# integration_test_phase1.py
async def test_phase1():
    """
    1. State Manager inicia en IDLE
    2. Comienza a monitorear recursos
    3. Gemini Client se inicializa
    4. Testear cada ability básica
    5. Ejecutar: Abrir Notepad, escribir, capturar, cerrar
    """
```

---

## Fase 2: Con Conciencia de Pantalla (Días 6-10)

### Objetivo
Que Gemini entienda qué está en la pantalla y tome decisiones basadas en eso

### 2.1 OCR & Visual Detection (Días 6-7)

**Archivo**: `abilities/vision.py`

```python
import pytesseract
from PIL import Image

async def ocr_screen() -> dict:
    """Lee TODO el texto visible en pantalla"""
    screenshot = await screenshot()  # De input_control
    
    # Primera pasada: Gemini vision (más preciso)
    # Segunda pasada: pytesseract (fallback si Gemini falla)
    
    return {
        "status": "success",
        "text": "...all text...",
        "elements": [
            {"text": "Save", "x": 100, "y": 200, "bbox": (100, 200, 150, 220)},
            # ...
        ]
    }

async def detect_button(button_text: str) -> tuple:
    """Encuentra botón por texto visual"""
    # OCR → Buscar texto → Retornar coordenadas
    pass

async def detect_element(description: str, screenshot: bytes = None) -> tuple:
    """
    Usa Gemini vision para encontrar elemento por descripción
    Ej: "botón azul con texto Guardar"
    """
    pass
```

**Dependencies**:
- `pip install pytesseract pillow`

### 2.2 Screenshot Analysis con Gemini (Días 8-9)

**Actualizar**: `core/gemini_client.py`

```python
async def analyze_screenshot(self, image_bytes: bytes) -> dict:
    """
    Pasa screenshot a Gemini vision para análisis
    """
    image_data = base64.standard_b64encode(image_bytes).decode("utf-8")
    
    response = await self.model.generate_content_async([
        "Analiza esta captura de pantalla y dame:",
        "1. Ventana principal abierta",
        "2. Botones visibles",
        "3. Campos de texto o entrada",
        "4. Errores o diálogos",
        "Formato: JSON",
        {
            "mime_type": "image/png",
            "data": image_data
        }
    ])
    
    return json.loads(response.text)
```

### 2.3 Task Orchestrator - V1 (Día 10)

**Archivo**: `core/task_orchestrator.py`

```python
class TaskOrchestrator:
    def __init__(self, state_manager, gemini_client):
        self.state_manager = state_manager
        self.gemini = gemini_client
        self.current_task = None
    
    async def execute_task(self, task: str) -> dict:
        """
        1. Captura estado actual
        2. Pregunta a Gemini qué hacer
        3. Ejecuta cada comando
        4. Si error, recupera
        5. Retorna resultado
        """
        
        # 1. Estado actual
        current_state = await self.state_manager.get_state()
        screenshot = await screenshot()
        
        # 2. Pedir plan a Gemini
        plan_json = await self.gemini.ask_for_plan(task, {
            "state": current_state,
            "screenshot": screenshot,
            "windows": await list_windows()
        })
        
        plan = json.loads(plan_json)
        results = []
        
        # 3. Ejecutar cada comando
        for step in plan["steps"]:
            try:
                result = await self.execute_command(step)
                results.append(result)
                
                # Capturar screenshot después de cada paso
                screenshot = await screenshot()
                
            except Exception as e:
                # 4. Recovery
                recovery_plan = await self.gemini.recover_from_error(
                    str(e), 
                    screenshot
                )
                # Ejecutar recovery steps...
        
        return {
            "status": "success" if not results[-1].get("error") else "failed",
            "steps": results
        }
    
    async def execute_command(self, command: dict) -> dict:
        """Ejecuta un comando individual"""
        cmd_type = command["type"]
        
        if cmd_type == "mouse_click":
            return await mouse_click(command["x"], command["y"])
        elif cmd_type == "keyboard_type":
            return await keyboard_type(command["text"])
        elif cmd_type == "screenshot":
            return await screenshot()
        # ... etc
```

### Checkpoint 2: Vision Integration Test

```python
# test_phase2.py
async def test_phase2():
    """
    1. Abrir Notepad
    2. Gemini analiza screenshot
    3. Detecta campo de texto
    4. Escribe algo
    5. Verifica que se escribió
    """
```

---

## Fase 3: Gestión de Tareas (Días 11-15)

### 3.1 Task Queue (Día 11)

**Archivo**: `core/task_queue.py`

```python
import json
from pathlib import Path
from datetime import datetime

class TaskQueue:
    def __init__(self, db_path: str = "tasks/tasks.json"):
        self.db_path = Path(db_path)
        self.load_queue()
    
    def load_queue(self):
        if self.db_path.exists():
            with open(self.db_path) as f:
                self.tasks = json.load(f)
        else:
            self.tasks = []
    
    def save_queue(self):
        self.db_path.parent.mkdir(exist_ok=True)
        with open(self.db_path, 'w') as f:
            json.dump(self.tasks, f, indent=2)
    
    def add_task(self, task_data: dict) -> str:
        task_id = str(uuid.uuid4())
        task = {
            "id": task_id,
            "status": "PENDING",
            "created_at": datetime.now().isoformat(),
            **task_data
        }
        self.tasks.append(task)
        self.save_queue()
        return task_id
    
    def get_next_task(self) -> dict:
        """Retorna tarea con mayor prioridad pendiente"""
        pending = [t for t in self.tasks if t["status"] == "PENDING"]
        if pending:
            return max(pending, key=lambda t: t.get("priority", 1))
        return None
    
    def update_task(self, task_id: str, updates: dict):
        for task in self.tasks:
            if task["id"] == task_id:
                task.update(updates)
                self.save_queue()
                break
```

### 3.2 Main Loop (Días 12-13)

**Archivo**: `main.py`

```python
import asyncio
from core.state_manager import StateManager
from core.gemini_client import GeminiClient
from core.task_orchestrator import TaskOrchestrator
from core.task_queue import TaskQueue

async def main():
    # Inicializar componentes
    state_manager = StateManager()
    gemini_client = GeminiClient(api_key=os.getenv("GEMINI_API_KEY"))
    task_queue = TaskQueue()
    orchestrator = TaskOrchestrator(state_manager, gemini_client)
    
    # Iniciar monitoring de stats
    asyncio.create_task(state_manager.monitor_loop())
    
    # Main loop
    while True:
        try:
            # 1. Obtener siguiente tarea
            task = task_queue.get_next_task()
            
            if not task:
                await asyncio.sleep(5)  # Dormir si no hay tareas
                continue
            
            # 2. Verificar si el sistema está listo
            if state_manager.current_state == SystemState.OVERLOADED:
                await asyncio.sleep(10)  # Esperar si está sobrecargado
                continue
            
            # 3. Marcar como en progreso
            task_queue.update_task(task["id"], {"status": "RUNNING"})
            
            # 4. Ejecutar tarea
            result = await orchestrator.execute_task(task["description"])
            
            # 5. Guardar resultado
            task_queue.update_task(task["id"], {
                "status": "COMPLETED",
                "result": result,
                "completed_at": datetime.now().isoformat()
            })
            
        except Exception as e:
            logger.error(f"Error en main loop: {e}")
            task_queue.update_task(task["id"], {
                "status": "FAILED",
                "error": str(e)
            })
            await asyncio.sleep(5)

if __name__ == "__main__":
    asyncio.run(main())
```

### 3.3 Error Handling (Días 14-15)

**Archivo**: `core/error_handler.py`

```python
class ErrorHandler:
    @staticmethod
    async def handle_timeout(task_id: str, timeout: int):
        """Tarea tardó más de lo esperado"""
        logger.warning(f"Task {task_id} timed out after {timeout}s")
        # Opción 1: Reintentarcircuit
        # Opción 2: Cancelar
        # Opción 3: Escalar a humano
    
    @staticmethod
    async def handle_resource_error(error: str):
        """Problema de recursos (OOM, disk full, etc)"""
        # Cambiar a OVERLOADED state
        # Limpiar cache/temp
        # Reintentarwith backoff
    
    @staticmethod
    async def handle_app_crash(app_name: str):
        """Aplicación se cerró inesperadamente"""
        # Reabrir app
        # Verificar estado
        # Continuar o rollback
    
    @staticmethod
    async def handle_permission_error(path: str):
        """Permiso denegado en file operation"""
        # Intentar de diferente forma
        # Elevar privilegios si es posible
        # Log y reportar
```

### Checkpoint 3: Queue & Main Loop Test

```python
# test_phase3.py
async def test_phase3():
    """
    1. Agregar múltiples tareas a queue
    2. Main loop procesa tasks
    3. Simular errores y verificar recovery
    4. Verificar logging
    """
```

---

## Fase 4: Learning & Optimization (Días 16-20)

### 4.1 Metrics Engine (Días 16-17)

**Archivo**: `core/metrics.py`

```python
class TaskMetrics:
    task_id: str
    duration_seconds: float
    ram_peak: float
    cpu_peak: float
    api_calls: int
    screenshot_count: int
    error_count: int
    success: bool
    commands_executed: int
    
    def efficiency_score(self) -> float:
        """Calcula 0-1 score de eficiencia"""
        # Menos tiempo = mejor
        # Menos errores = mejor
        # Menos API calls = mejor
        # Menos screenshots = mejor
        pass

class MetricsEngine:
    def __init__(self, db_path: str = "tasks/metrics.json"):
        self.db_path = db_path
        self.metrics = []
    
    def record_metric(self, metric: TaskMetrics):
        self.metrics.append(metric.to_dict())
        self.save()
    
    def get_pattern(self, tasktype: str) -> dict:
        """
        Analiza histórico de tareas del mismo tipo
        Retorna patrón promedio
        """
        similar_tasks = [m for m in self.metrics if m["task_type"] == task_type]
        
        if not similar_tasks:
            return None
        
        return {
            "avg_duration": sum(m["duration"] for m in similar_tasks) / len(similar_tasks),
            "avg_errors": ...,
            "success_rate": ...,
            "commands_per_task": ...,
        }
    
    def suggest_optimizations(self) -> list:
        """
        Basado en métricas, sugiere mejoras
        """
        suggestions = []
        
        # Si alta tasa de error en ciertas acciones
        # Si tomar mucho tiempo
        # Si usar muchos recursos
        
        return suggestions
```

### 4.2 Playbook System (Días 18-19)

**Archivo**: `core/playbooks.py`

```python
class Playbook:
    """Receta de cómo completar un tipo de tarea"""
    task_type: str
    steps: List[dict]
    success_rate: float
    avg_duration: float
    last_used: datetime

class PlaybookLibrary:
    def __init__(self):
        self.playbooks = {}
    
    def save_playbook(self, task_type: str, steps: list):
        """
        Después de completar una tarea exitosamente,
        guarda secuencia de pasos como playbook
        """
        playbook = Playbook(
            task_type=task_type,
            steps=steps,
            success_rate=1.0,
            avg_duration=...
        )
        self.playbooks[task_type] = playbook
    
    def get_playbook(self, task_type: str) -> Optional[Playbook]:
        """
        Si existe playbook para este tipo de tarea,
        retorna y salta planinng con Gemini
        """
        return self.playbooks.get(task_type)
    
    def update_playbook(self, task_type: str, success: bool):
        """
        Actualiza success_rate después de ejecutar
        """
        pass
```

### 4.3 Learning Loop Integration (Día 20)

**Actualizar**: `main.py`

```python
async def main():
    # ... previous setup ...
    metrics_engine = MetricsEngine()
    playbook_library = PlaybookLibrary()
    
    while True:
        try:
            task = task_queue.get_next_task()
            if not task:
                await asyncio.sleep(5)
                continue
            
            # NUEVO: Chequear si existe playbook
            playbook = playbook_library.get_playbook(task["type"])
            
            if playbook:
                # Saltarse Gemini planning, usar playbook directo
                result = await orchestrator.execute_playbook(playbook, task)
            else:
                # Usar Gemini para generar plan
                result = await orchestrator.execute_task(task)
            
            # NUEVO: Guardar métricas
            metrics = TaskMetrics(
                task_id=task["id"],
                duration_seconds=result["duration"],
                # ... otros metrics ...
            )
            metrics_engine.record_metric(metrics)
            
            # NUEVO: Si exitoso y es nueva tarea type, guardar playbook
            if result["success"] and not playbook:
                playbook_library.save_playbook(
                    task["type"],
                    result["steps"]
                )
            
            task_queue.update_task(task["id"], {
                "status": "COMPLETED",
                "result": result
            })
            
        except Exception as e:
            logger.error(f"Error: {e}")
```

### Checkpoint 4: Learning Loop Test

```python
# test_phase4.py
async def test_phase4():
    """
    1. Completar tarea tipo X → Guardar como playbook
    2. Nueva tarea tipo X → Usar playbook (sin Gemini)
    3. Verificar que segunda tarea fue más rápida
    4. Verificar métricas registradas
    """
```

---

## Fase 5: API & Dashboard (Días 21-25)

### 5.1 FastAPI Setup (Día 21)

**Archivo**: `api/app.py`

```python
from fastapi import FastAPI, Depends, Header, HTTPException
from fastapi.responses import JSONResponse

app = FastAPI(title="SynapseOS API", version="1.0.0")

# Middleware de autenticación
async def verify_api_key(x_api_key: str = Header(...)) -> str:
    if x_api_key not in os.getenv("VALID_API_KEYS", "").split(","):
        raise HTTPException(status_code=401, detail="Invalid API key")
    return x_api_key

@app.post("/api/v1/tasks")
async def submit_task(
    task_data: dict,
    api_key: str = Depends(verify_api_key)
):
    """Crea nueva tarea"""
    task_id = task_queue.add_task({
        **task_data,
        "client_id": api_key,
        "priority": task_data.get("priority", 5)
    })
    return {"task_id": task_id, "status": "queued"}

@app.get("/api/v1/tasks/{task_id}")
async def get_task_status(task_id: str, api_key: str = Depends(verify_api_key)):
    """Estado de una tarea"""
    task = task_queue.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@app.get("/api/v1/tasks/{task_id}/result")
async def get_task_result(task_id: str, api_key: str = Depends(verify_api_key)):
    """Resultado de tarea completada"""
    task = task_queue.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    if task["status"] != "COMPLETED":
        raise HTTPException(status_code=409, detail="Task not completed yet")
    return task["result"]

@app.get("/api/v1/metrics")
async def get_metrics(api_key: str = Depends(verify_api_key)):
    """Estadísticas del sistema"""
    return {
        "tasks_completed": len([t for t in task_queue.tasks if t["status"] == "COMPLETED"]),
        "tasks_failed": len([t for t in task_queue.tasks if t["status"] == "FAILED"]),
        "avg_duration": metrics_engine.get_avg_duration(),
        "current_state": state_manager.current_state.value
    }
```

**Dependencies**:
- `pip install fastapi uvicorn`

### 5.2 OAuth Integration (Días 22-23)

```python
# Mediante library de Codex OAuth
# (Depende de qué OAuth provider uses)

# Ejemplo con OAuth2PasswordBearer:
from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

@app.post("/token")
async def login(username: str, password: str):
    # Validar credenciales
    # Retornar JWT token
    pass

async def verify_token(token: str = Depends(oauth2_scheme)) -> str:
    # Validar JWT
    # Retornar user_id
    pass
```

### 5.3 Dashboard Frontend (Día 24)

**Archivo**: `api/static/index.html`

```html
<!DOCTYPE html>
<html>
<head>
    <title>SynapseOS Dashboard</title>
    <style>
        body { font-family: monospace; background: #0a0e27; color: #00ff00; }
        .container { max-width: 1200px; margin: auto; padding: 20px; }
        .metric { display: inline-block; width: 23%; margin: 1%; padding: 20px; 
                  background: #1a1f3a; border: 1px solid #00ff00; }
        .task-list { margin-top: 40px; }
        .task { padding: 10px; margin: 5px; background: #1a1f3a; }
        .success { color: #00ff00; }
        .failed { color: #ff0000; }
        .pending { color: #ffff00; }
    </style>
</head>
<body>
    <div class="container">
        <h1>SynapseOS Dashboard</h1>
        
        <div id="metrics">
            <div class="metric">
                <h3>Tasks Completed</h3>
                <p id="completed">0</p>
            </div>
            <div class="metric">
                <h3>Tasks Failed</h3>
                <p id="failed">0</p>
            </div>
            <div class="metric">
                <h3>Avg Duration</h3>
                <p id="avg-duration">0s</p>
            </div>
            <div class="metric">
                <h3>System State</h3>
                <p id="system-state">IDLE</p>
            </div>
        </div>
        
        <div class="task-list">
            <h2>Recent Tasks</h2>
            <div id="tasks"></div>
        </div>
    </div>
    
    <script>
        async function updateMetrics() {
            const response = await fetch('/api/v1/metrics', {
                headers: { 'X-API-Key': localStorage.getItem('api_key') }
            });
            const data = await response.json();
            
            document.getElementById('completed').textContent = data.tasks_completed;
            document.getElementById('failed').textContent = data.tasks_failed;
            document.getElementById('avg-duration').textContent = data.avg_duration.toFixed(2) + 's';
            document.getElementById('system-state').textContent = data.current_state;
        }
        
        setInterval(updateMetrics, 5000);
        updateMetrics();
    </script>
</body>
</html>
```

**Servir estáticos**:
```python
from fastapi.staticfiles import StaticFiles

app.mount("/", StaticFiles(directory="api/static", html=True), name="static")
```

### 5.4 Server Runner (Día 25)

**Archivo**: `run_server.py`

```python
import uvicorn
import asyncio

async def run():
    # Iniciar main loop en background
    asyncio.create_task(main())
    
    # Iniciar servidor
    config = uvicorn.Config(
        app="api.app:app",
        host="127.0.0.1",
        port=8000,
        reload=False
    )
    server = uvicorn.Server(config)
    await server.serve()

if __name__ == "__main__":
    asyncio.run(run())
```

### Checkpoint 5: Full Integration Test

```python
# test_phase5.py
async def test_phase5():
    """
    1. Iniciar servidor
    2. Submit task via API
    3. Check status
    4. Get result
    5. Verify metrics updated
    """
```

---

## Pruebas & QA (Días 26-30)

### Test Suite Completo

```
tests/
├── unit/
│   ├── test_state_manager.py
│   ├── test_gemini_client.py
│   ├── test_abilities.py
│   └── test_metrics.py
├── integration/
│   ├── test_full_workflow.py
│   ├── test_error_handling.py
│   └── test_api.py
└── performance/
    ├── test_concurrent_tasks.py
    └── test_resource_usage.py
```

### CI/CD Setup

```yaml
# .github/workflows/test.yml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: windows-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
      - run: pip install -r requirements.txt
      - run: pytest tests/
```

---

## Timeline Resumen

| Fase | Duración | Hito |
|------|----------|------|
| 0 | 1 día | Setup inicial |
| 1 | 5 días | Core + abilities básicas |
| 2 | 5 días | Vision & OCR |
| 3 | 5 días | Queue + main loop |
| 4 | 5 días | Learning & optimization |
| 5 | 5 días | API + Dashboard |
| QA | 5 días | Testing + optimizaciones |
| **Total** | **~30 días** | **Sistema en producción** |

---

## Dependencias Python

```
# requirements.txt
google-generativeai>=0.3.0
pyautogui>=0.9.53
pygetwindow>=0.0.9
pillow>=9.0.0
pytesseract>=0.3.10
fastapi>=0.95.0
uvicorn>=0.21.0
python-dotenv>=0.21.0
sqlalchemy>=2.0.0
pytest>=7.0.0
httpx>=0.23.0
pydantic>=1.9.0
```

---

## Checklist Final

- [ ] Fase 1 completada y testeada
- [ ] Fase 2 completada y testeada
- [ ] Fase 3 completada y testeada
- [ ] Fase 4 completada y testeada
- [ ] Fase 5 completada y testeada
- [ ] Suite de tests en verde
- [ ] Documentación actualizada
- [ ] .env.example creado
- [ ] README con instrucciones de inicio
- [ ] Deployment instructions ready

