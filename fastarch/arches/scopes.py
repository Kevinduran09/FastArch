"""Dependency lifetime scopes for Arches."""

from __future__ import annotations

from enum import StrEnum


class Scope(StrEnum):
    """Supported Arches dependency lifetimes."""

    SINGLETON = "singleton"
    REQUEST = "request"
    TRANSIENT = "transient"
