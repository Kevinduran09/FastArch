****# PRD — FastArch

## 1. Resumen del producto

**FastArch** será una librería ligera para organizar proyectos FastAPI grandes usando una sintaxis basada en controllers, decorators y convenciones limpias de arquitectura, sin reemplazar FastAPI ni romper su comportamiento nativo.

La librería permitirá escribir controllers de esta forma:

```python
from fastarch import controller, get, post

@controller(prefix="/users", tags=["Users"])
class UserController:

    @get("/", response_model=list[UserResponse])
    async def list_users(self, service: UserServiceDep):
        return await service.list_users()

    @post("/", response_model=UserResponse, status_code=201)
    async def create_user(self, data: CreateUserRequest, service: UserServiceDep):
        return await service.create_user(data)
```

Y registrarlos así:

```python
from fastapi import FastAPI
from fastarch import include_controllers

app = FastAPI()

include_controllers(app, [UserController], prefix="/api/v1")
```

## 2. Objetivo principal

Crear una librería pública de Python llamada **FastArch** que permita organizar rutas de FastAPI con una API tipo controller, manteniendo compatibilidad total con:

- `FastAPI`
- `APIRouter`
- `Depends`
- `Annotated`
- `response_model`
- `status_code`
- `tags`
- `summary`
- `description`
- `responses`
- OpenAPI automático
- middlewares nativos de FastAPI
- testing con `TestClient`

La librería debe aportar estructura, consistencia y developer experience sin crear un framework nuevo encima de FastAPI.

## 3. Problema

En proyectos FastAPI medianos o grandes, la organización basada solo en `APIRouter` puede volverse repetitiva:

```python
router = APIRouter(prefix="/users", tags=["Users"])

@router.get("/")
async def list_users():
    ...

@router.post("/")
async def create_user():
    ...
```

Aunque este patrón es válido, muchos equipos prefieren organizar por clases:

```python
class UserController:
    async def list_users(self):
        ...

    async def create_user(self):
        ...
```

FastAPI no tiene controllers como abstracción central. Existen alternativas, pero muchas agregan demasiada magia o no ofrecen una experiencia minimalista, bien tipada y orientada a arquitectura limpia.

## 4. Público objetivo

### Usuarios primarios

- Desarrolladores backend Python usando FastAPI.
- Equipos que trabajan en APIs medianas o grandes.
- Desarrolladores que quieren una estructura similar a controllers sin migrar a Litestar, Django REST Framework u otro framework.

### Usuarios secundarios

- Educadores que enseñan arquitectura backend con FastAPI.
- Equipos que quieren generar módulos estandarizados.
- Desarrolladores que prefieren arquitectura limpia: controller, service, repository, domain.

## 5. Propuesta de valor

FastArch debe prometer:

> Arquitectura limpia para FastAPI sin dejar de usar FastAPI.

Beneficios:

- Código más ordenado.
- Menos repetición en routers.
- Mejor navegación en proyectos grandes.
- Compatibilidad con FastAPI nativo.
- API simple, expresiva y fácil de adoptar.
- Convenciones útiles sin imponer un framework completo.
- Sin dependency injection propio.
- Sin ORM propio.
- Sin sistema de permisos incompatible.
- Sin decorators que rompan firmas de endpoints.

## 6. Principios de diseño

### 6.1 FastAPI-first

FastArch no debe competir con FastAPI. Debe apoyarse en `APIRouter` internamente.

### 6.2 Sin magia innecesaria

Los decorators deben guardar metadata, no envolver funciones de forma peligrosa.

Incorrecto:

```python
def decorator(func):
    async def wrapper(*args, **kwargs):
        return await func(*args, **kwargs)

    return wrapper
```

Correcto:

```python
def decorator(func):
    setattr(func, "__fastarch_route_definition__", route_definition)
    return func
```

### 6.3 Compatibilidad con type hints

FastAPI inspecciona firmas y anotaciones. FastArch debe preservar:

- Parámetros de path.
- Query params.
- Request bodies.
- `Depends`.
- `Annotated`.
- Return types.

### 6.4 API pequeña

La API pública v1.0 debe ser reducida:

```python
from fastarch import (
    controller,
    route,
    get,
    post,
    put,
    patch,
    delete,
    include_controllers,
    include_controllers_from_package,
)
```

