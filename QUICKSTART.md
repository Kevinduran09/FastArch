# FastArch — Quick Start

## Opción 1: Con Makefile (recomendado)

```bash
# Setup inicial (una sola vez)
make setup

# Levantar el servidor
make run

# En otra terminal, tests
make test
```

## Opción 2: Manual

```bash
# Setup
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e .
python -m pip install uvicorn[standard]

# Levantar servidor
python -m uvicorn examples.fastapi_backend.app:app --reload --port 8000

# Tests (en otra terminal, con venv activo)
python -m pytest -v
```

## Comandos disponibles con Makefile

```bash
make help          # Ver todos los comandos disponibles
make setup         # Instalar dependencias mínimas
make setup-dev     # Setup + dev dependencies (tests, formatting)
make run           # Levantar servidor en localhost:8000
make test          # Correr tests
make test-watch    # Correr tests en watch mode
make lint          # Revisar código
make format        # Auto-formatear código
make clean         # Limpiar venv y cachés
```

## URLs útiles (una vez que el servidor esté corriendo)

- Docs interactivo: http://127.0.0.1:8000/docs
- OpenAPI JSON: http://127.0.0.1:8000/openapi.json
- Healthcheck: http://127.0.0.1:8000/api/v1/health

## Ejemplo de llamada con curl

```bash
# Listar usuarios
curl -X GET http://127.0.0.1:8000/api/v1/users/

# Crear usuario
curl -X POST http://127.0.0.1:8000/api/v1/users/ \
  -H "Content-Type: application/json" \
  -d '{"name": "Bob"}'
```

## Nota

El Makefile detecta automáticamente la mejor versión de Python disponible (3.14, 3.12, 3.11, 3.10, o fallback a 3.9 del sistema). Si usas una versión < 3.10, la instalación fallará con un mensaje claro.

Para instalar Python 3.14 en macOS:

```bash
brew install python@3.14
```
