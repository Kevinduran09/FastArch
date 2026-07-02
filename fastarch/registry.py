"""Controller registration for FastArch."""

from __future__ import annotations

import inspect
from collections.abc import Iterable
from typing import Any

from fastapi import APIRouter, Depends

from fastarch.types import (
    FASTARCH_CONTROLLER_DEFINITION_ATTR,
    FASTARCH_ROUTE_DEFINITION_ATTR,
    ControllerDefinition,
    RouteDefinition,
)


def include_controllers(
    app_or_router: Any, controllers: Iterable[Any], prefix: str = ""
) -> Any:
    """Register FastArch controllers on a FastAPI app or router.

    This function discovers all `@route`-decorated methods in the provided
    controllers and registers them as routes on the app/router, automatically
    handling dependencies, guards, and metadata.

    Args:
        app_or_router: FastAPI app or APIRouter instance.
        controllers: Iterable of controller classes or instances.
        prefix: Global URL prefix prepended to all controller prefixes.

    Returns:
        The `app_or_router` argument (for chaining).

    Raises:
        TypeError: If app_or_router does not have `include_router()` method,
                   or if a controller is not decorated with `@controller()`,
                   or if a controller class cannot be instantiated.

    Example:
        ```python
        app = FastAPI()
        include_controllers(app, [UsersController, HealthController], prefix="/api/v1")
        ```

    Notes:
        - Controllers are instantiated automatically if passed as classes.
        - Class-based controllers must accept zero arguments.
        - Pre-instantiated controllers can have constructor dependencies.
        - Dependencies and guards are merged in order:
          controller dependencies → controller guards → route dependencies → route guards.
    """

    include_router = getattr(app_or_router, "include_router", None)
    if not callable(include_router):
        raise TypeError("FastArch registration target must expose include_router().")

    global_prefix = _normalize_prefix(prefix)

    for controller in controllers:
        instance = _resolve_controller(controller)
        router = _build_controller_router(instance, global_prefix)
        include_router(router)

    return app_or_router


def _resolve_controller(controller: Any) -> Any:
    """Resolve a controller class or instance to a single instance.

    If a class is passed, it is instantiated with no arguments.
    If an instance is passed, it is returned as-is (but type is still validated).

    Args:
        controller: Class or instance to resolve.

    Returns:
        An instance of the controller.

    Raises:
        TypeError: If controller class cannot be instantiated or is missing metadata.
    """
    if inspect.isclass(controller):
        _get_controller_definition(controller)

        try:
            return controller()
        except TypeError as error:
            raise TypeError(
                f"Controller class {controller.__name__!r} must be instantiated with no arguments."
            ) from error

    _get_controller_definition(type(controller))
    return controller


def _build_controller_router(controller: Any, global_prefix: str) -> APIRouter:
    """Build an APIRouter from a controller instance and global prefix.

    Discovers all route-decorated methods, merges their metadata with
    controller-level metadata, and registers them as API routes.

    Args:
        controller: An instance of a controller class.
        global_prefix: The global prefix to prepend to controller prefix.

    Returns:
        A FastAPI APIRouter ready to be included in an app.
    """
    controller_definition = _get_controller_definition(type(controller))
    router = APIRouter(
        prefix=_join_paths(global_prefix, controller_definition.prefix),
        tags=list(controller_definition.tags) or None,
        responses=dict(controller_definition.responses) or None,
        **dict(controller_definition.extras),
    )

    for route_name, route_definition in _iter_route_definitions(type(controller)):
        endpoint = getattr(controller, route_name)
        merged_dependencies = _merge_dependencies(
            controller_definition, route_definition
        )
        route_kwargs = _build_route_kwargs(route_definition, merged_dependencies)
        router.add_api_route(
            route_definition.path,
            endpoint,
            methods=list(route_definition.methods),
            **route_kwargs,
        )

    return router