### 6.5 Extensible, pero no pesada

Los plugins y CLI pueden existir, pero no deben ser necesarios para el uso básico.

## 7. Alcance del producto

### 7.1 Incluido

FastArch debe incluir:

- Decorator `@controller`.
- Decorators HTTP: `@get`, `@post`, `@put`, `@patch`, `@delete`.
- Decorator genérico `@route`.
- Registro manual con `include_controllers`.
- Registro automático con `include_controllers_from_package`.
- Soporte de prefijo global.
- Soporte de tags.
- Soporte de dependencies.
- Soporte de guards como alias expresivo de `Depends`.
- Soporte de metadata OpenAPI.
- CLI opcional para generar módulos.
- Tests unitarios.
- Tests de integración con FastAPI.
- Documentación básica.
- Ejemplo real de arquitectura limpia.

### 7.2 Excluido

La v1.0 no debe incluir:

- ORM propio.
- AutoCRUD mágico.
- Sistema propio de dependency injection.
- Sistema propio de autenticación.
- Sistema complejo de permisos.
- Reemplazo de `APIRouter`.
- Reemplazo de `Depends`.
- Reemplazo de Pydantic.
- Abstracciones tipo Django REST Framework `ModelViewSet`.

## 8. API esperada

### 8.1 Controller básico

```python
from fastarch import controller, get, post

@controller(prefix="/users", tags=["Users"])
class UserController:

    @get("/")
    async def list_users(self):
        return []

    @post("/")
    async def create_user(self):
        return {"created": True}
```

### 8.2 Registro manual

```python
from fastapi import FastAPI
from fastarch import include_controllers

from app.users.controller import UserController
from app.orders.controller import OrderController

app = FastAPI()

include_controllers(
    app,
    [
        UserController,
        OrderController,
    ],
)
```

### 8.3 Registro con prefijo global

```python
include_controllers(
    app,
    [
        UserController,
        OrderController,
    ],
    prefix="/api/v1",
)
```

Resultado esperado:

```text
/api/v1/users
/api/v1/orders
```

### 8.4 Controller con dependencies

```python
from fastapi import Depends
from fastarch import controller, get

async def require_auth():
    ...

@controller(
    prefix="/profile",
    tags=["Profile"],
    dependencies=[Depends(require_auth)],
)
class ProfileController:

    @get("/")
    async def get_profile(self):
        return {"profile": True}
```

### 8.5 Controller con guards

```python
from fastarch import controller, get

async def require_auth():
    ...

async def require_admin():
    ...

@controller(
    prefix="/admin",
    tags=["Admin"],
    guards=[require_auth, require_admin],
)
class AdminController:

    @get("/dashboard")
    async def dashboard(self):
        return {"admin": True}
```

Internamente, esto debe traducirse a:

```python
dependencies=[
    Depends(require_auth),
    Depends(require_admin),
]
```

### 8.6 Endpoint con metadata OpenAPI

```python
@get(
    "/{user_id}",
    response_model=UserResponse,
    summary="Obtener usuario",
    description="Obtiene un usuario por ID.",
    responses={
        404: {"description": "Usuario no encontrado"},
    },
)
async def get_user(self, user_id: int):
    ...
```

### 8.7 Auto-discovery

```python
from fastarch import include_controllers_from_package

include_controllers_from_package(
    app,
    package="app.modules",
    prefix="/api/v1",
)
```

Estructura esperada:

```text
app/
  modules/
    users/
      controller.py
    orders/
      controller.py
    payments/
      controller.py
```

La función debe encontrar clases decoradas con `@controller`.

## 9. Diseño técnico

### 9.1 Estructura interna de la librería

```text
fastarch/
  __init__.py
  controllers.py
  routes.py
  discovery.py
  registry.py
  cli.py
  types.py
  exceptions.py
tests/
  test_controller.py
  test_routes.py
  test_dependencies.py
  test_guards.py
  test_discovery.py
  test_openapi.py
examples/
  basic/
  clean_architecture/
  versioned_api/
```

### 9.2 `RouteDefinition`

La librería debe guardar metadata en cada método decorado.

