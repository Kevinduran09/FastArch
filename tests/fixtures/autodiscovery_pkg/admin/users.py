from __future__ import annotations

from pydantic import BaseModel

from fastarch import controller, get


class UserPayload(BaseModel):
    id: int
    name: str


@controller("/users", tags=["users"])
class UsersController:
    @get("/", response_model=list[UserPayload], summary="List discovered users")
    def list_users(self) -> list[UserPayload]:
        return [
            UserPayload(id=1, name="Ada Lovelace"),
            UserPayload(id=2, name="Grace Hopper"),
        ]
