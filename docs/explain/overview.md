# FastArch — Explicación de clases y decoradores

Este documento explica en detalle las definiciones y decoradores del paquete `fastarch` (MVP), cómo se construyen y cómo funcionan. Incluye ejemplos de uso y notas de diseño.

**Archivos analizados**
- `fastarch/types.py`
- `fastarch/controllers.py`
- `fastarch/routes.py`
- `fastarch/__init__.py`

**Resumen del propósito**
FastArch separa la declaración de metadata (decoradores) del registro real de rutas en una aplicación HTTP. Los decoradores solo almacenan metadata inmutable en clases y funciones; luego `include_controllers(...)` lee esa metadata, crea un `APIRouter` por controller y registra métodos enlazados (`bound methods`) para preservar el comportamiento nativo de FastAPI.

**Constantes y tipos**
- `FASTARCH_CONTROLLER_DEFINITION_ATTR` = "__fastarch_controller_definition__": atributo usado para adjuntar `ControllerDefinition` a la clase.
- `FASTARCH_ROUTE_DEFINITION_ATTR` = "__fastarch_route_definition__": atributo usado para adjuntar `RouteDefinition` a la función.
- `HttpMethod` = Literal["GET", "POST", "PUT", "PATCH", "DELETE"]: tipo que asegura los métodos HTTP esperados.

**ControllerDefinition (clase)**
- Ubicación: `fastarch/types.py`
- Propósito: representar metadatos de un controller (grupo de rutas) de forma inmutable y ligera.
- Declaración clave: `@dataclass(frozen=True, slots=True)` — inmutable y con slots para menor uso de memoria.
- Atributos:
  - `prefix: str` — prefijo de ruta aplicado a todas las rutas del controller (ej. `/users`).
  - `tags: tuple[str, ...]` — etiquetas para documentación/agrupación (tupla inmutable).
  - `dependencies: tuple[Any, ...]` — dependencias compartidas (inyección) como tupla inmutable.
  - `responses: dict[int | str, Any]` — mapeo de códigos de respuesta a esquemas/ejemplos (usa default_factory para evitar mutación compartida).
  - `extras: dict[str, Any]` — espacio para opciones adicionales específicas del integrador.
- Motivos de diseño:
  - `frozen=True` garantiza que la metadata no se muta accidentalmente en runtime.
  - `slots=True` evita la creación dinámica de atributos y reduce huella de memoria.
- Construcción:
  - Se crea mediante el decorador `controller(...)` que convierte listas a tuplas y dicts según convenga y lo adjunta a la clase.
- Lectura:
  - `getattr(MyController, "__fastarch_controller_definition__", None)` devuelve la definición si existe.

**RouteDefinition (clase)**
- Ubicación: `fastarch/types.py`
- Propósito: contener metadatos de una ruta (endpoint) sin envolver la función, para permitir registro posterior.
- Declaración clave: `@dataclass(frozen=True, slots=True)`.
- Atributos importantes:
  - `path: str` — ruta relativa (ej. `/{id}`).
  - `methods: tuple[HttpMethod, ...]` — métodos HTTP permitidos (p. ej. (`GET`,)).
  - `response_model: Any | None` — modelo de respuesta (pydantic u otro), opcional.
  - `status_code: int | None` — código de respuesta por defecto.
  - `tags`, `dependencies` — igual que en `ControllerDefinition`.
  - `summary`, `description` — textos para documentación.
  - `responses` — mapeo de respuestas específicas.
  - `name`, `operation_id`, `deprecated`, `include_in_schema`, `response_description` — opciones para documentación/comportamiento.
  - `extras: dict[str, Any]` — opciones adicionales.
- Motivo de diseño: inmutabilidad y `extras` para extensibilidad.
- Construcción:
  - El decorador `route(...)` normaliza `methods` a mayúsculas y crea una instancia `RouteDefinition` que se adjunta a la función.
