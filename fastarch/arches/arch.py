"""Declarative Arch tree definition."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from fastarch.arches.binding import Binding


@dataclass(frozen=True, slots=True, init=False)
class Arch:
    """Declarative architecture unit for Arches.

    Arch stores architecture metadata only. It does not register routes,
    resolve dependencies, create service instances, or mutate FastAPI.
    Runtime compilation will be introduced in a later batch through mount().
    """

    prefix: str = ""
    controllers: tuple[Any, ...] = ()
    wires: tuple[Binding, ...] = ()
    arches: tuple[Arch, ...] = ()

    def __init__(
        self,
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