def _iter_route_definitions(
    controller_type: type[Any],
) -> list[tuple[str, RouteDefinition]]:
    """Discover all route-decorated methods in a controller class.

    Iterates through class members in definition order and returns those with
    `RouteDefinition` metadata.

    Args:
        controller_type: The controller class to inspect.

    Returns:
        List of (method_name, RouteDefinition) tuples.
    """
    routes: list[tuple[str, RouteDefinition]] = []

    for name, member in controller_type.__dict__.items():
        if isinstance(member, (staticmethod, classmethod)):
            member = member.__func__

        if not callable(member):
            continue

        definition = getattr(member, FASTARCH_ROUTE_DEFINITION_ATTR, None)
        if definition is not None:
            routes.append((name, definition))

    return routes


def _get_controller_definition(controller_type: type[Any]) -> ControllerDefinition:
    """Retrieve the ControllerDefinition attached to a controller class.

    Args:
        controller_type: The controller class to inspect.

    Returns:
        The ControllerDefinition attached to the class.

    Raises:
        TypeError: If the class is not decorated with @controller().
    """
    definition = getattr(controller_type, FASTARCH_CONTROLLER_DEFINITION_ATTR, None)
    if definition is None:
        raise TypeError("FastArch controllers must be decorated with @controller(...).")
    return definition


def _merge_dependencies(
    controller_definition: ControllerDefinition, definition: RouteDefinition
) -> list[Any] | None:
    """Merge controller-level and route-level dependencies and guards.

    Combines dependencies in the following order:
    1. Controller-level dependencies
    2. Controller-level guards (converted to Depends)
    3. Route-level dependencies
    4. Route-level guards (converted to Depends)

    This ensures controller logic runs before route-specific logic.

    Args:
        controller_definition: Metadata from the controller decorator.
        definition: Metadata from the route decorator.

    Returns:
        Merged list of Depends objects, or None if empty.
    """
    merged_dependencies = list(controller_definition.dependencies)
    merged_dependencies.extend(Depends(guard) for guard in controller_definition.guards)
    merged_dependencies.extend(definition.dependencies)
    merged_dependencies.extend(Depends(guard) for guard in definition.guards)
    return merged_dependencies or None


def _build_route_kwargs(
    definition: RouteDefinition, merged_dependencies: list[Any] | None
) -> dict[str, Any]:
    """Build kwargs for FastAPI's add_api_route() method.

    Extracts and formats all metadata from a RouteDefinition into a dict
    that FastAPI expects, filtering out None values where appropriate.

    Args:
        definition: Metadata from the route decorator.
        merged_dependencies: Pre-merged controller + route dependencies and guards.

    Returns:
        Dict of kwargs ready for FastAPI's add_api_route().
    """
    route_kwargs: dict[str, Any] = {
        "tags": list(definition.tags) or None,
        "dependencies": merged_dependencies,
        "summary": definition.summary,
        "description": definition.description,
        "responses": dict(definition.responses) or None,
        "deprecated": definition.deprecated,
        "include_in_schema": definition.include_in_schema,
        "name": definition.name,
        "operation_id": definition.operation_id,
        **dict(definition.extras),
    }

    if definition.response_model is not None:
        route_kwargs["response_model"] = definition.response_model
    if definition.status_code is not None:
        route_kwargs["status_code"] = definition.status_code
    if definition.response_description is not None:
        route_kwargs["response_description"] = definition.response_description

    return route_kwargs


def _join_paths(*segments: str) -> str:
    """Join multiple path segments into a single path.

    Strips leading/trailing slashes and normalizes separators.

    Args:
        *segments: Path segments to join.

    Returns:
        Normalized path with leading slash (or empty string if no segments).

    Example:
        >>> _join_paths("/api", "v1", "users/") -> "/api/v1/users"
    """
    normalized = [
        segment.strip("/") for segment in segments if segment and segment != "/"
    ]
    if not normalized:
        return ""
    return "/" + "/".join(normalized)


def _normalize_prefix(prefix: str) -> str:
    """Normalize a URL prefix.

    Args:
        prefix: Raw prefix string.

    Returns:
        Normalized prefix suitable for APIRouter.
    """
    return _join_paths(prefix)
