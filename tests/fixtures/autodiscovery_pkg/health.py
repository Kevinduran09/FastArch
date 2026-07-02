from __future__ import annotations

from fastarch import controller, get


@controller("/health", tags=["health"])
class HealthController:
    @get("", summary="Discovered health check")
    def read_health(self) -> dict[str, bool]:
        return {"ok": True}