```python
from dataclasses import dataclass
from typing import Any, Callable

@dataclass(frozen=True)
class RouteDefinition:
    path: str
    methods: list[str]
    status_code: int | None = None
    response_model: Any | None = None
    summary: str | None = None
    description: str | None = None
    responses: dict[int | str, Any] | None = None
    dependencies: list[Any] | None = None
    guards: list[Callable[..., Any]] | None = None
    tags: list[str] | None = None
    name: str | None = None
    operation_id: str | None = None
    deprecated: bool | None = None
```

### 9.3 `ControllerDefinition`

```python
@dataclass(frozen=True)
class ControllerDefinition:
    prefix: str
    tags: list[str]
    dependencies: list[Any]
    guards: list[Callable[..., Any]]
```

### 9.4 Decorator `@route`

Debe aceptar argumentos similares a `APIRouter.add_api_route`.

Ejemplo:

```python
def route(
    path: str,
    *,
    methods: list[str],
    response_model: Any | None = None,
    status_code: int | None = None,
    tags: list[str] | None = None,
    dependencies: list[Any] | None = None,
    guards: list[Callable[..., Any]] | None = None,
    summary: str | None = None,
    description: str | None = None,
    responses: dict[int | str, Any] | None = None,
    name: str | None = None,
    operation_id: str | None = None,
    deprecated: bool | None = None,
):
    ...
```

### 9.5 Decorators HTTP

Cada decorator debe delegar en `route`.

```python
def get(path: str, **kwargs):
    return route(path, methods=["GET"], **kwargs)

def post(path: str, **kwargs):
    return route(path, methods=["POST"], **kwargs)

def put(path: str, **kwargs):
    return route(path, methods=["PUT"], **kwargs)

def patch(path: str, **kwargs):
    return route(path, methods=["PATCH"], **kwargs)

def delete(path: str, **kwargs):
    return route(path, methods=["DELETE"], **kwargs)
```

### 9.6 Decorator `@controller`

Debe:

1. Guardar metadata de controller en la clase.
2. Crear un `APIRouter`.
3. Instanciar la clase.
4. Recorrer sus métodos.
5. Detectar métodos con `RouteDefinition`.
6. Registrar cada método como ruta del router.
7. Adjuntar el router generado a la clase.

Ejemplo de uso interno esperado:

```python
setattr(cls, "__fastarch_controller_definition__", controller_definition)
setattr(cls, "router", router)
setattr(cls, "__fastarch_is_controller__", True)
```

### 9.7 Manejo de `self`

La librería debe registrar métodos enlazados a una instancia:

```python
instance = cls()
endpoint = getattr(instance, method_name)
```

No debe registrar métodos directamente desde la clase, porque FastAPI podría interpretar `self` como parámetro de request.

### 9.8 Guards

Los guards deben convertirse en dependencies:

```python
from fastapi import Depends

dependencies = [
    Depends(guard)
    for guard in guards
]
```

Los guards del controller y los guards del endpoint deben combinarse.

Orden esperado:

```text
controller dependencies
controller guards
route dependencies
route guards
```

### 9.9 Registro manual

```python
def include_controllers(
    app: FastAPI,
    controllers: list[type],
    *,
    prefix: str = "",
) -> None:
    ...
```

Debe llamar internamente a:

```python
app.include_router(controller.router, prefix=prefix)
```

### 9.10 Auto-discovery

```python
def include_controllers_from_package(
    app: FastAPI,
    package: str,
    *,
    prefix: str = "",
) -> None:
    ...
```

Debe:

1. Importar el paquete.
2. Recorrer submódulos con `pkgutil.walk_packages`.
3. Importar módulos.
4. Detectar clases con `__fastarch_is_controller__ = True`.
5. Registrar sus routers.

## 10. Criterios de aceptación

### 10.1 Registro básico

Dado este controller:

```python
@controller(prefix="/users")
class UserController:

    @get("/")
    async def list_users(self):
        return []
```

Cuando se registre:

```python
include_controllers(app, [UserController])
```

Entonces debe existir la ruta:

```text
GET /users/
```

### 10.2 No debe exponer `self`

Dado un método:

```python
async def list_users(self):
    ...
```

El OpenAPI generado no debe mostrar un parámetro llamado `self`.

### 10.3 Debe soportar path params

```python
@get("/{user_id}")
async def get_user(self, user_id: int):
    ...
```

Debe funcionar:

```text
GET /users/123
```

Y `user_id` debe llegar como `int`.

### 10.4 Debe soportar request body

