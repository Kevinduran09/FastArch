"""Route decorators for FastArch."""

from __future__ import annotations

from collections.abc import Callable, Sequence
from typing import Any, cast

from fastarch.types import FASTARCH_ROUTE_DEFINITION_ATTR, HttpMethod, RouteDefinition


def route(
    path: str,
    *,
    methods: Sequence[str],
    response_model: Any | None = None,
    status_code: int | None = None,
    tags: Sequence[str] | None = None,
    dependencies: Sequence[Any] | None = None,
    guards: Sequence[Any] | None = None,
    summary: str | None = None,
    description: str | None = None,
    responses: dict[int | str, Any] | None = None,
    name: str | None = None,
    operation_id: str | None = None,
    deprecated: bool | None = None,
    include_in_schema: bool = True,
    response_description: str | None = None,
    **kwargs: Any,
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """Attach metadata to a function for FastAPI route registration.

    This decorator marks a function as a FastArch route and stores metadata
    that will be used during controller registration. It does not wrap the
    function or modify its behavior.

    Args:
        path: URL path for this route (relative to controller prefix).
        methods: Sequence of HTTP methods (e.g., ["GET", "POST"]).
        response_model: Pydantic model for response serialization and validation.
        status_code: Default HTTP status code for successful responses.
        tags: Sequence of OpenAPI tags for documentation grouping.
        dependencies: Sequence of `Depends()` objects for route-level dependencies.
        guards: Sequence of callables for route-level authorization/security.
                Guards are converted to `Depends()` during registration.
        summary: Short description for OpenAPI documentation.
        description: Detailed description for OpenAPI documentation.
        responses: Mapping of status codes to response descriptions for OpenAPI.
        name: Internal name for the route (used by FastAPI routing).
        operation_id: Custom operation ID for OpenAPI (used by code generators).
        deprecated: Mark route as deprecated in OpenAPI documentation.
        include_in_schema: Whether to include this route in OpenAPI schema.
        response_description: Description of the response for OpenAPI.
        **kwargs: Additional metadata passed through to FastAPI route extras.

    Returns:
        A decorator function that attaches `RouteDefinition` to the function.

    Example:
        ```python
        @get("/users/{id}", response_model=UserSchema)
        def get_user(id: int):
            return {"id": id}

        @post("/users", status_code=201, guards=(require_admin,))
        def create_user(data: UserCreate):
            return {"id": 1}
        ```

    Notes:
        - Routes only become active when their controller is registered via `include_controllers()`.
        - Method names are normalized to uppercase.
        - Guards execute before the route handler (after dependencies).
    """

    normalized_methods = tuple(cast(HttpMethod, method.upper()) for method in methods)
    definition = RouteDefinition(
        path=path,
        methods=normalized_methods,
        response_model=response_model,
        status_code=status_code,
        tags=tuple(tags or ()),
        dependencies=tuple(dependencies or ()),
        guards=tuple(guards or ()),
        summary=summary,
        description=description,
        responses=dict(responses or {}),
        name=name,
        operation_id=operation_id,
        deprecated=deprecated,
        include_in_schema=include_in_schema,
        response_description=response_description,
        extras=dict(kwargs),
    )

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        setattr(func, FASTARCH_ROUTE_DEFINITION_ATTR, definition)
        return func

    return decorator


def get(path: str, **kwargs: Any) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """Decorator for HTTP GET routes.

    Shorthand for `route(path, methods=["GET"], ...)`.

    Args:
        path: URL path for this route.
        **kwargs: Additional arguments passed to `route()`.

    Returns:
        A decorator function.

    Example:
        ```python
        @get("/users")
        def list_users():
            return []
        ```
    """
    return route(path, methods=("GET",), **kwargs)


def post(path: str, **kwargs: Any) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """Decorator for HTTP POST routes.

    Shorthand for `route(path, methods=["POST"], ...)`.
    """
    return route(path, methods=("POST",), **kwargs)


def put(path: str, **kwargs: Any) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """Decorator for HTTP PUT routes.

    Shorthand for `route(path, methods=["PUT"], ...)`.
    """
    return route(path, methods=("PUT",), **kwargs)


def patch(path: str, **kwargs: Any) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """Decorator for HTTP PATCH routes.

    Shorthand for `route(path, methods=["PATCH"], ...)`.
    """
    return route(path, methods=("PATCH",), **kwargs)


def delete(path: str, **kwargs: Any) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """Decorator for HTTP DELETE routes.

    Shorthand for `route(path, methods=["DELETE"], ...)`.
    """
    return route(path, methods=("DELETE",), **kwargs)
