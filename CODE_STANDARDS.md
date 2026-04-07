# Code Standards - SynapseOS

## Objetivo

Mantener un código limpio, consistente y fácil de mantener.

---

## 🐍 Python Coding Standards

### 1. Nombre de Variables

```python
# ✅ Good
user_email = "user@example.com"
max_retries = 5
is_active = True
task_queue = []

# ❌ Bad
userEmail = "user@example.com"  # No camelCase
mr = 5  # No obscuro
active = True  # Sin prefijo para booleans
q = []  # Demasiado corto
```

### 2. Type Hints (Obligatorio)

```python
# ✅ Good
def process_task(task: dict, timeout: int) -> bool:
    """Process a single task."""
    pass

async def get_screenshot() -> bytes:
    """Capture and return screenshot."""
    pass

# ❌ Bad
def process_task(task, timeout):  # Sin types
    pass
```

### 3. Docstrings (Google Style)

```python
# ✅ Good
def calculate_efficiency(metrics: TaskMetrics) -> float:
    """
    Calculate task execution efficiency score.
    
    Analyzes multiple metrics to produce a 0-1 efficiency score.
    Higher values indicate better performance.
    
    Args:
        metrics: TaskMetrics object with timing and resource data
        
    Returns:
        Efficiency score between 0 and 1
        
    Raises:
        ValueError: If metrics are invalid or negative
        
    Example:
        >>> metrics = TaskMetrics(duration=10, errors=0)
        >>> score = calculate_efficiency(metrics)
        >>> print(f"Efficiency: {score:.2%}")
        Efficiency: 95.00%
    """
    pass

# ❌ Bad
def calculate_efficiency(metrics):
    # Calcula eficiencia
    return 0.5
```

### 4. Async/Await

```python
# ✅ Good
async def execute_task(task_id: str) -> dict:
    """Execute task asynchronously."""
    result = await self.orchestrator.process(task_id)
    return result

# ❌ Bad
def execute_task(task_id):  # No async
    return orchestrator.process(task_id)
```

### 5. Error Handling

```python
# ✅ Good
try:
    result = await mouse_click(x, y)
except TimeoutError:
    logger.error(f"Mouse click timeout at ({x}, {y})")
    result = await self.recover_from_timeout()
except Exception as e:
    logger.exception(f"Unexpected error: {e}")
    raise

# ❌ Bad
try:
    result = await mouse_click(x, y)
except Exception:  # Demasiado genérico
    pass  # Silent fail
```

### 6. Longitud de Línea

Max: **100 caracteres**

```python
# ✅ Good
very_long_function_call(
    parameter_one=value1,
    parameter_two=value2,
    parameter_three=value3
)

# ❌ Bad
very_long_function_call(parameter_one=value1, parameter_two=value2, parameter_three=value3)
```

### 7. Imports

```python
# ✅ Good
import os
import logging
from typing import Optional, Dict, List
from core.state_manager import StateManager
from abilities.input_control import mouse_click

# ❌ Bad
from *  # Never do this
import os, sys, logging  # Separados
```

### 8. Constants

```python
# ✅ Good - en config/settings.py
MAX_CONCURRENT_TASKS = 5
MAX_RAM_USAGE = 0.85
TASK_TIMEOUT_SECONDS = 300

# Usage
tasks = [task for task in queue if count < MAX_CONCURRENT_TASKS]

# ❌ Bad
if count < 5:  # Magic numbers
    pass
```

### 9. Classes

```python
# ✅ Good
class TaskMetrics:
    """Container for task performance metrics."""
    
    def __init__(self, task_id: str, duration: float):
        """Initialize metrics."""
        self.task_id = task_id
        self.duration = duration
    
    def efficiency_score(self) -> float:
        """Calculate efficiency 0-1."""
        return max(0, min(1, 100 / self.duration))

# ❌ Bad
class task_metrics:  # Lowercase
    def __init__(self, task_id, duration):
        self.tid = task_id  # Abbreviation
```

### 10. Logging

```python
# ✅ Good
import logging

logger = logging.getLogger(__name__)

logger.info("Task started", extra={"task_id": task_id})
logger.warning(f"Retry attempt {retry_count}")
logger.error(f"Failed to execute task: {error}", exc_info=True)

# ❌ Bad
print("Task started")  # Nunca print
logging.info("Task startes")  # Typo
logger.error("Error: " + str(error))  # String concat
```

