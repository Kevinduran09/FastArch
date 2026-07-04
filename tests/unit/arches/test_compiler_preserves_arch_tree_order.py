"""Compiler arch tree order preservation tests."""

from __future__ import annotations

from fastarch import Arch
from fastarch.arches.compiler import compile_arch
from fastarch.controllers import controller
from fastarch.routes import get


@controller("/users")
class UsersController:
    @get("/")
    def list_users(self) -> list:
        return []


@controller("/pets")
class PetsController:
    @get("/")
    def list_pets(self) -> list:
        return []


@controller("/items")
class ItemsController:
    @get("/")
    def list_items(self) -> list:
        return []


def test_compiler_preserves_arch_tree_order() -> None:
    """Verify that compiler maintains the order of child arches during compilation."""
    users_arch = Arch(prefix="/users", controllers=[UsersController])
    pets_arch = Arch(prefix="/pets", controllers=[PetsController])
    items_arch = Arch(prefix="/items", controllers=[ItemsController])

    api_arch = Arch(
        prefix="/api/v1",
        arches=[users_arch, pets_arch, items_arch],
    )

    compiled = compile_arch(api_arch)

    assert len(compiled) == 3
    assert compiled[0].prefix == "/api/v1/users"
    assert compiled[1].prefix == "/api/v1/pets"
    assert compiled[2].prefix == "/api/v1/items"
