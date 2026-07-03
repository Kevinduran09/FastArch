"""Fluent binding definitions for Arches."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, TypeVar

from fastarch.arches.scopes import Scope

T = TypeVar("T")


@dataclass(frozen=True, slots=True)
class Binding:
    """A dependency binding from a token to an implementation."""

    token: Any
    implementation: Any
    scope: Scope


@dataclass(frozen=True, slots=True)
class BindingBuilder:
    """Fluent API used by bind(...)."""

    token: Any
    implementation: Any | None = None

    def to(self, implementation: Any) -> BindingBuilder:
        """Bind the token to a concrete implementation."""

        return BindingBuilder(token=self.token, implementation=implementation)

    def singleton(self) -> Binding:
        """Resolve this binding once for the application lifetime."""

        return self._build(Scope.SINGLETON)

    def request(self) -> Binding:
        """Resolve this binding once per request dependency graph."""

        return self._build(Scope.REQUEST)

    def transient(self) -> Binding:
        """Resolve a new instance every time the token is requested."""

        return self._build(Scope.TRANSIENT)

    def _build(self, scope: Scope) -> Binding:
        return Binding(
            token=self.token,
            implementation=self.implementation or self.token,
            scope=scope,
        )


def bind(token: Any) -> BindingBuilder:
    """Start a fluent dependency binding definition."""

    return BindingBuilder(token=token)
