# FastArch API Reference

Complete API documentation for FastArch decorators and functions.

## Overview

FastArch provides decorators to register class-based controllers in FastAPI without wrapping or modifying your functions. All decorators store metadata that is later processed by `include_controllers()` during app registration.

## Decorators

### `@controller(...)`

Attach metadata to a class for FastAPI controller registration.

```python
from fastarch import controller

@controller(prefix="/users", tags=["users"])
class UsersController:
    @get("/")
    def list(self):
        return []
```

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `prefix` | `str` | `""` | URL path prefix for all routes in this controller |
| `tags` | `Sequence[str] \| None` | `None` | OpenAPI tags for documentation and grouping |
| `dependencies` | `Sequence[Any] \| None` | `None` | Controller-level dependencies (using `Depends()`) |
| `guards` | `Sequence[Any] \| None` | `None` | Controller-level guards (authorization/security) |
| `responses` | `dict[int \| str, Any] \| None` | `None` | Mapping of status codes to response schemas |
| `**kwargs` | | | Additional metadata passed to FastAPI router |

**Raises:**

- `TypeError` — If decorated object is not a class, or if missing from a route

---

### `@route(path, *, methods, ...)`

Attach metadata to a function for FastAPI route registration.

```python
from fastarch import route

@route("/users", methods=["GET"])
def list_users():
    return []
```

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `path` | `str` | Required | URL path for this route |
| `methods` | `Sequence[str]` | Required | HTTP methods (e.g., `["GET", "POST"]`) |
| `response_model` | `Any \| None` | `None` | Pydantic model for response validation |
| `status_code` | `int \| None` | `None` | Default HTTP status code for success |
| `tags` | `Sequence[str] \| None` | `None` | OpenAPI tags for documentation |
| `dependencies` | `Sequence[Any] \| None` | `None` | Route-level dependencies (using `Depends()`) |
| `guards` | `Sequence[Any] \| None` | `None` | Route-level guards (authorization/security) |
| `summary` | `str \| None` | `None` | Short description for OpenAPI |
| `description` | `str \| None` | `None` | Detailed description for OpenAPI |
| `responses` | `dict[int \| str, Any] \| None` | `None` | Status code to response schema mapping |
| `name` | `str \| None` | `None` | Internal route name for FastAPI |
| `operation_id` | `str \| None` | `None` | Custom operation ID for OpenAPI code generators |
| `deprecated` | `bool \| None` | `None` | Mark as deprecated in OpenAPI |
| `include_in_schema` | `bool` | `True` | Include in OpenAPI schema |
| `response_description` | `str \| None` | `None` | Description of the response for OpenAPI |
| `**kwargs` | | | Additional metadata passed to FastAPI |

**Raises:**

- `TypeError` — If decorated object is not callable

---

### HTTP Method Shortcuts

FastArch provides shortcuts for common HTTP methods:

```python
from fastarch import get, post, put, patch, delete

@get("/users")
def list_users(): ...

@post("/users")
def create_user(): ...

@put("/users/{id}")
def update_user(id: int): ...

@patch("/users/{id}")
def partial_update(id: int): ...

@delete("/users/{id}")
def delete_user(id: int): ...
```

Each shorthand accepts all arguments that `@route()` accepts (except `methods`).

---

## Functions

### `include_controllers(app_or_router, controllers, prefix="")`

Register FastArch controllers on a FastAPI app or router.

```python
from fastapi import FastAPI
from fastarch import include_controllers

app = FastAPI()
include_controllers(app, [UsersController, HealthController], prefix="/api/v1")
```

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `app_or_router` | `Any` | Required | FastAPI app or APIRouter instance |
| `controllers` | `Iterable[Any]` | Required | Controller classes or instances |
| `prefix` | `str` | `""` | Global prefix prepended to controller prefixes |

**Returns:**

The `app_or_router` argument (for chaining).

**Raises:**

- `TypeError` — If app/router lacks `include_router()`, if controller lacks `@controller()`, or if controller class cannot be instantiated

**Notes:**

- Controllers passed as classes are instantiated with zero arguments
- Pre-instantiated controllers are accepted and used as-is
- Dependencies and guards are merged per-route in this order:
  1. Controller-level dependencies
  2. Controller-level guards
  3. Route-level dependencies
  4. Route-level guards

---

### `include_controllers_from_package(app_or_router, package, prefix="")`

Auto-discover and register all `@controller`-decorated classes from a package.

```python
from fastapi import FastAPI
from fastarch import include_controllers_from_package

app = FastAPI()

# Scan entire "myapp.controllers" package recursively
include_controllers_from_package(app, "myapp.controllers", prefix="/api/v1")

# Or pass a module object directly
import myapp.controllers
include_controllers_from_package(app, myapp.controllers, prefix="/api/v1")
```

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `app_or_router` | `Any` | Required | FastAPI app or APIRouter instance |
| `package` | `str \| ModuleType` | Required | Package name (e.g., `"myapp.controllers"`) or module object |
| `prefix` | `str` | `""` | Global prefix for all discovered controllers |

**Returns:**

The `app_or_router` argument (for chaining).

**Raises:**

- `ImportError` — If package cannot be imported or nested modules fail
- `TypeError` — If package is not a string or ModuleType

