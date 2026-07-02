from __future__ import annotations

import pkgutil
from types import ModuleType
from typing import Any

import pytest
from fastapi import FastAPI
from fastapi.routing import APIRoute
from fastapi.testclient import TestClient

import fastarch.discovery as discovery
from fastarch import controller, get, include_controllers


def test_include_controllers_from_package_matches_manual_registration_for_nested_fixture_package() -> (
    None
):
    autodiscovery_app = FastAPI()

    discovery.include_controllers_from_package(
        autodiscovery_app,
        "tests.fixtures.autodiscovery_pkg",
        prefix="/api",
    )

    from tests.fixtures.autodiscovery_pkg.admin.users import UsersController
    from tests.fixtures.autodiscovery_pkg.health import HealthController

    manual_app = FastAPI()
    include_controllers(manual_app, [UsersController, HealthController], prefix="/api")

    autodiscovery_client = TestClient(autodiscovery_app)
    manual_client = TestClient(manual_app)

    assert autodiscovery_client.get("/api/health").json() == {
        "ok": True,
    }
    assert autodiscovery_client.get("/api/health").json() == manual_client.get(
        "/api/health"
    ).json()
    assert autodiscovery_client.get("/api/users/").json() == [
        {"id": 1, "name": "Ada Lovelace"},
        {"id": 2, "name": "Grace Hopper"},
    ]
    assert autodiscovery_client.get("/api/users/").json() == manual_client.get(
        "/api/users/"
    ).json()
    assert _route_snapshot(autodiscovery_app) == _route_snapshot(manual_app)
    assert autodiscovery_app.openapi() == manual_app.openapi()


def test_include_controllers_from_package_avoids_duplicate_registration_from_reexports() -> (
    None
):
    app = FastAPI()

    result = discovery.include_controllers_from_package(
        app,
        "tests.fixtures.autodiscovery_reexport_pkg",
        prefix="/api",
    )

    shared_routes = [
        route
        for route in _iter_routes(app)
        if route.path == "/api/shared" and "GET" in route.methods
    ]
    client = TestClient(app)

    assert result is app
    assert len(shared_routes) == 1
    assert client.get("/api/shared").json() == {"source": "source"}
    assert list(app.openapi()["paths"]) == ["/api/shared"]


def test_include_controllers_from_package_discovers_controllers_from_plain_module(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    app = FastAPI()
    plain_module = ModuleType("tests.fake_single")
    single_controller = _build_controller(plain_module.__name__, "/single")
    plain_module.SingleController = single_controller
    calls: list[tuple[Any, list[type[Any]], str]] = []

    monkeypatch.setattr(discovery, "include_controllers", _record_include_calls(calls))

    result = discovery.include_controllers_from_package(app, plain_module, prefix="/api")

    assert result is app
    assert calls == [(app, [single_controller], "/api")]


def test_include_controllers_from_package_discovers_nested_controllers_once(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    app = FastAPI()
    root_package = ModuleType("tests.fakepkg")
    root_package.__path__ = ["/virtual/tests/fakepkg"]
    users_module = ModuleType("tests.fakepkg.users")
    health_module = ModuleType("tests.fakepkg.health")
    reexport_module = ModuleType("tests.fakepkg.reexport")

    users_controller = _build_controller(users_module.__name__, "/users")
    health_controller = _build_controller(health_module.__name__, "/health")

    users_module.UsersController = users_controller
    users_module.UsersAlias = users_controller
    health_module.HealthController = health_controller
    health_module.PlainClass = _build_plain_class(health_module.__name__)
    reexport_module.UsersController = users_controller

    modules = {
        root_package.__name__: root_package,
        users_module.__name__: users_module,
        health_module.__name__: health_module,
        reexport_module.__name__: reexport_module,
    }
    calls: list[tuple[Any, list[type[Any]], str]] = []

    monkeypatch.setattr(discovery, "include_controllers", _record_include_calls(calls))
    monkeypatch.setattr(discovery.importlib, "import_module", modules.__getitem__)
    monkeypatch.setattr(
        discovery.pkgutil,
        "walk_packages",
        lambda path, prefix: [
            pkgutil.ModuleInfo(None, "tests.fakepkg.users", False),
            pkgutil.ModuleInfo(None, "tests.fakepkg.reexport", False),
            pkgutil.ModuleInfo(None, "tests.fakepkg.health", False),
        ],
    )

    result = discovery.include_controllers_from_package(app, root_package, prefix="/api")

    assert result is app
    assert calls == [(app, [health_controller, users_controller], "/api")]


def test_include_controllers_from_package_wraps_missing_root_imports() -> None:
    app = FastAPI()

    with pytest.raises(ImportError) as exc_info:
        discovery.include_controllers_from_package(app, "fastarch.missing_pkg")

    assert "root package/module" in str(exc_info.value)
    assert "fastarch.missing_pkg" in str(exc_info.value)


def test_include_controllers_from_package_wraps_broken_nested_imports_from_fixture_package() -> (
    None
):
    with pytest.raises(ImportError) as exc_info:
        discovery.include_controllers_from_package(
            FastAPI(), "tests.fixtures.autodiscovery_broken_pkg"
        )

    assert "nested module" in str(exc_info.value)
    assert "tests.fixtures.autodiscovery_broken_pkg.broken" in str(exc_info.value)
    assert "tests.fixtures.autodiscovery_broken_pkg" in str(exc_info.value)
    assert isinstance(exc_info.value.__cause__, ImportError)
    assert "autodiscovery fixture nested import failure" in str(exc_info.value.__cause__)


def _build_controller(module_name: str, prefix: str) -> type[Any]:
    @controller(prefix)
    class GeneratedController:
        @get("/")
        def read(self) -> dict[str, str]:
            return {"module": module_name}

    GeneratedController.__module__ = module_name
    return GeneratedController


def _build_plain_class(module_name: str) -> type[Any]:
    class PlainClass:
        pass

    PlainClass.__module__ = module_name
    return PlainClass


def _record_include_calls(
    calls: list[tuple[Any, list[type[Any]], str]],
) -> Any:
    def fake_include_controllers(
        app_or_router: Any, controllers: Any, prefix: str = ""
    ) -> Any:
        calls.append((app_or_router, list(controllers), prefix))
        return app_or_router

    return fake_include_controllers


def _iter_routes(app: FastAPI) -> list[APIRoute]:
    collected: list[APIRoute] = []

    for route in app.router.routes:
        if isinstance(route, APIRoute):
            collected.append(route)
            continue

        nested_router = getattr(route, "original_router", None)
        if nested_router is None:
            continue

        collected.extend(
            inner for inner in nested_router.routes if isinstance(inner, APIRoute)
        )

    return collected


def _route_snapshot(
    app: FastAPI,
) -> list[tuple[str, tuple[str, ...], str | None, tuple[str, ...]]]:
    snapshots: list[tuple[str, tuple[str, ...], str | None, tuple[str, ...]]] = []

    for route in _iter_routes(app):
        dependency_calls = tuple(
            dependency.call.__name__ for dependency in route.dependant.dependencies
        )
        snapshots.append(
            (route.path, tuple(sorted(route.methods or ())), route.summary, dependency_calls)
        )

    return sorted(snapshots)
