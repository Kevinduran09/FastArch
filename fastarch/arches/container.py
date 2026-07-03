"""Private dependency resolution container for Arches."""

from __future__ import annotations

import inspect
from typing import Any, get_type_hints

from fastapi import Request

from fastarch.arches.binding import Binding
from fastarch.arches.errors import (
    CircularDependencyError,
    UnresolvedDependencyError,
    token_name,
)
from fastarch.arches.scopes import Scope

_REQUEST_CACHE_KEY = "__fastarch_arches_request_cache__"


class Container:
    """Internal dependency resolver used by a mounted Arch branch."""

    def __init__(self, bindings: dict[Any, Binding]) -> None:
        self._bindings = dict(bindings)
        self._singletons: dict[Any, Any] = {}

    def dependency(self, token: Any) -> Any:
        """Build a FastAPI dependency callable for a token."""

        async def dependency(request: Request) -> Any:
            return self.resolve(token, request=request)

        dependency.__name__ = f"resolve_{token_name(token)}"
        return dependency

    def resolve(
        self,
        token: Any,
        *,
        request: Request | None = None,
        stack: tuple[Any, ...] = (),
    ) -> Any:
        """Resolve a dependency token according to its binding scope."""

        binding = self._get_binding(token)

        if binding.scope == Scope.SINGLETON:
            if token not in self._singletons:
                self._singletons[token] = self._build(binding, request=request, stack=stack)
            return self._singletons[token]

        if binding.scope == Scope.REQUEST and request is not None:
            cache = _get_request_cache(request)
            if token not in cache:
                cache[token] = self._build(binding, request=request, stack=stack)
            return cache[token]

        return self._build(binding, request=request, stack=stack)

    def validate_token(self, token: Any) -> None:
        """Raise if the token is not available in this container."""

        self._get_binding(token)

    def _get_binding(self, token: Any) -> Binding:
        binding = self._bindings.get(token)
        if binding is None:
            raise UnresolvedDependencyError(
                f"{token_name(token)} is not bound in this Arch branch."
            )
        return binding

    def _build(
        self,
        binding: Binding,
        *,
        request: Request | None,
        stack: tuple[Any, ...],
    ) -> Any:
        token = binding.token
        implementation = binding.implementation

        if token in stack:
            cycle = " -> ".join(token_name(item) for item in (*stack, token))
            raise CircularDependencyError(f"Circular dependency detected: {cycle}")

        if not inspect.isclass(implementation):
            if callable(implementation):
                return implementation()
            return implementation

        signature = inspect.signature(implementation.__init__)
        type_hints = get_type_hints(implementation.__init__)
        kwargs: dict[str, Any] = {}

        for name, parameter in signature.parameters.items():
            if name == "self":
                continue
            if parameter.kind in (
                inspect.Parameter.VAR_POSITIONAL,
                inspect.Parameter.VAR_KEYWORD,
            ):
                continue

            dependency_token = type_hints.get(name, parameter.annotation)
            if dependency_token is inspect.Parameter.empty:
                if parameter.default is not inspect.Parameter.empty:
                    continue
                raise UnresolvedDependencyError(
                    f"Cannot resolve constructor parameter {name!r} for "
                    f"{token_name(implementation)} because it has no type annotation."
                )

            kwargs[name] = self.resolve(
                dependency_token,
                request=request,
                stack=(*stack, token),
            )

        return implementation(**kwargs)


def _get_request_cache(request: Request) -> dict[Any, Any]:
    cache = getattr(request.state, _REQUEST_CACHE_KEY, None)
    if cache is None:
        cache = {}
        setattr(request.state, _REQUEST_CACHE_KEY, cache)
    return cache
