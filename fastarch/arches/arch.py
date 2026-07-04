"""Declarative Arch tree definition."""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any

from fastarch.arches.binding import Binding


@dataclass(frozen=True, slots=True)
class Arch:
    """Declarative architecture unit for Arches.

    Arch stores architecture metadata only. It does not register routes,
    resolve dependencies, create service instances, or mutate FastAPI.
    Runtime compilation will be introduced in a later batch through mount().
    """

    prefix: str = ""
    controllers: tuple[Any, ...] | list[Any] = field(default_factory=tuple)
    wires: tuple[Binding, ...] | list[Binding] = field(default_factory=tuple)
    arches: tuple[Arch, ...] | list[Arch] | Arch = field(default_factory=tuple)

    def __post_init__(self) -> None:
        normalized_controllers = tuple(self.controllers or ())
        normalized_wires = tuple(self.wires or ())
        if isinstance(self.arches, Arch):
            iterable_arche = (self.arches,)
            normalized_arches = iterable_arche
        else:
            normalized_arches = tuple(self.arches or ())
        object.__setattr__(self, "controllers", normalized_controllers)
        object.__setattr__(self, "wires", normalized_wires)
        object.__setattr__(self, "arches", normalized_arches)
