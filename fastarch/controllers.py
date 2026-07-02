"""Controller decorators for FastArch."""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any, TypeVar

from fastarch.types import FASTARCH_CONTROLLER_DEFINITION_ATTR, ControllerDefinition

_ControllerT = TypeVar("_ControllerT", bound=type[Any])


def controller(
    prefix: str = "",
    *,
    tags: Sequence[str] | None = None,
    dependencies: Sequence[Any] | None = None,
    guards: Sequence[Any] | None = None,
    responses: dict[int | str, Any] | None = None,
    **kwargs: Any,
) -> Any:
    """Attach metadata to a class for FastAPI controller registration.

    This decorator marks a class as a FastArch controller and stores metadata
    that will be used during registration with `include_controllers()`. It does
    not register the class or wrap any methods.

    Args:
        prefix: URL path prefix for all routes in this controller (e.g., "/users").
        tags: Sequence of OpenAPI tags for documentation and grouping.
        dependencies: Sequence of `Depends()` objects for controller-level dependencies.
        guards: Sequence of callables for controller-level authorization/security.
                Guards are converted to `Depends()` during registration.
        responses: Mapping of status codes to response schemas for OpenAPI docs.
        **kwargs: Additional metadata passed through to FastAPI router extras.

    Returns:
        A decorator function that attaches `ControllerDefinition` to the class.

    Raises:
        TypeError: If the decorated object is not a class.

    Example:
        ```python
        @controller("/users", tags=["users"])
        class UsersController:
            @get("/{id}")
            def get_user(self, id: int):
                return {"id": id}
        ```

    Notes:
        - Controllers must be registered via `include_controllers()` to become routes.
        - Class instances must accept zero arguments or be pre-instantiated.
    """

    definition = ControllerDefinition(
        prefix=prefix,
        tags=tuple(tags or ()),
        dependencies=tuple(dependencies or ()),
        guards=tuple(guards or ()),
        responses=dict(responses or {}),
        extras=dict(kwargs),
    )

    def decorator(cls: _ControllerT) -> _ControllerT:
        setattr(cls, FASTARCH_CONTROLLER_DEFINITION_ATTR, definition)
        return cls

    return decorator
