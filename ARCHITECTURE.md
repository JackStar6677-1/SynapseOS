# SynapseOS - Arquitectura Técnica Detallada

## 1. Componentes Principales

### 1.1 State Manager (core/state_manager.py)

Máquina de estados que controla el comportamiento del sistema según recursos disponibles.

```python
class SystemState(Enum):
    IDLE = "idle"           # Sin tareas, recursos mínimos
    WORKING = "working"     # Ejecutando tareas normales
    THINKING = "thinking"   # Razonamiento profundo, mayor uso de Gemini
    OVERLOADED = "overloaded"  # CPU/RAM críticos, modo seguro

class ResourceLimits:
    MAX_CONCURRENT_TASKS = 5
    MAX_RAM_USAGE = 0.85  # 85%
    MAX_CPU_USAGE = 0.80  # 80%
    MAX_DISK_TEMP = 85    # Celsius
    TIMEOUT_PER_TASK = 300  # segundos
    MAX_API_CALLS_PER_MIN = 60
```

**Responsabilidades:**
- Monitorear recursos del sistema continuamente
- Transicionar entre estados según condiciones
- Limitar concurrencia de tareas en estado OVERLOADED
- Notificar cambios de estado

### 1.2 Task Orchestrator (core/task_orchestrator.py)

Procesa la cola de tareas y coordina la ejecución.

```python
class Task:
    id: str
    client_id: str
    description: str
    priority: int (1-10)
    created_at: datetime
    timeout: int = 300
    status: TaskStatus = PENDING
    result: Optional[dict] = None
    error: Optional[str] = None

class TaskOrchestrator:
    def process_queue(self):
        # Loop principal que:
        # 1. Extrae tarea de cola según prioridad
        # 2. Verifica estado del sistema
        # 3. Genera plan de ejecución con Gemini
        # 4. Ejecuta abilities en secuencia
        # 5. Captura resultado
        # 6. Guarda métricas
```

**Flujo:**
```
1. RECEIVE TASK
   ↓
2. VALIDATE & ENQUEUE
   ↓
3. WAIT FOR SYSTEM IDLE
   ↓
4. ASK GEMINI FOR PLAN
   ↓
5. EXECUTE ABILITIES SEQUENTIALLY
   - Capture screenshot after each step
   - Check for errors
   - Retry if needed
   ↓
6. RETURN RESULT TO CLIENT
   ↓
7. RECORD METRICS FOR LEARNING
```

### 1.3 Gemini Client (core/gemini_client.py)

Cliente de la API de Gemini con context caching y multi-modal support.

```python
class GeminiClient:
    def __init__(self, api_key: str):
        self.client = genai.Client(api_key=api_key)
        self.model = "gemini-2.0-pro-vision"
        self.cache_threshold = 60 * 60  # 1 hora
    
    async def analyze_screenshot(self, image_bytes: bytes) -> str:
        """Usa vision de Gemini para entender pantalla actual"""
        
    async def generate_plan(self, task: str, current_state: dict) -> List[str]:
        """Genera secuencia de comandos para ejecutar"""
        
    async def error_recovery(self, error: str, screenshot: bytes) -> List[str]:
        """Propone pasos para recuperarse de error"""
```

**System Prompt para Gemini:**

```
Eres un agente operativo autónomo especializado en ejecutar tareas en Windows.

INSTRUCCIONES CRÍTICAS:
1. NO eres chatbot - solo respondes cuando se te da orden
2. Analiza SIEMPRE el estado actual ANTES de actuar
3. Genera secuencia exacta de COMANDOS (no descripción)
4. Ejecuta paso a paso
5. Si hay error, diagnostica automáticamente
6. Reporta solo: ÉXITO/FALLO + RESULTADO

FORMATO DE RESPUESTA:
[PLAN]
1. mouse_click(100, 200)
2. keyboard_type("searchterm")
3. keyboard_hotkey("Enter")
4. screenshot()
[END_PLAN]

ESTADO ACTUAL:
- RAM: {ram}%
- CPU: {cpu}%
- Ventanas: {windows}
- Pantalla: [screenshot_actual]

TAREA: {task_description}

ACTÚA AHORA.
```

### 1.4 Metrics Engine (core/metrics.py)

Recolecta datos de desempeño para optimización continua.