```python
@post("/")
async def create_user(self, data: CreateUserRequest):
    ...
```

FastAPI debe validar el body normalmente.

### 10.5 Debe soportar `Depends`

```python
async def list_users(self, service: UserServiceDep):
    ...
```

La dependency debe resolverse normalmente.

### 10.6 Debe generar OpenAPI correcto

Si se usa:

```python
@get("/", response_model=list[UserResponse], summary="Listar usuarios")
```

El schema OpenAPI debe incluir:

- Ruta.
- Método.
- Summary.
- Response model.
- Tags.

### 10.7 Debe soportar guards

Dado:

```python
@controller(prefix="/admin", guards=[require_admin])
class AdminController:
    ...
```

Si `require_admin` lanza `HTTPException(403)`, la ruta debe responder 403.

### 10.8 Debe soportar prefijo global

```python
include_controllers(app, [UserController], prefix="/api/v1")
```

Debe registrar:

```text
/api/v1/users
```

### 10.9 Debe soportar auto-discovery

Dado un paquete con controllers:

```text
app/modules/users/controller.py
app/modules/orders/controller.py
```

Esto debe registrar ambos:

```python
include_controllers_from_package(app, "app.modules")
```

## 11. Roadmap

### v0.1 — MVP

#### Objetivo

Crear la base mínima funcional.

#### Features

- `@controller`
- `@route`
- `@get`
- `@post`
- `@put`
- `@patch`
- `@delete`
- `include_controllers`

#### Criterios

- Debe registrar rutas correctamente.
- Debe funcionar con `TestClient`.
- Debe preservar firmas de endpoints.
- Debe generar OpenAPI válido.

### v0.2 — Metadata completa

#### Objetivo

Soportar metadata común de FastAPI.

#### Features

- `response_model`
- `status_code`
- `tags`
- `summary`
- `description`
- `responses`
- `name`
- `operation_id`
- `deprecated`
- `dependencies`

#### Criterios

- La metadata debe aparecer en OpenAPI.
- Las dependencies deben ejecutarse.
- Los status codes deben respetarse.

### v0.3 — Auto-discovery

#### Objetivo

Permitir registrar controllers automáticamente desde un paquete.

#### Features

- `include_controllers_from_package`
- Detección de controllers decorados.
- Errores claros si el paquete no existe.
- Evitar duplicados.

#### Criterios

- Debe registrar múltiples controllers desde distintos módulos.
- No debe registrar clases no decoradas.
- Debe manejar paquetes anidados.

### v0.4 — Guards

#### Objetivo

Agregar sintaxis expresiva para autorización.

#### Features

- `guards` en controller.
- `guards` en endpoint.
- Conversión interna a `Depends`.

#### Criterios

- Los guards deben ejecutarse.
- Los guards del controller deben aplicarse a todas las rutas.
- Los guards del endpoint deben aplicarse solo a esa ruta.
- Deben respetarse errores `HTTPException`.

### v0.5 — Versionado y prefijos

#### Objetivo

Facilitar APIs versionadas.

#### Features

- `prefix` global en `include_controllers`.
- Compatibilidad con prefix de controller.
- Documentación de versionado `/api/v1`.

#### Criterios

- Los prefijos deben componerse correctamente.
- No debe duplicar slashes.
- Debe funcionar con `/api/v1`, `/api/v2`, etc.

### v0.6 — CLI inicial

#### Objetivo

Agregar generación de módulos.

#### Features

Comando:

```bash
fastarch create-module users
```

Debe generar:

```text
users/
  __init__.py
  controller.py
  service.py
  schemas.py
```

#### Criterios

- Debe crear archivos.
- No debe sobrescribir archivos existentes sin confirmación.
- Debe generar código válido.
- Debe ser opcional.

### v0.7 — Ejemplos profesionales

#### Objetivo

Facilitar adopción real.

#### Features

- Ejemplo básico.
- Ejemplo con arquitectura limpia.
- Ejemplo con dependencies.
- Ejemplo con guards.
- Ejemplo con versionado.

#### Criterios

- Todos los ejemplos deben ejecutar.
- Todos los ejemplos deben tener README propio.
- Deben usarse en tests o CI cuando sea posible.

### v0.8 — Calidad de paquete

#### Objetivo

Preparar publicación seria.

#### Features

