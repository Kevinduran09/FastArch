from __future__ import annotations

from fastarch import controller, get


@controller("/shared")
class SharedController:
    @get("", summary="Read shared controller")
    def read_shared(self) -> dict[str, str]:
        return {"source": "source"}


SharedControllerAlias = SharedController
