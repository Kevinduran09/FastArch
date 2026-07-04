from __future__ import annotations

import inspect

from fastarch import delete, route
from fastarch.types import FASTARCH_ROUTE_DEFINITION_ATTR


def test_route_stores_metadata_without_wrapping_callable() -> None:
    dependency = object()

    def audit_guard() -> None:
        return None

    def endpoint(user_id: str) -> dict[str, str]:
        return {"user_id": user_id}

    decorated = route(
        "/{user_id}",
        methods=("GET", "POST"),
        response_model=dict,
        status_code=202,
        tags=("users",),
        dependencies=(dependency,),
        guards=(audit_guard,),
        summary="Get user",
        description="Fetch one user",
        responses={404: {"description": "Not found"}},
        name="get_user",
        operation_id="getUser",
        deprecated=False,
        include_in_schema=False,
        response_description="A user payload",
        audit="enabled",
    )(endpoint)

    definition = getattr(decorated, FASTARCH_ROUTE_DEFINITION_ATTR)

    assert decorated is endpoint
    assert inspect.signature(decorated) == inspect.signature(endpoint)
    assert definition.path == "/{user_id}"
    assert definition.methods == ("GET", "POST")
    assert definition.response_model is dict
    assert definition.status_code == 202
    assert definition.tags == ("users",)
    assert definition.dependencies == (dependency,)
    assert definition.guards == (audit_guard,)
    assert callable(definition.guards[0])
    assert definition.summary == "Get user"
    assert definition.description == "Fetch one user"
    assert definition.responses == {404: {"description": "Not found"}}
    assert definition.name == "get_user"
    assert definition.operation_id == "getUser"
    assert definition.deprecated is False
    assert definition.include_in_schema is False
    assert definition.response_description == "A user payload"
    assert definition.extras == {"audit": "enabled"}


def test_http_helpers_delegate_to_route_metadata() -> None:
    def delete_guard() -> None:
        return None

    @delete("/{user_id}", summary="Delete user", guards=(delete_guard,))
    def delete_user(user_id: str) -> dict[str, str]:
        return {"user_id": user_id}

    definition = getattr(delete_user, FASTARCH_ROUTE_DEFINITION_ATTR)

    assert definition.methods == ("DELETE",)
    assert definition.summary == "Delete user"
    assert definition.guards == (delete_guard,)
