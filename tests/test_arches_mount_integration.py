from __future__ import annotations

from fastapi import FastAPI
from fastapi.testclient import TestClient

from fastarch import Arch, bind, controller, get, wires
from fastarch.arches.errors import DuplicateBindingError, UnresolvedDependencyError, WireParameterError


class LoggerService:
    def __init__(self) -> None:
        self.messages: list[str] = []

    def info(self, message: str) -> None:
        self.messages.append(message)


class UserRepository:
    def list_users(self) -> list[str]:
        raise NotImplementedError


class UserRepositoryV1(UserRepository):
    def list_users(self) -> list[str]:
        return ["v1-user"]


class UserRepositoryV2(UserRepository):
    def list_users(self) -> list[str]:
        return ["v2-user"]


class UserService:
    def __init__(self, repository: UserRepository, logger: LoggerService) -> None:
        self.repository = repository
        self.logger = logger

    def list_users(self) -> list[str]:
        self.logger.info("list-users")
        return self.repository.list_users()


@controller("/users")
class UsersController:
    @get("/")
    @wires(service=UserService)
    def list_users(self, service: UserService) -> list[str]:
        return service.list_users()


@controller("/users")
class UsersV2Controller:
    @get("/")
    @wires(service=UserService)
    def list_users(self, service: UserService) -> list[str]:
        return service.list_users()


def test_arch_mount_injects_wired_service_and_hides_it_from_openapi() -> None:
    app = FastAPI()

    Arch(
        prefix="/api/v1",
        controllers=[UsersController],
        wires=[
            bind(LoggerService).singleton(),
            bind(UserRepository).to(UserRepositoryV1).request(),
            bind(UserService).request(),
        ],
    ).mount(app)

    client = TestClient(app)

    response = client.get("/api/v1/users/")
    schema = client.get("/openapi.json").json()
    parameters = schema["paths"]["/api/v1/users/"]["get"].get("parameters", [])

    assert response.status_code == 200
    assert response.json() == ["v1-user"]
    assert all(parameter["name"] != "service" for parameter in parameters)


def test_arch_children_inherit_parent_wires_and_can_override_by_branch() -> None:
    app = FastAPI()

    api = Arch(
        arches=[
            Arch(
                prefix="/api/v1",
                controllers=[UsersController],
                wires=[bind(UserRepository).to(UserRepositoryV1).request()],
            ),
            Arch(
                prefix="/api/v2",
                controllers=[UsersV2Controller],
                wires=[bind(UserRepository).to(UserRepositoryV2).request()],
            ),
        ],
        wires=[
            bind(LoggerService).singleton(),
            bind(UserService).request(),
        ],
    )

    api.mount(app)
    client = TestClient(app)

    assert client.get("/api/v1/users/").json() == ["v1-user"]
    assert client.get("/api/v2/users/").json() == ["v2-user"]


def test_arch_rejects_wires_without_matching_binding() -> None:
    app = FastAPI()

    try:
        Arch(
            prefix="/api/v1",
            controllers=[UsersController],
            wires=[],
        ).mount(app)
    except UnresolvedDependencyError as error:
        assert "UserService is not bound" in str(error)
    else:
        raise AssertionError("Expected unresolved @wires token to fail at mount time")


def test_arch_rejects_duplicate_bindings_in_same_arch() -> None:
    app = FastAPI()

    try:
        Arch(
            wires=[
                bind(UserService).request(),
                bind(UserService).singleton(),
            ]
        ).mount(app)
    except DuplicateBindingError as error:
        assert "UserService is bound more than once" in str(error)
    else:
        raise AssertionError("Expected duplicate binding to fail")


def test_arch_rejects_wires_for_missing_endpoint_parameter() -> None:
    @controller("/broken")
    class BrokenController:
        @get("/")
        @wires(service=UserService)
        def broken(self) -> dict[str, bool]:
            return {"ok": True}

    app = FastAPI()

    try:
        Arch(
            controllers=[BrokenController],
            wires=[bind(UserService).request()],
        ).mount(app)
    except WireParameterError as error:
        assert "missing parameter" in str(error)
    else:
        raise AssertionError("Expected invalid @wires parameter to fail")
