from __future__ import annotations

import fastarch


def test_mvp_symbols_are_importable() -> None:
    from fastarch import (
        controller,
        delete,
        get,
        include_controllers,
        include_controllers_from_package,
        patch,
        post,
        put,
        route,
    )

    assert controller is fastarch.controller
    assert route is fastarch.route
    assert get is fastarch.get
    assert post is fastarch.post
    assert put is fastarch.put
    assert patch is fastarch.patch
    assert delete is fastarch.delete
    assert include_controllers is fastarch.include_controllers
    assert include_controllers_from_package is fastarch.include_controllers_from_package


def test_cli_helpers_are_absent() -> None:
    assert not hasattr(fastarch, "cli")