---

## 🧪 Testing Standards

### 1. Test File Structure

```
tests/
├── unit/
│   └── test_state_manager.py
├── integration/
│   └── test_full_workflow.py
└── performance/
    └── test_concurrent_tasks.py
```

### 2. Test Naming

```python
# ✅ Good
def test_state_transition_from_idle_to_working():
    """Test that system transitions from IDLE to WORKING."""
    pass

@pytest.mark.asyncio
async def test_gemini_client_error_handling():
    """Test Gemini client handles API errors gracefully."""
    pass

# ❌ Bad
def test_state():  # Too vague
    pass

def test1():  # Non-descriptive
    pass
```

### 3. Test Structure

```python
# ✅ Good - Arrange, Act, Assert
@pytest.mark.asyncio
async def test_mouse_click_success():
    """Test successful mouse click."""
    # Arrange
    x, y = 100, 200
    
    # Act
    result = await mouse_click(x, y)
    
    # Assert
    assert result["status"] == "success"
    assert result["x"] == x
    assert result["y"] == y
```

### 4. Mocking

```python
# ✅ Good
@pytest.fixture
def mock_gemini(mocker):
    """Fixture for mocked Gemini client."""
    mock = mocker.AsyncMock()
    mock.analyze_screenshot.return_value = {"text": "Hello"}
    return mock

@pytest.mark.asyncio
async def test_with_mock(mock_gemini):
    """Test using mocked Gemini."""
    client = GeminiClient(api_key="test")
    # Replace real client with mock
    client.analyze_screenshot = mock_gemini.analyze_screenshot
```

### 5. Coverage

```bash
# Min 85% coverage
pytest tests/ --cov=core --cov=abilities --cov-report=term-missing

# HTML report
pytest tests/ --cov --cov-report=html
# Open htmlcov/index.html
```

---

## 📝 Documentation Standards

### 1. README Sections

✅ Include:
- Description
- Quick Start
- Architecture diagram
- Roadmap
- Contributing

### 2. Code Comments

```python
# ✅ Good - Explain WHY not WHAT
# If CPU usage exceeds 80%, shift to THINKING state
# to preserve system stability
if cpu_usage > 0.80:
    await state_manager.transition_to(SystemState.THINKING)

# ❌ Bad - Obvious what code does
# Set cpu_usage to value
cpu_usage = psutil.cpu_percent()
```

### 3. CHANGELOG

```
## [0.2.0] - 2026-04-15

### Added
- OCR support for screenshot analysis
- Playbook system for task templates

### Fixed
- Memory leak in screenshot processing
- State transition race condition

### Changed
- Increased max concurrent tasks to 5
```

---

## 🎯 Best Practices

### Performance

```python
# ✅ Good - Lazy evaluation
def get_high_priority_tasks() -> Iterator[Task]:
    """Yield tasks in priority order."""
    for task in self.queue:
        if task.priority > 5:
            yield task

# ❌ Bad - Loads entire list into memory
def get_high_priority_tasks() -> List[Task]:
    return [task for task in self.queue if task.priority > 5]
```

### Security

```python
# ✅ Good
import os
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("GEMINI_API_KEY not set")

# ❌ Bad
api_key = "AIza..."  # Hardcoded!
```

### Async Best Practices

```python
# ✅ Good - Concurrent tasks
tasks = [process_task(t) for t in task_list]
results = await asyncio.gather(*tasks)

# ❌ Bad - Sequential
results = []
for task in task_list:
    result = await process_task(task)
    results.append(result)
```

---

## 🔍 Pre-commit Checklist

- [ ] Seguir naming conventions
- [ ] Type hints en todas las funciones
- [ ] Docstrings en funciones públicas
- [ ] Tests añadidos/actualizados
- [ ] Coverage ≥ 85%
- [ ] No hardcoded secrets
- [ ] Logs en lugar de prints
- [ ] Manejo de errores adecuado
- [ ] Commits descriptivos

---

## 📚 References

- [PEP 8](https://www.python.org/dev/peps/pep-0008/)
- [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html)
- [Async Best Practices](https://docs.python.org/3/library/asyncio-dev.html)
- [Type Hints](https://docs.python.org/3/library/typing.html)