```python
class TaskMetrics:
    task_id: str
    duration_seconds: float
    ram_peak: float
    cpu_peak: float
    api_calls: int
    screenshot_count: int
    error_count: int
    retry_count: int
    success: bool
    
class LearningEngine:
    def calculate_efficiency(self, metrics: TaskMetrics) -> float:
        """Calcula puntuación de eficiencia (0-1)"""
        
    def identify_patterns(self, task_type: str) -> dict:
        """Identifica patrones en tareas del mismo tipo"""
        
    def suggest_optimizations(self, metrics: List[TaskMetrics]) -> List[str]:
        """Sugiere mejoras basadas en historial"""
```

---

## 2. Abilities Layer (100+ Habilidades)

Funciones que Gemini puede llamar para controlar la PC.

### 2.1 Input Control (abilities/input_control.py)

```python
async def mouse_move(x: int, y: int, speed: float = 1.0) -> dict:
    """Mueve mouse con trayectoria calculada (no lineal)"""
    # Calcula puntos intermedios para movimiento suave
    # Adapta velocidad según distancia
    
async def mouse_click(x: int, y: int, button: str = "left") -> dict:
    """Click, doble-click, click-derecha"""
    
async def keyboard_type(text: str, interval: float = 0.05) -> dict:
    """Escribe texto con intervalo entre caracteres"""
    
async def keyboard_hotkey(*keys: str) -> dict:
    """Ejecuta combinación de teclas (Ctrl+C, Alt+Tab, etc)"""
    
async def screenshot() -> bytes:
    """Captura pantalla actual como PNG"""
    
async def screenshot_region(x1, y1, x2, y2) -> bytes:
    """Captura región específica de pantalla"""
```

### 2.2 Window Management (abilities/window_management.py)

```python
async def get_active_window() -> dict:
    """Retorna nombre, PID, posición de ventana activa"""
    
async def list_windows() -> List[dict]:
    """Lista todas las ventanas abiertas"""
    
async def activate_window(window_name: str) -> bool:
    """Trae ventana al frente"""
    
async def get_window_elements(window_name: str) -> List[dict]:
    """Obtiene botones, campos de texto, etc. detectados por accesibilidad"""
    
async def close_window(window_name: str) -> bool:
    """Cierra ventana de forma segura"""
    
async def wait_for_window(window_name: str, timeout: int = 10) -> bool:
    """Espera a que una ventana aparezca"""
```

### 2.3 File Operations (abilities/file_operations.py)

```python
async def read_file(path: str) -> str:
    """Lee contenido de archivo (auto-detecta encoding)"""
    
async def write_file(path: str, content: str, mode: str = "w") -> bool:
    """Escribe contenido en archivo"""
    
async def list_dir(path: str, recursive: bool = False) -> List[dict]:
    """Lista archivos en directorio"""
    
async def copy_file(from_path: str, to_path: str) -> bool:
    """Copia archivo"""
    
async def move_file(from_path: str, to_path: str) -> bool:
    """Mueve/renombra archivo"""
    
async def parse_file(path: str, format: str) -> dict:
    """Parsed automático de CSV, JSON, Excel, PDF"""
    
async def create_folder(path: str) -> bool:
    """Crea carpeta recursivamente"""
```

### 2.4 Application Launcher (abilities/app_launcher.py)

```python
async def launch_app(app_name: str, args: List[str] = []) -> dict:
    """Abre aplicación y retorna PID"""
    # Busca en PATH, Program Files, Start Menu
    
async def close_app(app_name: str, force: bool = False) -> bool:
    """Cierra aplicación - fuerza si es necesario"""
    
async def is_app_running(app_name: str) -> bool:
    """Verifica si aplicación está corriendo"""
    
async def get_clipboard() -> str:
    """Lee contenido del clipboard"""
    
async def set_clipboard(text: str) -> bool:
    """Escribe en clipboard"""
```

### 2.5 Visual Recognition (abilities/vision.py)

```python
async def ocr_screen() -> dict:
    """Lee TODO el texto visible en pantalla con posiciones"""
    
async def detect_button(text: str, screenshot: bytes = None) -> Tuple[int, int]:
    """Encuentra botón por texto y retorna coordenadas"""
    
async def detect_element(description: str) -> Optional[Tuple[int, int]]:
    """Encuentra elemento por descripción visual (usa Gemini vision)"""
    
async def find_color(color_hex: str) -> Optional[Tuple[int, int]]:
    """Encuentra pixel del color especificado"""
    
async def check_error_dialog() -> Optional[str]:
    """Detecta si hay diálogo de error y extrae mensaje"""
```

### 2.6 System Monitor (abilities/system_monitor.py)

