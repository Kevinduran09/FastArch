"""Public package surface for the FastArch MVP."""

from __future__ import annotations

from fastarch.__version__ import __version__
from fastarch.controllers import controller
from fastarch.discovery import include_controllers_from_package
from fastarch.registry import include_controllers
from fastarch.routes import delete, get, patch, post, put, route

__all__ = [
    "__version__",
    "controller",
    "route",
    "get",
    "post",
    "put",
    "patch",
    "delete",
    "include_controllers",
    "include_controllers_from_package",
]
