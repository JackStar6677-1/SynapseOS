# Contributing to SynapseOS

¡Gracias por tu interés en contribuir a SynapseOS! 🎉

## 📋 Código de Conducta

Por participar en este proyecto, aceptas:
- Ser respetuoso con otros colaboradores
- Proporcionar feedback constructivo
- Reportar issues responsablemente

## 🚀 Cómo Contribuir

### Reporting Bugs

Antes de hacer un bug report checklist:
- [ ] ¿Ya existe un issue similar?
- [ ] ¿Puedes reproducir el error?
- [ ] ¿Incluyes pasos para reproducir?
- [ ] ¿Incluyes ejemplos específicos?

**Issues deben incluir:**
```
Título: [BUG] Descripción corta
Descripción: Qué pasó
Sistema: Windows 10/11, Python 3.10+
Pasos: 1. ... 2. ... 3. ...
Resultado esperado: ...
Resultado actual: ...
```

### Suggesting Features

**Feature requests deben tener:**
```
Título: [FEATURE] Descripción breve
Problema que soluciona:
Solución propuesta:
Alternativas consideradas:
```

### Pull Requests

1. **Fork** el repositorio
2. **Crea** una rama (`git checkout -b feature/my-feature`)
3. **Haz commits** descriptivos
4. **Push** a tu fork
5. **Abre** un Pull Request

**PR checklist:**
- [ ] Feature implementada completamente
- [ ] Tests añadidos (coverage ≥ 85%)
- [ ] Documentación actualizada
- [ ] Sigues el code style
- [ ] Commits son descriptivos

## 💻 Development Setup

```bash
# Setup environment
git clone https://github.com/tu-usuario/SynapseOS.git
cd SynapseOS
python -m venv venv
venv\Scripts\activate

# Install dev dependencies
pip install -r requirements.txt
pip install pytest pytest-asyncio black flake8

# Setup pre-commit hooks (próximamente)
# pre-commit install
```

## 🎯 Code Standards

### Python Style
- Sigue [PEP 8](https://www.python.org/dev/peps/pep-0008/)
- Use type hints: `def function(x: int) -> str:`
- Max line length: 100 caracteres
- Docstrings en formato Google

```python
def amazing_function(param1: str, param2: int) -> bool:
    """
    Brief description.
    
    Longer description if needed.
    
    Args:
        param1: Description of param1
        param2: Description of param2
        
    Returns:
        Description of return value
        
    Raises:
        ValueError: When something is wrong
        
    Example:
        >>> amazing_function("test", 42)
        True
    """
```

### Testing Requirements
- Escribir tests para cada feature nueva
- Minimun coverage: 85%
- Tests async deben usar `@pytest.mark.asyncio`

```python
# tests/unit/test_example.py
import pytest

@pytest.mark.asyncio
async def test_feature():
    """Test description."""
    result = await some_async_function()
    assert result == expected_value
```

### Git Commit Messages

```
[TYPE] Brief description (max 50 chars)

Detailed explanation if needed (max 72 chars per line).
Explain WHAT and WHY, not HOW.

Fixes #123
```

**Types:**
- `[FEAT]` - New feature
- `[FIX]` - Bug fix
- `[DOCS]` - Documentation
- `[STYLE]` - Code style (formatting, etc)
- `[REFACTOR]` - Code refactoring
- `[TEST]` - Tests
- `[PERF]` - Performance improvement

## 📚 Documentation

- Update docs cuando cambies comportamiento
- Incluye ejemplos de código
- Documenta breaking changes
- Update CHANGELOG.md

## 🧪 Running Tests

```bash
# All tests
pytest tests/ -v

# Specific test file
pytest tests/unit/test_state_manager.py -v

# With coverage
pytest tests/ --cov=core --cov=abilities --cov-report=html

# Watch mode (pytest-watch)
ptw tests/
```

## 📝 Commit Workflow

```bash
# Create feature branch
git checkout -b feature/amazing-thing

# Make changes
git add .
git commit -m "[FEAT] Add amazing feature"

# Keep updated with main
git fetch origin
git rebase origin/main

# Push to your fork
git push origin feature/amazing-thing

# Open PR on GitHub
```

## 🔍 Code Review Process

- Mínimo 1 review antes de merge
- CI/CD debe pasar (tests, linting)
- Coverage no debe disminuir
- Cambios significativos requieren 2 reviews

## 📦 Release Process

- Semvers: MAJOR.MINOR.PATCH
- Update version in `config/settings.py`
- Create release tag
- Update CHANGELOG.md

## ❓ Questions?

- 📧 Email: tu-email@example.com
- 💬 Issues: GitHub Issues
- 📚 Docs: README.md y ARCHITECTURE.md

---

**¡Thank you for contributing!** ⭐
