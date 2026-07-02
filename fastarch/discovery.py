"""Controller autodiscovery entry point for FastArch."""

from __future__ import annotations

import importlib
import inspect
import pkgutil
from collections.abc import Iterator
from types import ModuleType
from typing import Any

from fastarch.registry import include_controllers
from fastarch.types import FASTARCH_CONTROLLER_DEFINITION_ATTR


def include_controllers_from_package(
    app_or_router: Any, package: str | ModuleType, prefix: str = ""
) -> Any:
    """Register controllers discovered from a package or module root."""

    root_module = _resolve_package_module(package)
    controllers = _discover_controllers(root_module)
    return include_controllers(app_or_router, controllers, prefix=prefix)


def _resolve_package_module(package: str | ModuleType) -> ModuleType:
    """Resolve a discovery target to an imported module object."""

    if isinstance(package, ModuleType):
        return package

    if isinstance(package, str):
        try:
            return importlib.import_module(package)
        except ImportError as error:
            raise ImportError(
                f"Could not import FastArch discovery root package/module {package!r}."
            ) from error

    raise TypeError(
        "FastArch discovery target must be a module object or dotted import string."
    )


def _discover_controllers(root_module: ModuleType) -> list[type[Any]]:
    """Discover decorated controller classes from a module tree."""

    controllers: list[type[Any]] = []
    seen: set[tuple[str, str]] = set()

    for module in _iter_discovery_modules(root_module):
        for controller_type in _iter_module_controller_classes(module):
            controller_key = (controller_type.__module__, controller_type.__qualname__)
            if controller_key in seen:
                continue

            seen.add(controller_key)
            controllers.append(controller_type)

    return controllers


def _iter_discovery_modules(root_module: ModuleType) -> Iterator[ModuleType]:
    """Yield the root module and any recursively discovered child modules."""

    yield root_module

    package_paths = getattr(root_module, "__path__", None)
    if package_paths is None:
        return

    root_name = root_module.__name__
    child_modules = sorted(
        pkgutil.walk_packages(package_paths, prefix=f"{root_name}."),
        key=lambda module_info: module_info.name,
    )

    for module_info in child_modules:
        yield _import_nested_module(module_info.name, root_name)


def _import_nested_module(module_name: str, root_name: str) -> ModuleType:
    """Import a discovered child module with nested-scan error context."""

    try:
        return importlib.import_module(module_name)
    except ImportError as error:
        raise ImportError(
            "Could not import FastArch discovery nested module "
            f"{module_name!r} while scanning root package/module {root_name!r}."
        ) from error


def _iter_module_controller_classes(module: ModuleType) -> Iterator[type[Any]]:
    """Yield decorated controller classes defined directly in a module."""

    for _, member in inspect.getmembers(module, inspect.isclass):
        if member.__module__ != module.__name__:
            continue
        if getattr(member, FASTARCH_CONTROLLER_DEFINITION_ATTR, None) is None:
            continue

        yield member