```python
async def get_system_metrics() -> dict:
    """
    Retorna {
        'cpu': float,           # 0-100%
        'ram': float,           # 0-100%
        'disk': float,          # 0-100%
        'disk_temp': int,       # Celsius
        'network': {
            'bytes_in': int,
            'bytes_out': int,
            'latency_ms': int
        }
    }
    """
    
async def get_running_services() -> List[dict]:
    """Lista procesos activos con recursos usados"""
    
async def get_available_space() -> dict:
    """Espacio disponible en discos"""
    
async def ping_network() -> dict:
    """Verifica conectividad"""
    
async def get_current_time() -> datetime:
    """Hora sincronizada del sistema"""
```

---

## 3. Learning & Optimization Loop

### Fase 1: Recolección de Dados
Cada tarea completada registra:
- Tiempo de ejecución
- Recursos utilizados
- Errores encontrados
- Pasos realizados

### Fase 2: Análisis de Patrones
```python
def analyze_patterns(task_type: str, history: List[TaskMetrics]) -> dict:
    """
    Identifica patrones en ejecuciones pasadas:
    - Orden óptimo de abrir aplicaciones
    - Trayectorias eficientes de mouse
    - Tiempos de espera ideales
    - Errores comunes y su solución
    """
```

### Fase 3: Auto-Optimización
```python
optimizations = [
    "Abrir aplicaciones en orden decreciente de tiempo de inicio",
    "Pre-calcular trayectorias de mouse más ineficientes",
    "Reducir delays entre acciones en tareas repetidas",
    "Aumentar agresividad de multitask si recursos lo permiten",
    "Usar modo THINKING menos para tareas conocidas",
]
```

---

## 4. API & Integration

### 4.1 Task Submission API (FastAPI)

```python
@app.post("/api/v1/tasks")
async def submit_task(
    task: TaskRequest,
    x_api_key: str = Header(...)
):
    """
    Recibe tarea de cliente autenticado vía OAuth
    """
    
@app.get("/api/v1/tasks/{task_id}")
async def get_task_status(task_id: str):
    """
    Retorna estado de tarea
    """
    
@app.get("/api/v1/tasks/{task_id}/result")
async def get_task_result(task_id: str):
    """
    Retorna resultado cuando está completa
    """
```

### 4.2 OAuth Integration

```
Client → Codex OAuth Server
  ↓
  └─→ Obtiene token JWT
      ↓
      └─→ Usa token para acceder a /api/v1/tasks
          ↓
          └─→ SynapseOS valida en backend
```

---

## 5. Configuración de Recursos

### 5.1 Estado IDLE
- CPU: ~5%
- RAM: ~200MB
- GPU: 0%
- Tareas en paralelo: 0

### 5.2 Estado WORKING
- CPU: ~40-60%
- RAM: ~2-4GB
- Tareas en paralelo: 2-3

### 5.3 Estado THINKING
- CPU: ~70-80%
- RAM: ~5-6GB
- Tareas en paralelo: 2

### 5.4 Estado OVERLOADED
- CPU: 80%+ (throttled)
- RAM: 85%+ (con swap)
- Tareas en paralelo: 1
- Acciones: Slower, sin multitask, priori estabilidad

---

## 6. Error Handling & Recovery

```python
class ErrorRecoveryStrategy:
    
    @staticmethod
    async def handle_timeout(task_id: str):
        """Tarea tardó más de lo permitido - reintenta o cancela"""
        
    @staticmethod
    async def handle_access_denied(path: str):
        """Intentar diferentes estrategias: UAC, cambiar carpeta, etc"""
        
    @staticmethod
    async def handle_app_crash(app_name: str):
        """Reabrir app, esperar, validar estado"""
        
    @staticmethod
    async def handle_oom(task_id: str):
        """Cambiar a OVERLOADED, sacrificar no-esencial, reintenta"""
        
    @staticmethod
    async def handle_network_error():
        """Retry con backoff exponencial, usar resultado en caché"""
```

---

## 7. Roadmap Técnico

| Semana | Objetivos |
|--------|-----------|
| 1 | State Manager, Gemini Client, 20 abilities básicas |
| 2 | Vision/OCR, Task Queue, Task Orchestrator |
| 3 | Error handling, Timeout management |
| 4 | Metrics engine, Learning loop, Optimizaciones |
| 5 | FastAPI, OAuth, Dashboard |
| 6-8 | Testing, Escalabilidad, Documentación |

