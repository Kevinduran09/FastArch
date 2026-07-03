# RFC-001: Arches

## Status

Draft.

## Summary

Arches is the second major capability of FastArch. It introduces a declarative architecture tree that can be compiled into a FastAPI application at mount time.

FastArch Core answers:

```text
How do I organize endpoints?
```

Arches answers:

```text
How do I organize an application?
```

Arches is not a NestJS-style module system. It is not a public dependency injection container. It is a declarative composition model built around one concept: `Arch`.

## Core idea

An `Arch` is a mountable architecture unit.

An `Arch` can contain:

- controllers
- wires
- child arches
- a prefix

An application can be composed from one arch or from many nested arches.

```python
api_v1 = Arch(
    prefix="/api/v1",
    controllers=[
        UserController,
        PetController,
    ],
    wires=[
        bind(UserRepository).to(SqlAlchemyUserRepository).request(),
        bind(UserService).request(),
    ],
)

api_v1.mount(app)
```

Nested composition:

```python
users = Arch(
    prefix="/users",
    controllers=[UserController],
    wires=[
        bind(UserRepository).to(SqlAlchemyUserRepository).request(),
        bind(UserService).request(),
    ],
)

pets = Arch(
    prefix="/pets",
    controllers=[PetController],
    wires=[
        bind(PetRepository).to(SqlAlchemyPetRepository).request(),
        bind(PetService).request(),
    ],
)

api = Arch(
    prefix="/api/v1",
    arches=[users, pets],
    wires=[
        bind(Settings).singleton(),
        bind(LoggerService).singleton(),
    ],
)

api.mount(app)
```

## Design principle

`Arch(...)` only describes architecture.

It must not register routes, resolve dependencies, create service instances, or mutate FastAPI by itself.

The real work happens during:

```python
arch.mount(app)
```

Mounting compiles the arch tree into FastAPI-native routing and dependency resolution.

## Compilation model

At mount time, Arches should:

1. walk the arch tree
2. compose prefixes
3. merge parent and child wires
4. build an internal container/runtime
5. apply `@wires(...)` metadata to endpoint signatures as `Depends(...)`
6. register controllers through FastArch Core

Conceptually:

```text
Arch tree
  -> compiler
  -> internal container
  -> Depends-compatible endpoint signatures
  -> FastAPI app/router
```

## Dependency Injection model

Users declare bindings with `bind(...)`:

```python
bind(Settings).singleton()
bind(UserRepository).to(SqlAlchemyUserRepository).request()
bind(UserService).request()
```

Bindings describe how a token maps to an implementation and lifetime.

They do not create instances directly.

## Scopes

Initial supported scopes:

```text
singleton
request
transient
```

### singleton

One instance for the mounted arch runtime.

### request

One instance per request dependency graph.

### transient

A new instance every time the dependency is resolved.

## `@wires(...)`

`@wires(...)` declares which endpoint parameters should be resolved by Arches.

```python
@controller("/users")
class UserController:
    @get("/")
    @wires(service=UserService)
    async def list_users(self, service: UserService):
        return await service.list_users()
```

Arches must compile that into a FastAPI-compatible dependency signature equivalent to:

```python
async def list_users(
    service: Annotated[UserService, Depends(container.dependency(UserService))]
):
    ...
```

The user-facing function should remain easy to read. FastAPI should still own request validation, OpenAPI generation, `Depends`, `Annotated`, and `TestClient` behavior.

## Parent/child wire visibility

Child arches inherit parent wires.

```text
Root Arch
  Settings
  LoggerService

  Users Arch
    UserRepository
    UserService
```

`UserService` can depend on `LoggerService` even if the logger binding is declared in the parent arch.

## Overrides

A child arch can override a parent binding inside its own branch.

This enables versioned APIs and testing setups.

```python
api_v1 = Arch(
    prefix="/api/v1",
    wires=[bind(UserService).to(UserServiceV1).request()],
)

api_v2 = Arch(
    prefix="/api/v2",
    wires=[bind(UserService).to(UserServiceV2).request()],
)
```

Overrides should affect only the arch branch where they are declared.

## Versioning use case

```python
api = Arch(
    arches=[
        Arch(
            prefix="/api/v1",
            controllers=[UserV1Controller, PetV1Controller],
            wires=[bind(UserService).to(UserServiceV1).request()],
        ),
        Arch(
            prefix="/api/v2",
            controllers=[UserV2Controller],
            wires=[bind(UserService).to(UserServiceV2).request()],
        ),
    ],
    wires=[
        bind(Settings).singleton(),
        bind(LoggerService).singleton(),
    ],
)

api.mount(app)
```

## Non-goals

Arches must not introduce:

- NestJS-style modules
- public provider registries
- ORM abstractions
- authentication frameworks
- FastAPI internals monkeypatching
- mandatory DI usage

The existing FastArch Core API must remain valid:

```python
include_controllers(app, [UserController])
```

## Public API target

```python
from fastarch import Arch, bind, wires
```

## Internal implementation direction

`Arch` should be declarative.

The internal container should be private implementation detail. Users should not need to create or manage a container manually.

Possible internal layout:

```text
fastarch/arches/
  arch.py
  binding.py
  compiler.py
  runtime.py
  wiring.py
  scopes.py
  errors.py
```

## Open questions

- Should singleton instances be shared across the whole mounted arch tree or scoped per branch?
- Should `Arch(app, ...)` auto-mount, or should only `arch.mount(app)` be supported initially?
- Should route registration preserve the exact same order as the arch tree traversal?
- Should branch-level overrides be exposed through a dedicated method later?
