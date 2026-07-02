# FastArch

FastArch is a thin layer on top of FastAPI for class-based controllers without breaking native FastAPI behavior.

## MVP API

```python
from fastarch import controller, route, get, post, put, patch, delete, include_controllers
```

MVP scope is intentionally small:

- metadata-only decorators
- manual controller registration
- FastAPI-native signatures, `Depends`, `Annotated`, and OpenAPI support

Out of scope for this MVP:

- autodiscovery
- CLI/scaffolding
- auth/permissions abstractions
- database/ORM integrations

## Quickstart

```python
from fastapi import FastAPI, status
from pydantic import BaseModel

from fastarch import controller, get, include_controllers, post


class UserCreate(BaseModel):
    name: str


class UserRead(BaseModel):
    id: int
    name: str


class InMemoryUserService:
    def __init__(self) -> None:
        self._users = [UserRead(id=1, name="Ada")]
        self._next_id = 2

    def list_users(self) -> list[UserRead]:
        return list(self._users)

    def create_user(self, payload: UserCreate) -> UserRead:
        user = UserRead(id=self._next_id, name=payload.name)
        self._users.append(user)
        self._next_id += 1
        return user


@controller("/users", tags=("users",))
class UsersController:
    def __init__(self, service: InMemoryUserService) -> None:
        self.service = service

    @get("/", response_model=list[UserRead], summary="List users")
    def list_users(self) -> list[UserRead]:
        return self.service.list_users()

    @post("/", response_model=UserRead, status_code=status.HTTP_201_CREATED)
    def create_user(self, payload: UserCreate) -> UserRead:
        return self.service.create_user(payload)


app = FastAPI()
service = InMemoryUserService()

include_controllers(app, [UsersController(service)], prefix="/api/v1")
```

## Example app

A runnable example lives in [`examples/fastapi_backend`](examples/fastapi_backend/README.md).

It shows:

- one zero-arg controller and one stateful controller instance
- manual `include_controllers(...)` registration
- controller `dependencies=` and `guards=` staying separate until registration
- an in-memory service instead of a database
- generated OpenAPI metadata staying native to FastAPI

## Guards stay FastAPI-native

Use `guards=` when you want guard callables to become native FastAPI dependencies at registration time without mixing them into metadata early.

FastArch keeps `dependencies=` and `guards=` separate on `ControllerDefinition` and `RouteDefinition`, then `include_controllers(...)` merges them once in this order:

1. controller dependencies
2. controller guards
3. route dependencies
4. route guards

```python
from typing import Annotated

from fastapi import Depends, Header

from fastarch import controller, post


def audit_users_access() -> None:
    return None


def require_demo_token(x_demo_token: Annotated[str, Header()]) -> None:
    return None


def audit_create_user() -> None:
    return None


def require_write_token(x_write_token: Annotated[str, Header()]) -> None:
    return None


@controller(
    "/users",
    dependencies=(Depends(audit_users_access),),
    guards=(require_demo_token,),
)
class UsersController:
    @post(
        "/",
        dependencies=(Depends(audit_create_user),),
        guards=(require_write_token,),
    )
    def create_user(self, payload: dict[str, str]) -> dict[str, str]:
        ...
```

No manual guard execution, no endpoint wrapping, and no signature changes — FastAPI still owns the dependency graph.

## Development notes

FastArch decorators only attach metadata. Real FastAPI routes are created when you call `include_controllers(...)`.
