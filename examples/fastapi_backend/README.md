# FastArch FastAPI backend example

This example stays inside the MVP boundaries:

- manual controller registration
- one zero-arg controller (`HealthController`)
- one stateful controller instance (`UsersController`)
- native FastAPI guard headers declared with FastArch `guards=`
- in-memory service only
- no DB, auth, autodiscovery, or CLI

## Files

- `app.py` — creates the FastAPI app and registers controllers with `include_controllers(...)`

## Run

From the repository root:

```bash
uvicorn examples.fastapi_backend.app:app --reload
```

Then open:

- `http://127.0.0.1:8000/docs`
- `GET /api/v1/health`
- `GET /api/v1/users/` with header `x-demo-token: demo`
- `POST /api/v1/users/` with headers `x-demo-token: demo` and `x-write-token: demo`

The users controller demonstrates the approved merge order without adding a custom auth layer:

1. controller dependencies
2. controller guards
3. route dependencies
4. route guards

Both guard headers are plain FastAPI `Header(...)` dependencies declared through FastArch `guards=`. The example keeps them no-op on purpose so the focus stays on native registration semantics.

Example POST body:

```json
{
  "name": "Grace Hopper"
}
```
