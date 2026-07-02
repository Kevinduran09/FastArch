from __future__ import annotations

import inspect

from fastapi import FastAPI
from fastapi.routing import APIRoute

from fastarch import controller, get, include_controllers


def _get_api_route(app: FastAPI, path: str, method: str) -> APIRoute:
    for route in _iter_routes(app):
        if route.path == path and method in route.methods:
            return route

    raise AssertionError(f"Route {method} {path} was not registered")


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


def test_include_controllers_registers_bound_methods_for_zero_arg_classes() -> None:
    @controller("/users")
    class UsersController:
        def __init__(self) -> None:
            self.source = "controller-state"

        @get("/{user_id}")
        def read_user(self, user_id: str) -> dict[str, str]:
            return {"user_id": user_id, "source": self.source}

    app = FastAPI()

    include_controllers(app, [UsersController], prefix="/api")

    route = _get_api_route(app, "/api/users/{user_id}", "GET")

    assert route.endpoint("123") == {"user_id": "123", "source": "controller-state"}


def test_include_controllers_keeps_bound_methods_private_for_classes_and_instances() -> (
    None
):
    @controller("/class")
    class ClassController:
        def __init__(self) -> None:
            self.source = "class"

        @get("/ping")
        def ping(self) -> dict[str, str]:
            return {"source": self.source}

    @controller("/instance")
    class InstanceController:
        def __init__(self) -> None:
            self.source = "instance"

        @get("/ping")
        def ping(self) -> dict[str, str]:
            return {"source": self.source}

    instance = InstanceController()
    app = FastAPI()

    include_controllers(app, [ClassController, instance])

    class_route = _get_api_route(app, "/class/ping", "GET")
    instance_route = _get_api_route(app, "/instance/ping", "GET")

    assert class_route.endpoint is class_route.dependant.call
    assert inspect.signature(class_route.endpoint).parameters == {}
    assert class_route.endpoint.__self__.__class__ is ClassController
    assert class_route.endpoint() == {"source": "class"}

    assert instance_route.endpoint is instance_route.dependant.call
    assert inspect.signature(instance_route.endpoint).parameters == {}
    assert instance_route.endpoint.__self__ is instance
    assert instance_route.endpoint() == {"source": "instance"}


def test_include_controllers_supports_multiple_controllers_and_prefix_composition() -> (
    None
):
    @controller("/users")
    class UsersController:
        @get("/{user_id}")
        def read_user(self, user_id: str) -> dict[str, str]:
            return {"user_id": user_id}

    @controller("/health")
    class HealthController:
        def __init__(self) -> None:
            self.ready = True

        @get("")
        def readiness(self) -> dict[str, bool]:
            return {"ready": self.ready}

    app = FastAPI()

    include_controllers(app, [UsersController(), HealthController], prefix="/v1")

    user_route = _get_api_route(app, "/v1/users/{user_id}", "GET")
    health_route = _get_api_route(app, "/v1/health", "GET")

    assert user_route.endpoint("abc") == {"user_id": "abc"}
    assert health_route.endpoint() == {"ready": True}


def test_include_controllers_preserves_method_definition_order() -> None:
    @controller("/ordered")
    class OrderedController:
        @get("/first")
        def first(self) -> dict[str, str]:
            return {"order": "first"}

        @get("/second")
        def second(self) -> dict[str, str]:
            return {"order": "second"}

        @get("/third")
        def third(self) -> dict[str, str]:
            return {"order": "third"}

    app = FastAPI()

    include_controllers(app, [OrderedController])

    route_paths = [
        route.path for route in _iter_routes(app) if route.path.startswith("/ordered")
    ]

    assert route_paths == ["/ordered/first", "/ordered/second", "/ordered/third"]


def test_include_controllers_rejects_invalid_controller_inputs() -> None:
    class MissingMetadata:
        pass

    @controller("/broken")
    class NeedsArgsController:
        def __init__(self, value: str) -> None:
            self.value = value

    app = FastAPI()

    try:
        include_controllers(app, [MissingMetadata])
    except TypeError as error:
        assert "FastArch controllers must be decorated" in str(error)
    else:
        raise AssertionError("Expected invalid controller metadata to raise TypeError")

    try:
        include_controllers(app, [NeedsArgsController])
    except TypeError as error:
        assert "must be instantiated with no arguments" in str(error)
    else:
        raise AssertionError("Expected non-zero-arg controller to raise TypeError")
