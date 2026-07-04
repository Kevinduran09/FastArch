from __future__ import annotations

import fastarch
from fastarch import Arch, Scope, bind, wires
from fastarch.arches.binding import Binding
from fastarch.arches.wiring import FASTARCH_WIRES_ATTR


class Settings:
    pass


class UserRepository:
    pass


class SqlAlchemyUserRepository(UserRepository):
    pass


class UserService:
    pass


def test_arches_symbols_are_importable_from_public_api() -> None:
    assert Arch is fastarch.Arch
    assert bind is fastarch.bind
    assert wires is fastarch.wires
    assert Scope is fastarch.Scope


def test_bind_builds_singleton_request_and_transient_bindings() -> None:
    singleton = bind(Settings).singleton()
    request = bind(UserRepository).to(SqlAlchemyUserRepository).request()
    transient = bind(UserService).transient()

    assert isinstance(singleton, Binding)
    assert singleton.token is Settings
    assert singleton.implementation is Settings
    assert singleton.scope == Scope.SINGLETON

    assert request.token is UserRepository
    assert request.implementation is SqlAlchemyUserRepository
    assert request.scope == Scope.REQUEST

    assert transient.token is UserService
    assert transient.implementation is UserService
    assert transient.scope == Scope.TRANSIENT


def test_wires_stores_metadata_without_wrapping_function() -> None:
    def handler(service: UserService) -> None:
        return None

    decorated = wires(service=UserService)(handler)

    assert decorated is handler
    assert getattr(handler, FASTARCH_WIRES_ATTR) == {"service": UserService}


def test_arch_is_declarative_and_stores_nested_arches() -> None:
    users_arch = Arch(
        prefix="/users",
        controllers=[],
        wires=[bind(UserService).request()],
    )

    api_arch = Arch(
        prefix="/api/v1",
        arches=[users_arch],
        wires=[bind(Settings).singleton()],
    )

    assert api_arch.prefix == "/api/v1"
    assert api_arch.controllers == ()
    assert len(api_arch.wires) == 1
    assert api_arch.arches == (users_arch,)
    assert users_arch.prefix == "/users"


def test_arch_batch_1_has_no_runtime_mount() -> None:
    assert "mount" not in vars(Arch)