- `pyproject.toml`
- Ruff
- mypy o pyright
- pytest
- coverage
- GitHub Actions
- README completo
- Licencia MIT
- Changelog

#### Criterios

- Tests pasan en CI.
- Lint pasa en CI.
- Type checking pasa en CI.
- Build del paquete funciona.

### v0.9 — Plugins ligeros

#### Objetivo

Permitir extensiones controladas.

#### Features

- Interfaz `FastArchPlugin`.
- Hooks:
  - `before_register_controller`
  - `after_register_controller`
  - `before_register_route`
  - `after_register_route`

#### Criterios

- Plugins no deben ser necesarios para uso básico.
- Plugins no deben modificar endpoints de forma insegura.
- Debe existir al menos un ejemplo de plugin de logging.

### v1.0 — API estable

#### Objetivo

Publicar versión estable.

#### Requisitos

- API pública congelada.
- Documentación completa.
- Tests completos.
- Ejemplos funcionales.
- Compatibilidad comprobada con FastAPI actual.
- Publicación en PyPI.
- README profesional.

## 12. Requisitos no funcionales

### 12.1 Compatibilidad

FastArch debe ser compatible con:

- Python 3.10+
- FastAPI moderno
- Pydantic v2
- Starlette usado por FastAPI

### 12.2 Performance

FastArch registra rutas al iniciar la app. No debe agregar overhead significativo por request.

Objetivo:

```text
Overhead en runtime: prácticamente cero.
```

La lógica de decorators ocurre en import/register time.

### 12.3 Seguridad

FastArch no debe implementar autenticación propia.

Los guards deben usar funciones normales compatibles con `Depends`.

### 12.4 Mantenibilidad

El código debe ser pequeño y testeable.

Evitar:

- metaprogramación excesiva
- monkeypatching de FastAPI
- manipulación peligrosa de firmas
- dependencias innecesarias

### 12.5 Documentación

La documentación debe incluir:

- Instalación.
- Uso básico.
- Uso con `Depends`.
- Uso con guards.
- Uso con OpenAPI.
- Uso con auto-discovery.
- Ejemplo de arquitectura limpia.
- Migración desde `APIRouter`.

## 13. Casos de uso principales

### 13.1 Proyecto pequeño

```python
@controller(prefix="/health")
class HealthController:

    @get("/")
    async def health(self):
        return {"status": "ok"}
```

### 13.2 Proyecto modular

```text
app/
  modules/
    users/
      controller.py
    orders/
      controller.py
```

```python
include_controllers_from_package(app, "app.modules")
```

### 13.3 API privada con autenticación

```python
@controller(prefix="/profile", guards=[require_auth])
class ProfileController:
    ...
```

### 13.4 API administrativa

```python
@controller(prefix="/admin", guards=[require_auth, require_admin])
class AdminController:
    ...
```

### 13.5 API versionada

```python
include_controllers(app, [UserController], prefix="/api/v1")
```

## 14. Ejemplo final esperado

```python
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel

from fastarch import controller, get, post, include_controllers


class CreateUserRequest(BaseModel):
    email: str
    name: str


class UserResponse(BaseModel):
    id: int
    email: str
    name: str


class UserService:
    def __init__(self):
        self.users = {}
        self.sequence = 1

    async def list_users(self):
        return list(self.users.values())

    async def create_user(self, data: CreateUserRequest):
        user = UserResponse(id=self.sequence, email=data.email, name=data.name)
        self.users[user.id] = user
        self.sequence += 1
        return user

    async def get_user(self, user_id: int):
        return self.users.get(user_id)


user_service = UserService()


def get_user_service():
    return user_service


UserServiceDep = Annotated[UserService, Depends(get_user_service)]


async def require_auth():
    return {"id": 1}


@controller(prefix="/users", tags=["Users"], guards=[require_auth])
class UserController:

    @get("/", response_model=list[UserResponse])
    async def list_users(self, service: UserServiceDep):
        return await service.list_users()

    @post("/", response_model=UserResponse, status_code=201)
    async def create_user(self, data: CreateUserRequest, service: UserServiceDep):
        return await service.create_user(data)

    @get("/{user_id}", response_model=UserResponse)
    async def get_user(self, user_id: int, service: UserServiceDep):
        user = await service.get_user(user_id)

        if user is None:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")

        return user


app = FastAPI(title="Example API")

include_controllers(app, [UserController], prefix="/api/v1")
```

