from __future__ import annotations

from fastapi import FastAPI

from fastarch import controller, get
from fastarch.types import FASTARCH_CONTROLLER_DEFINITION_ATTR, FASTARCH_ROUTE_DEFINITION_ATTR


def test_controller_stores_metadata_without_registering_routes() -> None:
    dependency = object()

    def require_token() -> None:
        return None

    @controller(
        "/users",
        tags=("users",),
        dependencies=(dependency,),
        guards=(require_token,),
        responses={404: {"description": "Not found"}},
        team="platform",
    )
    class UsersController:
        @get("/{user_id}")
        def get_user(self, user_id: str) -> dict[str, str]:
            return {"user_id": user_id}

    definition = getattr(UsersController, FASTARCH_CONTROLLER_DEFINITION_ATTR)
    route_definition = getattr(UsersController.get_user, FASTARCH_ROUTE_DEFINITION_ATTR)
    app = FastAPI()

    assert definition.prefix == "/users"
    assert definition.tags == ("users",)
    assert definition.dependencies == (dependency,)
    assert definition.guards == (require_token,)
    assert callable(definition.guards[0])
    assert definition.responses == {404: {"description": "Not found"}}
    assert definition.extras == {"team": "platform"}
    assert route_definition.path == "/{user_id}"
    assert all(route.path != "/users/{user_id}" for route in app.routes)


def test_controller_decorator_returns_original_class() -> None:
    class UsersController:
        pass

    decorated = controller("/users")(UsersController)

    assert decorated is UsersController
