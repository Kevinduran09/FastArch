from dataclasses import dataclass
from typing import Any

from fastarch.arches.arch import Arch
from fastarch.arches.binding import Binding
from fastarch.arches.errors import DuplicateBindingError


@dataclass(frozen=True, slots=True)
class CompiledArch:
    prefix: str
    controllers: tuple[Any, ...]
    bindings: dict[Any, Binding]


def compile_arch(arch: Arch) -> list[CompiledArch]:
    compiled = []

    walk_arch(arch=arch, inherited_prefix="", inherited_bindings={}, compiled=compiled)
    return compiled


def walk_arch(
    arch: Arch,
    inherited_prefix: str,
    inherited_bindings: dict[Any, Binding],
    compiled: list[CompiledArch],
) -> None:
    local_prefix = join_paths(inherited_prefix, arch.prefix)

    effective_bindings = merge_bindings(
        inherited_bindings,
        arch.wires,
    )

    if arch.controllers:
        compiled.append(
            CompiledArch(
                prefix=local_prefix,
                controllers=arch.controllers,
                bindings=effective_bindings,
            )
        )

    for sub_arch in arch.arches:
        walk_arch(
            arch=sub_arch,
            inherited_prefix=local_prefix,
            inherited_bindings=effective_bindings,
            compiled=compiled,
        )


def join_paths(*args: str) -> str:
    segments = [
        segmented.strip("/") for segmented in args if segmented and segmented != "/"
    ]
    return "/" + "/".join(segments)


def merge_bindings(
    inherited_bindings: dict[Any, Binding],
    wires: tuple[Binding, ...],
) -> dict[Any, Binding]:
    merged = dict(inherited_bindings)
    seen_local = set()
    for binding in wires:
        token = binding.token
        # Valida que no hayan repeditos dentro del mismo wires
        if token in seen_local:
            raise DuplicateBindingError(
                f"{token} is bound more than once in the same Arch."
            )
        seen_local.add(token)
        merged[token] = binding

    return merged
