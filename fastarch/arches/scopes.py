"""Dependency lifetime scopes for Arches."""

from __future__ import annotations

from enum import Enum


class Scope(str, Enum):
    """Supported Arches dependency lifetimes."""

    SINGLETON = "singleton"
    REQUEST = "request"
    TRANSIENT = "transient"
