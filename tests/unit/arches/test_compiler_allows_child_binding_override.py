"""Compiler binding override tests."""

from __future__ import annotations

from fastarch import Arch, bind
from fastarch.arches.compiler import compile_arch
from fastarch.controllers import controller
from fastarch.routes import get


class UserRepository:
    pass


class UserPostgresRepository(UserRepository):
    pass


class UserMuckRepository(UserRepository):
    pass


@controller("/users")
class UsersController:
    @get("/{user_id}")
    def read_user(self, user_id: str) -> dict[str, str]:
        return {"user_id": user_id}


def test_compiler_allows_child_binding_override() -> None:
    """Verify that child Arch can override parent bindings in its own branch."""
    users_arch = Arch(
        prefix="/users",
        controllers=[UsersController],
        wires=[bind(UserRepository).to(UserMuckRepository).request()],
    )

    api_arch = Arch(
        prefix="/api/v1",
        arches=[users_arch],
        wires=[bind(UserRepository).to(UserPostgresRepository).request()],
    )

    compiled = compile_arch(api_arch)

    # Child binding should override parent binding
    assert compiled[0].bindings[UserRepository].implementation == UserMuckRepository
