"""Compiler binding inheritance tests."""

from __future__ import annotations

from fastarch import Arch, bind
from fastarch.arches.compiler import compile_arch
from fastarch.controllers import controller
from fastarch.routes import get


class Settings:
    pass


class UserRepository:
    pass


class UserService:
    pass


@controller("/users")
class UsersController:
    @get("/{user_id}")
    def read_user(self, user_id: str) -> dict[str, str]:
        return {"user_id": user_id}


@controller("/pets")
class PetsController:
    @get("/")
    def list_pets(self) -> list:
        return []


def test_compiler_inherits_parent_bindings() -> None:
    """Verify that child Arch instances inherit bindings from parent Arch."""
    users_arch = Arch(
        prefix="/users",
        controllers=[UsersController],
        wires=[bind(UserService).request()],
    )
    pets_arch = Arch(prefix="/pets", controllers=[PetsController])
    api_arch = Arch(
        prefix="/api/v1",
        arches=[users_arch, pets_arch],
        wires=[bind(Settings).singleton()],
    )

    compiled = compile_arch(api_arch)

    assert len(compiled) == 2
    # Both children should have access to parent's Settings binding
    assert Settings in compiled[0].bindings
    assert Settings in compiled[1].bindings
