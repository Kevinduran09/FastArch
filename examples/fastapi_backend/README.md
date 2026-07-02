# FastAPI Backend Example

Demostración de FastArch con guardias de autorización y dependencias.

## Ejecutar

```bash
cd /Users/kevinduran/dev/fastarch
make run
```

O manualmente:

```bash
source .venv/bin/activate
python -m uvicorn examples.fastapi_backend.app:app --reload --port 8000
```

## URLs

- Documentación interactiva: http://127.0.0.1:8000/docs
- OpenAPI JSON: http://127.0.0.1:8000/openapi.json

## Guardias requeridas

### GET /api/v1/health (sin guardia)

```bash
curl http://127.0.0.1:8000/api/v1/health
```

Respuesta:
```json
{"ok": true}
```

### GET /api/v1/users/ (requiere demo-token)

```bash
curl -H "x-demo-token: demo-secret" http://127.0.0.1:8000/api/v1/users/
```

### POST /api/v1/users/ (requiere demo-token + write-token)

```bash
curl -X POST \
  -H "x-demo-token: demo-secret" \
  -H "x-write-token: write-secret" \
  -H "Content-Type: application/json" \
  -d '{"name": "Grace Hopper"}' \
  http://127.0.0.1:8000/api/v1/users/
```

## Códigos de error

- `401` — Falta o es inválido `x-demo-token`
- `403` — Falta o es inválido `x-write-token`

## Estructura

### HealthController
- Sin guardias (acceso público)
- `GET /api/v1/health` → `{"ok": true}`

### UsersController  
- Guardia `x-demo-token: demo-secret` a nivel controller
- Guardia adicional `x-write-token: write-secret` para POST

**Rutas:**
- `GET /api/v1/users/` → lista de usuarios
- `POST /api/v1/users/` → crear usuario

## Demostración de guards

Este ejemplo ilustra cómo FastArch:
- Separa declarativamente guards de dependencies
- Mantiene el orden: controller deps → controller guards → route deps → route guards
- Usa headers nativos de FastAPI dentro del sistema de guards
- Registra todo automáticamente en OpenAPI
