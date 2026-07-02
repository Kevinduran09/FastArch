from __future__ import annotations

from fastapi import FastAPI
from fastapi.routing import APIRoute

from examples.fastapi_backend.app import (
    UserCreate,
    audit_create_user,
    audit_users_access,
    create_app,
    require_demo_token,
    require_write_token,
)


def _get_api_route(app: FastAPI, path: str, method: str) -> APIRoute:
    for route in app.router.routes:
        if isinstance(route, APIRoute) and route.path == path and method in route.methods:
            return route

        nested_router = getattr(route, "original_router", None)
        if nested_router is None:
            continue

        for nested_route in nested_router.routes:
            if isinstance(nested_route, APIRoute) and nested_route.path == path and method in nested_route.methods:
                return nested_route

    raise AssertionError(f"Route {method} {path} was not registered")


def test_example_app_registers_health_and_user_routes() -> None:
    app = create_app()
    health_route = _get_api_route(app, "/api/v1/health", "GET")
    list_route = _get_api_route(app, "/api/v1/users/", "GET")
    create_route = _get_api_route(app, "/api/v1/users/", "POST")
    openapi = app.openapi()

    assert health_route.endpoint() == {"ok": True}
    assert [user.id for user in list_route.endpoint()] == [1]
    assert create_route.status_code == 201
    assert openapi["paths"]["/api/v1/users/"]["post"]["summary"] == "Create user"
    assert openapi["paths"]["/api/v1/health"]["get"]["summary"] == "Readiness probe"


def test_example_app_uses_in_memory_service_state() -> None:
    app = create_app()
    list_route = _get_api_route(app, "/api/v1/users/", "GET")
    create_route = _get_api_route(app, "/api/v1/users/", "POST")

    created = create_route.endpoint(UserCreate(name="Grace Hopper"))
    users = list_route.endpoint()

    assert created.id == 2
    assert created.name == "Grace Hopper"
    assert [user.name for user in users] == ["Ada Lovelace", "Grace Hopper"]


def test_example_app_exposes_guard_order_through_fastapi_routes() -> None:
    app = create_app()
    list_route = _get_api_route(app, "/api/v1/users/", "GET")
    create_route = _get_api_route(app, "/api/v1/users/", "POST")
    openapi = app.openapi()

    assert [dependency.call for dependency in list_route.dependant.dependencies] == [
        audit_users_access,
        require_demo_token,
    ]
    assert [dependency.call for dependency in create_route.dependant.dependencies] == [
        audit_users_access,
        require_demo_token,
        audit_create_user,
        require_write_token,
    ]
    assert {parameter["name"] for parameter in openapi["paths"]["/api/v1/users/"]["get"].get("parameters", [])} == {
        "x-demo-token"
    }
    assert {parameter["name"] for parameter in openapi["paths"]["/api/v1/users/"]["post"].get("parameters", [])} == {
        "x-demo-token",
        "x-write-token",
    }
