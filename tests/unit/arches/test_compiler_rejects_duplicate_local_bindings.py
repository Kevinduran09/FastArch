"""Compiler duplicate binding validation tests."""

from __future__ import annotations

import pytest

from fastarch import Arch, bind
from fastarch.arches.compiler import compile_arch
from fastarch.arches.errors import DuplicateBindingError


class UserService:
    pass


class UserServiceV1(UserService):
    pass


class UserServiceV2(UserService):
    pass


def test_compiler_rejects_duplicate_local_bindings() -> None:
    """Verify that compiler rejects duplicate bindings within the same Arch."""
    api_arch = Arch(
        prefix="/api/v1",
        wires=[
            bind(UserService).to(UserServiceV1).request(),
            bind(UserService).to(UserServiceV2).singleton(),
        ],
    )

    with pytest.raises(DuplicateBindingError, match="bound more than once"):
        compile_arch(api_arch)
