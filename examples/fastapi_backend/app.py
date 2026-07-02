"""Minimal FastAPI backend showing FastArch in a realistic MVP flow."""

from __future__ import annotations

from typing import Annotated

from fastapi import Depends, FastAPI, Header, HTTPException, status
from pydantic import BaseModel

from fastarch import controller, get, include_controllers, post


class UserCreate(BaseModel):
    name: str


class UserRead(BaseModel):
    id: int
    name: str


class InMemoryUserService:
    def __init__(self) -> None:
        self._users = [UserRead(id=1, name="Ada Lovelace")]
        self._next_id = 2

    def list_users(self) -> list[UserRead]:
        return list(self._users)

    def create_user(self, payload: UserCreate) -> UserRead:
        user = UserRead(id=self._next_id, name=payload.name)
        self._users.append(user)
        self._next_id += 1
        return user


def audit_users_access() -> None:
    """Controller-level dependency kept separate from guards until registration."""


def require_demo_token(x_demo_token: Annotated[str | None, Header()] = None) -> None:
    """Controller-level guard exposed as a native FastAPI header dependency."""
    if not x_demo_token or x_demo_token != "demo-secret":
        raise HTTPException(
            status_code=401, detail="Invalid or missing x-demo-token header"
        )


def audit_create_user() -> None:
    """Route-level dependency that still runs before route guards."""


def require_write_token(x_write_token: Annotated[str | None, Header()] = None) -> None:
    """Route-level guard exposed as a native FastAPI header dependency."""
    if not x_write_token or x_write_token != "write-secret":
        raise HTTPException(
            status_code=403, detail="Invalid or missing x-write-token header"
        )


@controller("/health", tags=("health",))
class HealthController:
    @get("", summary="Readiness probe")
    def readiness(self) -> dict[str, bool]:
        return {"ok": True}


@controller(
    "/users",
    tags=("users",),
    dependencies=(Depends(audit_users_access),),
    guards=(require_demo_token,),
)
class UsersController:
    def __init__(self, service: InMemoryUserService) -> None:
        self.service = service

    @get("/", response_model=list[UserRead], summary="List users")
    def list_users(self) -> list[UserRead]:
        return self.service.list_users()

    @post(
        "/",
        response_model=UserRead,
        status_code=status.HTTP_201_CREATED,
        dependencies=(Depends(audit_create_user),),
        guards=(require_write_token,),
        summary="Create user",
    )
    def create_user(self, payload: UserCreate) -> UserRead:
        return self.service.create_user(payload)


def create_app() -> FastAPI:
    app = FastAPI(title="FastArch Example API", version="0.1.0")
    service = InMemoryUserService()

    include_controllers(
        app, [HealthController, UsersController(service)], prefix="/api/v1"
    )

    return app


app = create_app()