## 15. Plan para agente de IA

El agente debe implementar el proyecto por fases.

### Fase 1 — Setup

Crear:

```text
pyproject.toml
fastarch/
tests/
README.md
```

Configurar:

- pytest
- ruff
- mypy o pyright
- build backend
- package metadata

### Fase 2 — Core decorators

Implementar:

- `RouteDefinition`
- `ControllerDefinition`
- `route`
- `get`
- `post`
- `put`
- `patch`
- `delete`
- `controller`

### Fase 3 — Registro

Implementar:

- `include_controllers`
- validación de controller
- errores claros

### Fase 4 — Tests básicos

Crear tests para:

- rutas GET
- rutas POST
- path params
- request body
- response model
- status code
- OpenAPI
- `self` no aparece como parámetro

### Fase 5 — Dependencies y guards

Implementar:

- dependencies en controller
- dependencies en endpoint
- guards en controller
- guards en endpoint
- combinación correcta

### Fase 6 — Auto-discovery

Implementar:

- `include_controllers_from_package`
- búsqueda recursiva
- detección de controllers
- evitar duplicados

### Fase 7 — CLI

Implementar comando:

```bash
fastarch create-module users
```

Generar archivos básicos.

### Fase 8 — Documentación

Crear README con:

- qué es
- instalación
- quickstart
- examples
- guards
- discovery
- versioning
- filosofía del proyecto

### Fase 9 — CI

Agregar GitHub Actions para:

- install
- lint
- type check
- tests

### Fase 10 — Release v1.0

Antes de v1.0:

- revisar API pública
- congelar nombres
- agregar changelog
- publicar en PyPI
- crear tag `v1.0.0`

## 16. Definition of Done

El proyecto se considera listo para v1.0 cuando:

- La API pública está documentada.
- Todos los tests pasan.
- El paquete instala correctamente desde wheel.
- El README tiene ejemplos funcionales.
- Los controllers funcionan con FastAPI real.
- OpenAPI se genera correctamente.
- `Depends` funciona sin hacks.
- `Annotated` funciona correctamente.
- Guards funcionan como dependencies.
- Auto-discovery funciona.
- CLI genera módulos válidos.
- No hay monkeypatching de FastAPI.
- No hay manipulación peligrosa de firmas.
- El código está tipado.
- El proyecto puede publicarse en PyPI.

## 17. Riesgos

### 17.1 Romper firmas de endpoints

Riesgo alto. FastAPI depende de la firma original.

Mitigación:

- No envolver handlers.
- Guardar metadata con `setattr`.
- Usar métodos enlazados a instancia.

### 17.2 Crear demasiada abstracción

Riesgo medio.

Mitigación:

- Mantener API pequeña.
- No implementar AutoCRUD antes de v1.0.
- No crear dependency injection propio.

### 17.3 Incompatibilidad con FastAPI

Riesgo medio.

Mitigación:

- Tests de integración.
- Mantener dependencia flexible.
- Evitar usar internals privados de FastAPI.

### 17.4 Baja adopción

Riesgo medio.

Mitigación:

- README excelente.
- Ejemplos reales.
- Comparación honesta con `APIRouter`.
- Documentar que la librería es opcional y minimalista.

## 18. Métricas de éxito

### Técnicas

- 90%+ coverage en core.
- CI estable.
- Tiempo de registro de rutas mínimo.
- Cero overhead por request atribuible a la librería.

### Comunidad

- README claro.
- Ejemplo funcional en menos de 5 minutos.
- Primeros usuarios pueden migrar un router FastAPI sin fricción.
- Issues resueltos con rapidez.
- API pública estable desde v1.0.

## 19. Mensaje de posicionamiento

Mensaje recomendado en inglés:

```text
FastArch adds lightweight architecture-oriented controllers to FastAPI without replacing FastAPI, APIRouter, Depends, or OpenAPI.
```

Mensaje recomendado en español:

```text
FastArch agrega controllers ligeros y arquitectura limpia a FastAPI sin reemplazar FastAPI, APIRouter, Depends ni OpenAPI.
```

## 20. Filosofía final

FastArch debe mantener esta idea central:

```text
FastAPI sigue siendo FastAPI.
FastArch solo organiza mejor tus rutas y tu arquitectura.
```
