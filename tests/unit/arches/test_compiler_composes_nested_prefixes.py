"""Compiler prefix composition tests."""

from __future__ import annotations

from fastarch import Arch
from fastarch.arches.compiler import compile_arch
from fastarch.controllers import controller
from fastarch.routes import get


@controller("/users")
class UsersController:
    @get("/{user_id}")
    def read_user(self, user_id: str) -> dict[str, str]:
        return {"user_id": user_id}


def test_compiler_composes_deeply_nested_prefixes() -> None:
    """Verify that nested Arch prefixes are correctly composed into full paths."""
    user_arch = Arch(prefix="user", controllers=[UsersController])
    v1_arch = Arch(prefix="v1", arches=user_arch)
    api_arch = Arch(prefix="api", arches=v1_arch)

    compiled = compile_arch(api_arch)

    assert len(compiled) == 1
    assert compiled[0].prefix == "/api/v1/user"
