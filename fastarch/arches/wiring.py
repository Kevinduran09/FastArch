"""Endpoint wiring metadata for Arches."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any, TypeVar

FASTARCH_WIRES_ATTR = "__fastarch_wires__"

FuncT = TypeVar("FuncT", bound=Callable[..., Any])


def wires(**mapping: Any) -> Callable[[FuncT], FuncT]:
    """Declare endpoint parameters that must be resolved by Arches.

    The decorator only stores metadata. The active Arch runtime converts this
    metadata to FastAPI Depends(...) entries during mount().
    """

    def decorator(func: FuncT) -> FuncT:
        setattr(func, FASTARCH_WIRES_ATTR, dict(mapping))
        return func

    return decorator
