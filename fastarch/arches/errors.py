"""Arches-specific errors."""

from __future__ import annotations

from typing import Any


class ArchesError(Exception):
    """Base error for Arches."""


class DuplicateBindingError(ArchesError):
    """Raised when the same token is bound twice in the same Arch."""


class UnresolvedDependencyError(ArchesError):
    """Raised when a token cannot be resolved from the active Arch branch."""


class CircularDependencyError(ArchesError):
    """Raised when constructor injection finds a dependency cycle."""


class WireParameterError(ArchesError):
    """Raised when @wires references an invalid endpoint parameter."""


def token_name(token: Any) -> str:
    """Return a readable name for a dependency token."""

    return getattr(token, "__qualname__", getattr(token, "__name__", repr(token)))