**How it works:**

1. Recursively scans all modules in the package tree
2. Collects all classes decorated with `@controller()`
3. Passes discovered controllers to `include_controllers()`
4. Deduplicates controllers by module and qualified name

**Example structure:**

```python
# myapp/controllers/__init__.py
# (empty or re-exports)

# myapp/controllers/users.py
from fastarch import controller, get

@controller("/users")
class UsersController:
    @get("/")
    def list_users(self):
        return []

# myapp/controllers/health.py
@controller("/health")
class HealthController:
    @get("")
    def ping(self):
        return {"status": "ok"}

# main.py
from fastapi import FastAPI
from fastarch import include_controllers_from_package

app = FastAPI()
include_controllers_from_package(app, "myapp.controllers", prefix="/api/v1")

# Now available:
# GET /api/v1/users/
# GET /api/v1/health
```

---

## Metadata Classes

### `ControllerDefinition`

Immutable dataclass storing controller metadata.

```python
from fastarch.types import ControllerDefinition

definition = ControllerDefinition(
    prefix="/users",
    tags=("users",),
    dependencies=(),
    guards=(),
    responses={},
    extras={},
)
```

**Attributes:**

| Attribute | Type | Description |
|-----------|------|-------------|
| `prefix` | `str` | URL prefix for controller routes |
| `tags` | `tuple[str, ...]` | OpenAPI tags |
| `dependencies` | `tuple[Any, ...]` | Controller-level dependencies |
| `guards` | `tuple[Any, ...]` | Controller-level guards |
| `responses` | `dict[int \| str, Any]` | Status code to response schema mapping |
| `extras` | `dict[str, Any]` | Custom metadata for integrators |

---

### `RouteDefinition`

Immutable dataclass storing route metadata.

```python
from fastarch.types import RouteDefinition

definition = RouteDefinition(
    path="/users",
    methods=("GET",),
    response_model=UserSchema,
    status_code=200,
    tags=("users",),
    dependencies=(),
    guards=(),
    summary="List users",
    description=None,
    responses={},
    name=None,
    operation_id=None,
    deprecated=False,
    include_in_schema=True,
    response_description=None,
    extras={},
)
```

**Attributes:**

| Attribute | Type | Description |
|-----------|------|-------------|
| `path` | `str` | URL path for the route |
| `methods` | `tuple[HttpMethod, ...]` | HTTP methods |
| `response_model` | `Any \| None` | Response model for validation |
| `status_code` | `int \| None` | Default success status code |
| `tags` | `tuple[str, ...]` | OpenAPI tags |
| `dependencies` | `tuple[Any, ...]` | Route-level dependencies |
| `guards` | `tuple[Any, ...]` | Route-level guards |
| `summary` | `str \| None` | Short description |
| `description` | `str \| None` | Detailed description |
| `responses` | `dict[int \| str, Any]` | Status code mappings |
| `name` | `str \| None` | Internal route name |
| `operation_id` | `str \| None` | OpenAPI operation ID |
| `deprecated` | `bool \| None` | Deprecated flag |
| `include_in_schema` | `bool` | Include in OpenAPI schema |
| `response_description` | `str \| None` | Response description |
| `extras` | `dict[str, Any]` | Custom metadata for integrators |

---

## Type Hints

### `HttpMethod`

```python
from fastarch.types import HttpMethod

# Type: Literal["GET", "POST", "PUT", "PATCH", "DELETE"]
```

---

## Constants

| Name | Value | Purpose |
|------|-------|---------|
| `FASTARCH_CONTROLLER_DEFINITION_ATTR` | `"__fastarch_controller_definition__"` | Attribute name for storing controller metadata |
| `FASTARCH_ROUTE_DEFINITION_ATTR` | `"__fastarch_route_definition__"` | Attribute name for storing route metadata |

---

## Complete Example

```python
from typing import Annotated
from fastapi import FastAPI, Depends, Header, status
from pydantic import BaseModel

from fastarch import controller, get, post, include_controllers


class User(BaseModel):
    id: int
    name: str


def require_admin(x_token: Annotated[str, Header()]) -> None:
    """Guard: verify admin token."""
    if x_token != "admin-secret":
        raise ValueError("Unauthorized")


def audit_log() -> None:
    """Dependency: log access."""
    pass


@controller("/users", tags=["users"], dependencies=(Depends(audit_log),), guards=(require_admin,))
class UsersController:
    def __init__(self) -> None:
        self.users = [User(id=1, name="Alice")]

    @get("/", response_model=list[User])
    def list_users(self) -> list[User]:
        return self.users

    @post("/", response_model=User, status_code=status.HTTP_201_CREATED)
    def create_user(self, name: str) -> User:
        user = User(id=len(self.users) + 1, name=name)
        self.users.append(user)
        return user


app = FastAPI()
include_controllers(app, [UsersController], prefix="/api/v1")

# Now available:
# GET  /api/v1/users/
# POST /api/v1/users/
```

---

For more examples, see:
- [docs/explain/overview.md](../explain/overview.md) — Detailed architecture explanation
- [examples/fastapi_backend/](../../examples/fastapi_backend/) — Full working example
- [tests/](../../tests/) — Test examples and fixtures
