"""Declarative Arch tree and mount compiler."""

from __future__ import annotations

import inspect
from dataclasses import dataclass, field
from typing import Annotated, Any

from fastapi import Depends

from fastarch.arches.binding import Binding
from fastarch.arches.container import Container
from fastarch.arches.errors import DuplicateBindingError, WireParameterError, token_name
from fastarch.arches.wiring import FASTARCH_WIRES_ATTR
from fastarch.registry import include_controllers
from fastarch.types import FASTARCH_ROUTE_DEFINITION_ATTR


@dataclass(frozen=True, slots=True)
class Arch:
    """Declarative architecture unit that compiles to FastAPI on mount()."""

    prefix: str = ""
    controllers: tuple[Any, ...] = ()
    wires: tuple[Binding, ...] = ()
    arches: tuple[Arch, ...] = ()

    def __init__(
        self,
        app_or_router: Any | None = None,
        *,
        prefix: str = "",
        controllers: list[Any] | tuple[Any, ...] | None = None,
        wires: list[Binding] | tuple[Binding, ...] | None = None,
        arches: list[Arch] | tuple[Arch, ...] | None = None,
    ) -> None:
        object.__setattr__(self, "prefix", prefix)
        object.__setattr__(self, "controllers", tuple(controllers or ()))
        object.__setattr__(self, "wires", tuple(wires or ()))
        object.__setattr__(self, "arches", tuple(arches or ()))

        if app_or_router is not None:
            self.mount(app_or_router)

    def mount(self, app_or_router: Any) -> Any:
        """Compile this Arch tree and register its controllers on FastAPI."""

        _mount_arch(
            app_or_router,
            arch=self,
            inherited_prefix="",
            inherited_bindings={},
        )
        return app_or_router


def _mount_arch(
    app_or_router: Any,
    *,
    arch: Arch,
    inherited_prefix: str,
    inherited_bindings: dict[Any, Binding],
) -> None:
    local_bindings = _merge_bindings(inherited_bindings, arch.wires)
    effective_prefix = _join_paths(inherited_prefix, arch.prefix)

    if arch.controllers:
        container = Container(local_bindings)
        _apply_wires_to_controllers(arch.controllers, container)
        include_controllers(app_or_router, arch.controllers, prefix=effective_prefix)

    for child in arch.arches:
        _mount_arch(
            app_or_router,
            arch=child,
            inherited_prefix=effective_prefix,
            inherited_bindings=local_bindings,
        )


def _merge_bindings(
    inherited: dict[Any, Binding], local: tuple[Binding, ...]
) -> dict[Any, Binding]:
    merged = dict(inherited)
    seen_local: set[Any] = set()

    for binding in local:
        if binding.token in seen_local:
            raise DuplicateBindingError(
                f"{token_name(binding.token)} is bound more than once in the same Arch."
            )
        seen_local.add(binding.token)
        merged[binding.token] = binding

    return merged


def _apply_wires_to_controllers(controllers: tuple[Any, ...], container: Container) -> None:
    for controller in controllers:
        controller_type = controller if inspect.isclass(controller) else type(controller)
        for _, member in controller_type.__dict__.items():
            if getattr(member, FASTARCH_ROUTE_DEFINITION_ATTR, None) is None:
                continue
            _apply_wires_to_endpoint(member, container)


def _apply_wires_to_endpoint(endpoint: Any, container: Container) -> None:
    mapping = getattr(endpoint, FASTARCH_WIRES_ATTR, None)
    if not mapping:
        return

    signature = inspect.signature(endpoint)
    parameters = []

    for name, parameter in signature.parameters.items():
        if name not in mapping:
            parameters.append(parameter)
            continue

        token = mapping[name]
        container.validate_token(token)
        annotation = Annotated[token, Depends(container.dependency(token))]
        parameters.append(parameter.replace(annotation=annotation))

    missing = set(mapping) - set(signature.parameters)
    if missing:
        missing_list = ", ".join(sorted(missing))
        raise WireParameterError(
            f"@wires references missing parameter(s) {missing_list} in {endpoint.__name__}."
        )

    endpoint.__signature__ = signature.replace(parameters=parameters)


def _join_paths(*segments: str) -> str:
    normalized = [segment.strip("/") for segment in segments if segment and segment != "/"]
    if not normalized:
        return ""
    return "/" + "/".join(normalized)