- Lectura:
  - `getattr(func, "__fastarch_route_definition__", None)` devuelve la definición si existe.

**Decorador `controller(...)`**
- Ubicación: `fastarch/controllers.py`
- Propósito: anotar una clase con metadata de controller sin registrar rutas ni envolver métodos.
- Firma: `controller(prefix: str = "", *, tags: Sequence[str] | None = None, dependencies: Sequence[Any] | None = None, responses: dict | None = None, **kwargs)`
- Qué hace:
  1. Construye `ControllerDefinition` con `prefix`, `tags` y `dependencies` convertidos a tuplas, `responses` convertido a dict, y `extras` con `kwargs`.
  2. Adjunta esa definición a la clase usando `setattr(cls, FASTARCH_CONTROLLER_DEFINITION_ATTR, definition)`.
  3. Devuelve la clase sin modificar su comportamiento.
- Ventaja: declara metadata de forma declarativa y separada del registro.
- Ejemplo:
```python
@controller("/users", tags=["users"])
class UserController:
    def list(self):
        pass
```
Luego: `UserController.__fastarch_controller_definition__` contiene la metadata.

**Decorador `route(...)` y atajos HTTP**
- Ubicación: `fastarch/routes.py`
- Propósito: anotar funciones con metadata de ruta (path, métodos, modelos, etc.) sin envolver la función.
- Firma principal: `route(path: str, *, methods: Sequence[str], response_model: Any|None=None, status_code: int|None=None, ...)`
- Flujo interno:
  1. Normaliza `methods` a mayúsculas y los castea a `HttpMethod`, creando una tupla inmutable.
  2. Construye `RouteDefinition(...)` con los parámetros y `extras` desde `kwargs`.
  3. Adjunta la definición a la función con `setattr(func, FASTARCH_ROUTE_DEFINITION_ATTR, definition)`.
  4. Retorna la función original sin envolver.
- Helpers: `get`, `post`, `put`, `patch`, `delete` son atajos que llaman `route(..., methods=("GET",))`, etc.
- Ejemplo:
```python
@get("/users/{id}", response_model=UserSchema)
def read_user(id: int):
    return {...}
```
Luego: `read_user.__fastarch_route_definition__` contiene la `RouteDefinition`.

**Patrón de uso real (`include_controllers`)**
La implementación actual hace exactamente este flujo:
1. Recibe `app_or_router` y una lista de clases o instancias de controllers.
2. Si recibe una clase, intenta instanciarla sin argumentos; si falla, exige que el consumidor pase una instancia explícita.
3. Lee `ControllerDefinition` desde la clase decorada con `@controller(...)`.
4. Crea un `APIRouter` por controller, combinando el prefijo global con el prefijo del controller.
5. Recorre los métodos declarados con metadata de ruta, obtiene el método enlazado desde la instancia y lo registra con `router.add_api_route(...)`.
6. Incluye ese router en la app/router de destino.

Ejemplo simplificado del flujo real:
```python
app = FastAPI()
include_controllers(app, [UsersController(service)], prefix="/api/v1")
```

**Notas de diseño y recomendaciones**
- Separar metadata de registro facilita pruebas unitarias e introspección (no se cambia la signatura ni el comportamiento de las funciones).
- `extras` en ambas definiciones permite que integradores pasen opciones específicas del router sin romper la API pública.
- Mantener las dataclasses `frozen` evita mutaciones indeseadas que podrían introducir inconsistencias cuando múltiples módulos interactúan.

**Estado del MVP**
- `include_controllers(app_or_router, controllers, prefix="")` ya está implementado para registro manual sobre FastAPI/APIRouter.
- El repo ya tiene tests de metadata, registro e integración con compatibilidad OpenAPI/FastAPI.
- Existe un ejemplo runnable en `examples/fastapi_backend/` para probar el flujo completo sin salir del alcance del MVP.

---

Si querés probar el flujo completo, arrancá por `README.md` y `examples/fastapi_backend/README.md`.
