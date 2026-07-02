"""Test fixtures for FastArch."""

from __future__ import annotations

from typing import Annotated

import pytest
from fastapi import Depends, FastAPI, Header
from pydantic import BaseModel

from fastarch import controller, get, post


# ============================================================================
# Fixtures: Models
# ============================================================================


class User(BaseModel):
    """Sample user model for testing."""

    id: int
    name: str


class CreateUserRequest(BaseModel):
    """Request payload for creating a user."""

    name: str


# ============================================================================
# Fixtures: Dependencies and Guards
# ============================================================================


def mock_audit_log() -> None:
    """Mock audit logging dependency."""
    pass


def mock_get_current_user() -> str:
    """Mock user retrieval dependency."""
    return "test_user"


def mock_require_admin(x_admin_token: Annotated[str, Header()]) -> None:
    """Mock admin guard requiring header."""
    if not x_admin_token:
        raise ValueError("Missing admin token")


def mock_require_write(x_write_token: Annotated[str, Header()]) -> None:
    """Mock write permission guard requiring header."""
    if not x_write_token:
        raise ValueError("Missing write token")


# ============================================================================
# Fixtures: Controllers
# ============================================================================


@controller("/users", tags=["users"], dependencies=(Depends(mock_audit_log),), guards=(mock_require_admin,))
class MockUsersController:
    """Mock users controller for testing."""

    def __init__(self) -> None:
        self.users = [User(id=1, name="Alice"), User(id=2, name="Bob")]

    @get("/", response_model=list[User], summary="List all users")
    def list_users(self) -> list[User]:
        """List all users."""
        return self.users

    @get("/{user_id}", response_model=User, summary="Get user by ID")
    def get_user(self, user_id: int) -> User:
        """Get a user by ID."""
        for user in self.users:
            if user.id == user_id:
                return user
        raise ValueError("User not found")

    @post("/", response_model=User, status_code=201, dependencies=(Depends(mock_get_current_user),), guards=(mock_require_write,), summary="Create user")
    def create_user(self, payload: CreateUserRequest) -> User:
        """Create a new user."""
        user_id = max([u.id for u in self.users]) + 1
        user = User(id=user_id, name=payload.name)
        self.users.append(user)
        return user


@controller("/health", tags=["health"])
class MockHealthController:
    """Mock health check controller."""

    @get("", summary="Health check")
    def health(self) -> dict[str, str]:
        """Return health status."""
        return {"status": "ok"}


# ============================================================================
# Fixtures: Apps
# ============================================================================


@pytest.fixture
def fastapi_app() -> FastAPI:
    """Create a fresh FastAPI app for testing."""
    return FastAPI(title="Test API", version="0.1.0")


@pytest.fixture
def app_with_controllers(fastapi_app: FastAPI) -> FastAPI:
    """Create a FastAPI app with mock controllers registered."""
    from fastarch import include_controllers

    include_controllers(fastapi_app, [MockHealthController, MockUsersController], prefix="/api/v1")
    return fastapi_app


@pytest.fixture
def test_client(app_with_controllers: FastAPI):
    """Create a TestClient for the app."""
    from fastapi.testclient import TestClient

    return TestClient(app_with_controllers)
