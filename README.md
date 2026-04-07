# 🧠 SynapseOS
### *Autonomous AI Operating Agent powered by Multiple AI Providers*

<div align="center">

![Version](https://img.shields.io/badge/version-0.1.0-blue)
![Python](https://img.shields.io/badge/python-3.10+-green)
![License](https://img.shields.io/badge/license-MIT-orange)
![Status](https://img.shields.io/badge/status-In%20Development-yellow)

[📖 Docs](#-dokumentacin) • [🚀 Quick Start](#-quick-start) • [🏗️ Architecture](#-arquitectura) • [📊 Roadmap](#-roadmap) • [🤝 Contribute](#-contribute)

</div>

---

## 📋 Descripción

**SynapseOS** es un sistema operativo autónomo que puede **adoptar múltiples proveedores de IA** para convertirse en una "trabajadora IA" capaz de:

✅ **Multi-Provider AI**: Soporta Google Gemini, OpenAI Codex, y puede extenderse a otros proveedores  
✅ Recibir y procesar tareas complejas desde clientes vía API  
✅ Controlar independientemente una computadora Windows  
✅ Tomar decisiones basadas en análisis visual de pantalla (OCR, Vision)  
✅ Resolver problemas automáticamente y recuperarse de errores  
✅ **Aprender** y optimizar su desempeño con experiencia  
✅ Gestionar recursos inteligentemente (CPU, RAM, Disk)  
✅ Generar ingresos procesando trabajos reales  

> 🎬 **Inspirado en**: Proyecto de IA operativa donde múltiples proveedores de IA se convierten en asistentes autónomos que trabajan en vivo.

### ⚡ Características Clave

| Característica | Descripción |
|---|---|
| **Multi-Provider AI** | Soporta Google Gemini, OpenAI Codex, y extensible a otros proveedores |
| **Provider Adoption** | Puede cambiar dinámicamente entre proveedores de IA según necesidades |
| **Autonomous Adoption** | El sistema decide qué proveedor usar basado en tarea y disponibilidad |
| **Multimodal** | Procesa texto, imágenes y análisis visual simultáneamente |
| **State-Aware** | Adapta comportamiento según estado del sistema real |
| **Self-Learning** | Mejora con experiencia, crea playbooks automáticos |
| **Fault Tolerant** | Maneja errores, reintenta, escala inteligentemente |
| **Cost Optimized** | Minimiza llamadas API mediante context caching (50% off) |
| **Scalable** | Arquitectura preparada para múltiples instancias |

### 🔧 Funcionalidades Avanzadas

SynapseOS incorpora funcionalidades avanzadas inspiradas en sistemas de IA autónomos:

- **🤖 Sistema Multi-Provider AI**: Soporte para Google Gemini, OpenAI Codex, extensible a otros proveedores
- **🔄 Provider Adoption Dinámica**: Cambio automático entre proveedores según disponibilidad y tarea
- **🧠 Sistema de Memoria Persistente**: Almacenamiento SQLite con logs diarios y memoria a largo plazo
- **🔐 Autenticación OAuth**: Integración segura con OpenAI Codex usando PKCE
- **🆔 Identidad de Dispositivo**: Claves criptográficas Ed25519 para identificación única
- **🎯 Sistema de Skills Modulares**: Arquitectura extensible de habilidades (PC control, TTS, OCR, etc.)
- **📝 Text-to-Speech**: Síntesis de voz natural para comunicación
- **## 🎭 Sistema Multi-Provider AI

SynapseOS puede **adoptar múltiples proveedores de IA** y cambiar entre ellos dinámicamente según las necesidades:

### Proveedores Soportados

| Proveedor | Estado | Autenticación | Uso |
|-----------|--------|---------------|-----|
| **Google Gemini** | ✅ Disponible | API Key | Tareas generales, creatividad |
| **OpenAI Codex** | 🔄 Próximamente | OAuth 2.0 | Programación, análisis técnico |
| **Otros** | 🔄 Extensible | Según proveedor | Tareas especializadas |

### Adopción Dinámica

```python
from main import SynapseOS

system = SynapseOS()
await system.initialize()

# Ver proveedores disponibles
providers = system.ai_manager.list_available_providers()
print(f"Available: {providers}")

# Adoptar un proveedor específico
await system.adopt_ai_provider("gemini")

# Generar texto con el proveedor actual
response = await system.generate_text("Hello, what can you do?")

# O especificar proveedor para una tarea específica
response = await system.generate_text("Explain Python async/await", provider="openai-codex")
```

### Selección Inteligente

El sistema puede seleccionar automáticamente el mejor proveedor según:
- **Tipo de tarea**: Creatividad → Gemini, Programación → OpenAI
- **Disponibilidad**: Cambia a proveedores alternativos si uno falla
- **Costos**: Optimización automática de uso de API
- **Preferencias**: Configuración personalizada por usuario

---

## 🚀 Quick Start

### Requisitos Previos
- Python 3.10+
- Windows 10/11
- [Google Gemini API Key](https://ai.google.dev/) (gratis)
- Git

### 1️⃣ Instalación

```bash
# Clone repository
git clone https://github.com/tu-usuario/SynapseOS.git
cd SynapseOS

# Create virtual environment
python -m venv venv
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2️⃣ Configuración

```bash
# Copy example .env
copy .env.example .env

# Configure AI Providers
# Google Gemini (required)
GEMINI_API_KEY=AIza...your_gemini_key_here

# OpenAI Codex (optional - enables GPT adoption)
OPENAI_CLIENT_ID=your_openai_client_id
OPENAI_CLIENT_SECRET=your_openai_client_secret
OAUTH_REDIRECT_URI=http://localhost:8000/auth/callback
```

### 3️⃣ Ejecutar (en desarrollo)

```bash
python main.py
```

### 4️⃣ Demostración Multi-Provider

```bash
python demo_providers.py
```

Muestra cómo SynapseOS puede adoptar diferentes proveedores de IA dinámicamente.

### Primer Uso - API

```python
import requests

# Submit task
response = requests.post(
    "http://localhost:8000/api/v1/tasks",
    json={"description": "Abrir Notepad y escribir Hola", "priority": 5},
    headers={"X-API-Key": "your_api_key"}
)

task_id = response.json()["task_id"]
print(f"✅ Task submitted: {task_id}")

# Check status
status = requests.get(
    f"http://localhost:8000/api/v1/tasks/{task_id}",
    headers={"X-API-Key": "your_api_key"}
).json()

print(f"Status: {status['status']}")
```

---

## 🏗️ Arquitectura

### System Layers

```
┌─────────────────────────────────────────┐
│    CLIENTS (API + OAuth Codex)          │
└────────────────┬────────────────────────┘
                 │
         ┌───────▼────────────┐
         │   TASK QUEUE       │ ← Tareas pendientes
         └───────┬────────────┘
                 │
    ┌────────────▼─────────────────┐
    │   STATE MANAGER              │ ← Monitorea CPU/RAM/DISK
    │  (IDLE/WORKING/THINKING/OL)  │
    └────────────┬──────────────────┘
                 │
      ┌──────────▼────────────────┐
      │  GEMINI API (Reasoning)   │ ← AI Brain
      │  ├─ Vision                │
      │  ├─ Planning              │
      │  └─ Decision Making       │
      └──────────┬──────────────┘
                 │
    ┌────────────▼──────────────────────┐
    │   ABILITIES (100+ Skills)        │
    │  ├─ Input Control (Mouse/KB)      │
    │  ├─ Window Management             │
    │  ├─ File Operations               │
    │  ├─ Visual Recognition (OCR)      │
    │  ├─ App Launcher                  │
    │  └─ System Monitor                │
    └────────────┬──────────────────────┘
                 │
         ┌───────▼────────────┐
         │  WINDOWS SYSTEM    │ ← Hardware
         │  (Applications)    │
         └────────────────────┘
```

### Estados del Sistema

| Estado | CPU | RAM | Descripción |
|--------|-----|-----|-----------|
| 🟢 **IDLE** | ~5% | ~200MB | Watchdog activo, sin tareas |
| 🔵 **WORKING** | 40-60% | 2-4GB | Procesamiento normal |
| 🟣 **THINKING** | 70-80% | 5-6GB | Análisis profundo con Gemini |
| 🔴 **OVERLOADED** | 80%+ | 85%+ | Modo seguro (prioriza estabilidad) |

---

## 📊 Roadmap

### 🟢 Phase 1: Core Base (Week 1)
- [ ] State Manager con monitoreo real-time
- [ ] Cliente Gemini API completo
- [ ] 20 abilities básicas (mouse, teclado, ventanas)
- [ ] **Checkpoint**: Abrir Notepad y escribir

### 🟡 Phase 2: Visual Awareness (Week 2)
- [ ] OCR y reconocimiento visual (Gemini Vision)
- [ ] Detección automática de elementos en pantalla
- [ ] Screenshot analysis & interpretation
- [ ] **Checkpoint**: Navegar navegador web

### 🟡 Phase 3: Task Management (Week 3)
- [ ] Cola de tareas persistente (SQLite)
- [ ] Main loop de procesamiento
- [ ] Error handling y retry automático
- [ ] **Checkpoint**: Procesar múltiples tareas

### 🔵 Phase 4: Learning Loop (Week 4)
- [ ] Recolección de métricas en tiempo real
- [ ] Análisis de patrones y optimización automática
- [ ] Sistema de "playbooks" (plantillas de ejecución)
- [ ] **Checkpoint**: Verificar mejora exponencial

### 🔵 Phase 5: API & Dashboard (Week 5)
- [ ] FastAPI endpoints completos
- [ ] OAuth 2.0 con Codex
- [ ] Dashboard web en tiempo real
- [ ] **Checkpoint**: Full integration test

---

## 📁 Project Structure

```
SynapseOS/
├── 📄 README.md                    # This file
├── 📄 ARCHITECTURE.md              # Technical architecture (26KB)
├── 📄 PROJECT_PLAN.md              # 30-day implementation plan (35KB)
├── 📄 GETTING_STARTED.md           # Quick start guide
├── 📋 requirements.txt             # Python dependencies
├── 🔐 .env.example                 # Environment variables template
├── 📜 LICENSE                      # MIT License
├── .gitignore
│
├── 📂 core/                        # Main engine
│   ├── state_manager.py            # State machine & resource monitoring
│   ├── gemini_client.py            # Gemini API client
│   ├── task_orchestrator.py        # Task execution orchestrator
│   ├── task_queue.py               # Task queue management
│   ├── metrics.py                  # Performance metrics
│   └── __init__.py
│
├── 📂 abilities/                   # 100+ PC control skills
│   ├── input_control.py            # Mouse & keyboard
│   ├── window_management.py        # Window handling
│   ├── file_operations.py          # File I/O
│   ├── app_launcher.py             # Application launcher
│   ├── vision.py                   # OCR & visual recognition
│   ├── system_monitor.py           # CPU/RAM/Disk monitoring
│   └── __init__.py
│
├── 📂 config/                      # Configuration
│   ├── settings.py                 # Centralized settings
│   ├── prompts.py                  # Gemini system prompts
│   └── limits.py                   # Resource limits
│
├── 📂 api/                         # REST API
│   ├── app.py                      # FastAPI application
│   ├── routes/                     # API endpoints
│   └── static/                     # Web dashboard
│
├── 📂 utils/                       # Utilities
│   ├── logger.py                   # Logging system
│   ├── validators.py               # Input validators
│   └── helpers.py                  # Helper functions
│
├── 📂 tests/                       # Test suite
│   ├── unit/                       # Unit tests
│   ├── integration/                # Integration tests
│   └── performance/                # Performance tests
│
├── 📂 tasks/                       # Task storage
│   ├── pending.json
│   ├── completed.json
│   └── failed.json
│
├── 📂 logs/                        # System logs
└── main.py                         # Main entry point
```

---

## 🛠️ Tecnologías

### Core
- **Python 3.10+** - Main language
- **Google Gemini API** - Multimodal AI engine
- **FastAPI** - Async HTTP framework
- **SQLite/Redis** - Task storage
- **AsyncIO** - Async concurrency

### Desktop Automation
- **PyAutoGUI** - Mouse & keyboard control
- **PyGetWindow** - Window management
- **Pytesseract** - OCR
- **PIL/Pillow** - Image processing

### DevOps
- **Git/GitHub** - Version control
- **GitHub Actions** - CI/CD
- **Docker** (próximamente) - Containerization

---

## 🔑 Configuración

### Environment Variables

```bash
# Google Gemini
GEMINI_API_KEY=AIza...your_key

# Server
API_HOST=127.0.0.1
API_PORT=8000
API_DEBUG=false

# System Limits
MAX_CONCURRENT_TASKS=5
MAX_RAM_USAGE=0.85
MAX_CPU_USAGE=0.80
TASK_TIMEOUT=300

# Logging
LOG_LEVEL=INFO
LOG_PATH=logs/system.log

# Features
ENABLE_LEARNING=true
ENABLE_PLAYBOOKS=true
ENABLE_OPTIMIZATION=true
```

Setup:
```bash
copy .env.example .env
# Edit .env with your values
```

---

## 🔒 Security & Privacy

✅ **Isolation** - Sandboxed execution environment  
✅ **Timeouts** - All actions have maximum time limits  
✅ **Whitelist** - Only pre-approved commands allowed  
✅ **Audit Log** - Complete action history  
✅ **Rate Limiting** - API abuse protection  
✅ **Input Validation** - All inputs validated  
✅ **Encryption** - Sensitive data encrypted at rest  

---

## 💡 Use Cases

**Perfect for:**
- 📊 Data analysis & report generation
- 🔍 Web scraping & information extraction
- 📝 Administrative automation
- 💰 Financial audit & invoice processing
- 🖼️ Image processing & OCR
- 📱 Multi-app interaction
- ⚡ Repetitive tasks requiring precision

---

## 💰 Costos (Gemini API)

| Operation | Cost |
|-----------|------|
| Chat Input | $0.075 / 1M tokens |
| Chat Output | $0.30 / 1M tokens |
| Vision | $0.01 / 1K pixels |
| Context Cache | 50% descuento |

**Optimization Strategy:**
1. ♻️ Reuse context via cache (50% off)
2. 📸 Screenshot only when needed
3. 🎯 Limit output to max 500 tokens
4. 📦 Batch similar tasks
5. 🎭 Use playbooks (no Gemini cost)

---

## 🧪 Testing

```bash
# Run all tests
pytest tests/ -v

# Unit tests only
pytest tests/unit/ -v

# Integration tests
pytest tests/integration/ -v

# With coverage
pytest tests/ --cov=core --cov=abilities --cov-report=html
```

**Target Coverage: 85%+**

---

## 📖 Documentación

| Documento | Descripción |
|-----------|-------------|
| [GETTING_STARTED.md](./GETTING_STARTED.md) | Step-by-step guide |
| [ARCHITECTURE.md](./ARCHITECTURE.md) | Technical deep dive (26KB) |
| [PROJECT_PLAN.md](./PROJECT_PLAN.md) | Implementation phases (35KB) |
| [API_DOCS.md](./docs/API.md) | API reference (próximo) |

---

## 🤝 Contribute

Contributions welcome! 

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/Amazing`)
3. **Commit** changes (`git commit -m 'Add Amazing'`)
4. **Push** to branch (`git push origin feature/Amazing`)
5. **Open** a Pull Request

See [CONTRIBUTING.md](./CONTRIBUTING.md) for guidelines.

---

## 📞 Support

- 📧 **Email**: [tu-email@example.com]
- 💬 **Issues**: [GitHub Issues](https://github.com/tu-usuario/SynapseOS/issues)
- 📚 **Docs**: [Full Documentation](./docs)
- 🐛 **Bugs**: [Report Here](https://github.com/tu-usuario/SynapseOS/issues)

---

## 📜 Licencia

MIT License - see [LICENSE](./LICENSE) for details

```
MIT License

Copyright (c) 2026 Jack

Permission is hereby granted, free of charge, to any person obtaining a copy...
```

---

## 🙏 Acknowledgments

Inspired by:
- Autonomous AI projects
- OpenClaw multi-modal AI framework
- Open source community

---

<div align="center">

### 🚀 Ready to Get Started?

**[📖 Read Quick Start](./GETTING_STARTED.md)** • **[🏗️ View Architecture](./ARCHITECTURE.md)** • **[📋 See Plan](./PROJECT_PLAN.md)**

---

**Made with ❤️ by Jack**

*Convirtiendo Gemini en una trabajadora* 💼✨

[⭐ Star us](https://github.com/tu-usuario/SynapseOS) • [👀 Watch](https://github.com/tu-usuario/SynapseOS/subscription) • [🔔 Follow](https://github.com/tu-usuario)

</div>
