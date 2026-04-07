# Getting Started with SynapseOS

## 1. Setup

### Clone & Install
```bash
cd C:\Users\Jack\Documents\GitHub\Experimentos\SynapseOS
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### Environment Variables
```bash
# Copy example env
copy .env.example .env

# Edit .env with your keys
# Set GEMINI_API_KEY from Google AI Console
```

## 2. First Run

### Phase 1 (Current - Core Base)
```bash
# Soon: python main.py
```

This will:
- Initialize State Manager (monitoring CPU/RAM)
- Connect to Gemini API
- Setup ability system
- Start main event loop


## 3. Architecture Overview

```
┌─────────┐
│  Tasks  │
│ (API)   │
└────┬────┘
     │
┌────▼──────────┐
│   QUEUE       │ ← Tareas pendientes
└────┬──────────┘
     │
┌────▼────────────────┐
│  STATE MANAGER      │ ← Monitorea CPU/RAM/DISK
│  (idle/working/     │
│   thinking/overload)│
└────┬────────────────┘
     │
┌────▼─────────────┐
│  GEMINI          │ ← Razonamiento & decisiones
│  (Multi-modal)   │
└────┬─────────────┘
     │
┌────▼──────────────────────┐
│  ABILITIES                │ ← 100+ habilidades
│  - Mouse/Keyboard         │
│  - Window Mgmt            │
│  - File Operations        │
│  - Vision/OCR             │
│  - System Monitor         │
└────┬──────────────────────┘
     │
┌────▼────────────┐
│  WINDOWS SYSTEM │
└─────────────────┘
```

## 4. Quick Tutorial

### (After Phase 1 is ready)

```python
# Example 1: Submit a task via API
import requests

response = requests.post("http://localhost:8000/api/v1/tasks", 
    json={
        "description": "Abrir Notepad y escribir hola mundo",
        "priority": 5
    },
    headers={"X-API-Key": "your_key"}
)

task_id = response.json()["task_id"]
print(f"Task submitted: {task_id}")

# Example 2: Check status
response = requests.get(f"http://localhost:8000/api/v1/tasks/{task_id}",
    headers={"X-API-Key": "your_key"}
)
print(response.json())

# Example 3: Get result
response = requests.get(f"http://localhost:8000/api/v1/tasks/{task_id}/result",
    headers={"X-API-Key": "your_key"}
)
print(response.json()["result"])
```

## 5. Development Workflow

### Testing Phases
Each phase has checkpoints:

```
Phase 1 Checkpoint:
- test_phase1.py
- Verifies state transitions
- Verifies Ability executions
- Integration: Notepad test

Phase 2 Checkpoint:
- test_phase2.py
- Verifies Vision/OCR
- Gemini screenshot analysis
- Visual element detection

... etc
```

Run tests:
```bash
pytest tests/ -v
```

### Running Individual Tests
```bash
# Test state manager
pytest tests/unit/test_state_manager.py -v

# Test API
pytest tests/integration/test_api.py -v

# Test full workflow
pytest tests/integration/test_full_workflow.py -v
```

## 6. Current Status

### ✅ Done
- Project structure created
- Documentation (README, ARCHITECTURE, PROJECT_PLAN)
- Configuration system
- Main entry point skeleton

### 🚧 In Progress
- Phase 1: Core Base
  - State Manager
  - Gemini Client
  - Input Control
  - Window Management
  - App Launcher

### 📋 TODO
- Phase 2-5 (See PROJECT_PLAN.md)

## 7. Monitoring & Debugging

### View Logs
```bash
# Real-time logs
tail -f logs/system.log

# Or open in editor
code logs/system.log
```

### Dashboard
(After Phase 5)
```bash
# Visit dashboard at:
http://localhost:8000
```

## 8. Common Issues

### "GEMINI_API_KEY not found"
- Make sure `.env` file exists
- Check that `GEMINI_API_KEY` is set correctly
- Verify API key is valid at https://ai.google.dev/

### "ModuleNotFoundError: No module named 'google'"
```bash
# Reinstall dependencies
pip install -r requirements.txt
```

### "Port 8000 already in use"
```bash
# Change in .env
API_PORT=8001
```

## 9. Next Steps

1. **Phase 1**: Implement State Manager (EST: 1 day)
   - See PROJECT_PLAN.md, Section "Fase 1: Core Base (Days 1-5)"

2. **Phase 2**: Add Vision capabilities

3. **Integrate with clients**: Deploy API

## 10. Resources

- [Google Gemini API Docs](https://ai.google.dev/docs)
- [PyAutoGUI Docs](https://pyautogui.readthedocs.io/)
- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [Architecture Doc](ARCHITECTURE.md)
- [Project Plan](PROJECT_PLAN.md)

---

**Questions?** Check ARCHITECTURE.md for technical details or PROJECT_PLAN.md for implementation roadmap.
