from __future__ import annotations

import asyncio
import inspect
from typing import Annotated

from fastapi import Depends, FastAPI, Header
from fastapi.routing import APIRoute
from pydantic import BaseModel

from fastarch import controller, get, include_controllers, post


class CreateUserRequest(BaseModel):
    name: str


class UserResponse(BaseModel):
    name: str
    source: str
    request_id: str


def get_request_id() -> str:
    return "req-123"


def controller_dependency() -> None:
    return None


def controller_guard(x_token: Annotated[str, Header()]) -> None:
    return None


def route_dependency() -> None:
    return None


def route_guard() -> None:
    return None


@controller("/users", tags=("users",))
class UsersController:
    def __init__(self) -> None:
        self.source = "controller-state"

    @post(
        "/",
        response_model=UserResponse,
        status_code=201,
        tags=("write",),
        summary="Create user",
        description="Create one user",
        responses={409: {"description": "Conflict"}},
        operation_id="createUser",
    )
    async def create_user(
        self,
        payload: CreateUserRequest,
        request_id: Annotated[str, Depends(get_request_id)],
    ) -> dict[str, str]:
        return {
            "name": payload.name,
            "source": self.source,
            "request_id": request_id,
            "ignored": "filtered-by-response-model",
        }


@controller(
    "/secure",
    dependencies=(Depends(controller_dependency),),
    guards=(controller_guard,),
)
class SecureController:
    @get("/ping", dependencies=(Depends(route_dependency),), guards=(route_guard,))
    def ping(self) -> dict[str, bool]:
        return {"ok": True}


def _get_api_route(app: FastAPI, path: str, method: str) -> APIRoute:
    for route in app.router.routes:
        if (
            isinstance(route, APIRoute)
            and route.path == path
            and method in route.methods
        ):
            return route

        nested_router = getattr(route, "original_router", None)
        if nested_router is None:
            continue

        for nested_route in nested_router.routes:
            if (
                isinstance(nested_route, APIRoute)
                and nested_route.path == path
                and method in nested_route.methods
            ):
                return nested_route

    raise AssertionError(f"Route {method} {path} was not registered")


def test_include_controllers_builds_native_fastapi_dependency_graph_for_bound_methods() -> (
    None
):
    app = FastAPI()
    include_controllers(app, [UsersController], prefix="/api")
    route = _get_api_route(app, "/api/users/", "POST")
    openapi = app.openapi()
    operation = openapi["paths"]["/api/users/"]["post"]
    parameter_names = {
        parameter["name"] for parameter in operation.get("parameters", [])
    }

    assert route.status_code == 201
    assert route.response_model is UserResponse
    assert [parameter.name for parameter in route.dependant.body_params] == ["payload"]
    assert [parameter.name for parameter in route.dependant.path_params] == []
    assert [parameter.name for parameter in route.dependant.query_params] == []
    assert "self" not in parameter_names
    assert operation["requestBody"]["required"] is True
    result = asyncio.run(route.endpoint(CreateUserRequest(name="Ada"), "req-123"))

    assert result["name"] == "Ada"
    assert result["source"] == "controller-state"
    assert result["request_id"] == "req-123"


def test_include_controllers_merges_controller_and_route_dependencies_into_fastapi() -> (
    None
):
    app = FastAPI()
    include_controllers(app, [SecureController])
    route = _get_api_route(app, "/secure/ping", "GET")
    openapi = app.openapi()
    operation = openapi["paths"]["/secure/ping"]["get"]

    assert {parameter["name"] for parameter in operation.get("parameters", [])} == {
        "x-token"
    }
    assert [dependency.call for dependency in route.dependant.dependencies] == [
        controller_dependency,
        controller_guard,
        route_dependency,
        route_guard,
    ]
    assert route.endpoint is route.dependant.call
    assert inspect.signature(route.endpoint).parameters == {}
    assert route.endpoint() == {"ok": True}


def test_include_controllers_generates_openapi_without_self_and_with_metadata() -> None:
    app = FastAPI()
    include_controllers(app, [UsersController], prefix="/api")

    openapi = app.openapi()
    operation = openapi["paths"]["/api/users/"]["post"]
    parameter_names = {
        parameter["name"] for parameter in operation.get("parameters", [])
    }

    assert operation["summary"] == "Create user"
    assert operation["description"] == "Create one user"
    assert operation["operationId"] == "createUser"
    assert set(operation["tags"]) == {"users", "write"}
    assert operation["responses"]["201"]["content"]["application/json"]["schema"] == {
        "$ref": "#/components/schemas/UserResponse"
    }
    assert operation["responses"]["409"]["description"] == "Conflict"
    assert operation["requestBody"]["required"] is True
    assert "self" not in parameter_names
