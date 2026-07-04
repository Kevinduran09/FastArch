"""Shared metadata definitions for FastArch decorators and registry."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal
from collections.abc import Callable

FASTARCH_CONTROLLER_DEFINITION_ATTR = "__fastarch_controller_definition__"
FASTARCH_ROUTE_DEFINITION_ATTR = "__fastarch_route_definition__"

HttpMethod = Literal["GET", "POST", "PUT", "PATCH", "DELETE"]


@dataclass(frozen=True, slots=True)
class ControllerDefinition:
    prefix: str = ""
    tags: tuple[str, ...] = ()
    dependencies: tuple[Any, ...] = ()
    guards: tuple[Callable[..., Any], ...] = ()
    responses: dict[int | str, Any] = field(default_factory=dict)
    extras: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class RouteDefinition:
    path: str
    methods: tuple[HttpMethod, ...]
    response_model: Any | None = None
    status_code: int | None = None
    tags: tuple[str, ...] = ()
    dependencies: tuple[Any, ...] = ()
    guards: tuple[Callable[..., Any], ...] = ()
    summary: str | None = None
    description: str | None = None
    responses: dict[int | str, Any] = field(default_factory=dict)
    name: str | None = None
    operation_id: str | None = None
    deprecated: bool | None = None
    include_in_schema: bool = True
    response_description: str | None = None
    extras: dict[str, Any] = field(default_factory=dict)
