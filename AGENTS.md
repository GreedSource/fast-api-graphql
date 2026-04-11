# AGENTS.md

## Propósito

Esta guía orienta a cualquier agente que trabaje en este repositorio. El proyecto es una API backend con `FastAPI`, `Ariadne` y `MongoDB`, organizada por capas y enfocada en autenticación JWT, RBAC y administración de usuarios/roles/permisos.

## Stack y ejecución

- Python con dependencias declaradas en `requirements.txt`
- API HTTP y WebSocket en `FastAPI`
- GraphQL con `Ariadne`
- MongoDB async con `motor`
- Configuración por variables de entorno vía `pydantic-settings`
- Linting con `ruff`

Comandos comunes:

```bash
pip install -r requirements.txt
python manage.py migrate
python manage.py seed-all
uvicorn app:app --host 0.0.0.0 --port 5000 --reload --ws websockets
ruff check .
```

Si usas Docker:

```bash
docker-compose up -d --build
```

## Estructura del proyecto

Entrada principal:

- `app.py`: expone `app` para `uvicorn`
- `server/__init__.py`: construye la app FastAPI, middlewares, rutas `/`, `/ping`, `/graphql` y WebSocket `/graphql`

Capas principales:

- `server/schema/`: SDL GraphQL y resolvers
- `server/services/`: lógica de negocio
- `server/repositories/`: acceso a MongoDB
- `server/models/`: modelos de datos y respuestas
- `server/db/`: conexión Mongo, migraciones y seeders
- `server/helpers/` y `server/utils/`: utilidades compartidas
- `server/templates/`: templates HTML para correo/layouts
- `server/decorators/`: decorators para autenticación y autorización de resolvers

## Cómo extender funcionalidad

Si agregas un nuevo dominio de GraphQL:

1. Crea el subdirectorio en `server/schema/<dominio>/`
2. Añade `schema.graphql`
3. Implementa el resolver correspondiente
4. Registra el resolver en `server/schema/__init__.py`
5. Si hace falta persistencia, crea o actualiza:
   - `server/models/`
   - `server/repositories/`
   - `server/services/`
   - `server/db/migrations/`
   - `server/db/seeders/`

Regla de diseño:

- `schema`: recibe la request GraphQL y delega
- `services`: concentra reglas de negocio
- `repositories`: encapsula consultas a Mongo
- evita meter lógica compleja directamente en resolvers

## Autenticación y Autorización

### Decoradores disponibles

**`@require_token`** (`server/decorators/require_token_decorator.py`):
- Verifica que el usuario esté autenticado vía JWT (header `Authorization: Bearer` o cookies)
- Inyecta `current_user` en `info.context["current_user"]`
- El usuario incluye su rol con permisos resueltos: `user["role"]["permissions"] = [{"type": "users", "action": "read"}, ...]`

**`@require_permission(type, action)`** (`server/decorators/require_permission_decorator.py`):
- Verifica que el `current_user` tenga el permiso específico `{type, action}`
- `type` es la key del módulo (ej: `"users"`, `"roles"`)
- `action` es la key de la acción (ej: `"create"`, `"read"`, `"update"`, `"delete"`)
- Lanza `HTTPErrorCode.FORBIDDEN` (403) si el usuario no tiene el permiso
- Debe usarse **después** de `@require_token`

**`@require_permissions(permissions, mode)`** (`server/decorators/require_permission_decorator.py`):
- Verifica múltiples permisos simultáneamente
- `permissions`: lista de dicts `[{"type": "users", "action": "create"}, ...]`
- `mode`: `PermissionCheckMode.ANY` (basta uno) o `PermissionCheckMode.ALL` (todos requeridos)

Ejemplo de uso en resolvers:

```python
from server.decorators.require_token_decorator import require_token
from server.decorators.require_permission_decorator import require_permission

class UserResolver:
    @require_token
    @require_permission(type="users", action="create")
    async def resolve_create_user(self, _, info, input):
        # Solo usuarios con permiso users:create pueden ejecutar esta mutación
        ...
```

### Estructura de permisos

Los permisos se almacenan como objetos `{type, action}` donde:
- `type`: key del módulo (ej: `"users"`, `"roles"`, `"permissions"`)
- `action`: key de la acción (ej: `"create"`, `"read"`, `"update"`, `"delete"`)

El repositorio `UserRepository.aggregate_user_with_role_permissions()` resuelve los permisos del usuario haciendo join con las colecciones `roles`, `permissions`, `modules` y `actions`.

## Base de datos

La conexión a Mongo sale de `server/db/mongo.py` mediante `get_mongo_db()`.

Comandos administrativos disponibles en `manage.py`:

- `migrate`
- `seed-modules`
- `seed-actions`
- `seed-permissions`
- `seed-roles`
- `seed-users`
- `seed-all`
- `status`

Antes de asumir que una colección o índice existe, revisa `server/db/migrations/` y agrega una migración si el cambio modifica estructura, validaciones o índices.

## Configuración

La fuente de verdad para variables de entorno es `server/config/settings.py`, no el README.

Variables relevantes que el código espera:

- `JWT_SECRET_KEY`
- `JWT_REFRESH_SECRET_KEY`
- `SESSION_SECRET_KEY`
- `MONGO_URI`
- `MONGO_DB_NAME`
- `MAIL_SERVER`
- `MAIL_PORT`
- `MAIL_USERNAME`
- `MAIL_PASSWORD`
- `MAIL_DEFAULT_SENDER`
- `FRONTEND_URL`
- `CORS_ORIGINS`
- `RUN_SEEDERS`

Nota importante:

- `readme.md` y `.env.example` no están totalmente alineados con `settings.py`
- antes de editar configuración, valida nombres reales en `server/config/settings.py`
- no renombres variables de entorno sin revisar uso en auth, cookies, mail y Docker Compose

## Convenciones y cuidado al editar

- Mantén cambios pequeños y coherentes con la arquitectura existente
- Respeta el estilo async donde ya se usa `motor`
- Si tocas GraphQL, revisa tanto HTTP como WebSocket en `server/__init__.py`
- Si agregas errores de negocio, revisa `server/enums/http_error_code_enum.py` y el formatter custom
- Si cambias autenticación/cookies, revisa middlewares, decorators y utils relacionados
- Si cambias correo, revisa `MailHelper`, `TemplateHelper` y templates HTML

## Verificación mínima

Después de cambios relevantes, intenta validar al menos:

```bash
ruff check .
python manage.py status
```

Si el cambio toca GraphQL o persistencia, además valida manualmente:

- `GET /ping`
- `GET /graphql`
- la operación GraphQL afectada
- migraciones/seeders involucrados

## Estado actual del repositorio

Observaciones útiles para futuras tareas:

- No se observan tests automatizados en el repo
- `ruff.toml` usa `line-length = 120` y `target-version = "py312"`
- `docker-compose.yml` arranca migraciones y `seed-all` antes de levantar `uvicorn`
- `app.py` importa `create_app()` desde `server`

## Preferencias para agentes

- Prioriza corregir la fuente real del problema en lugar de parchear el resolver
- Si una nueva feature necesita datos persistidos, no omitas migración/seeder cuando aplique
- Documenta inconsistencias del repo al encontrarlas; varias ya existen entre README, `.env.example` y `settings.py`
- No introduzcas nuevas capas o patrones si la necesidad puede resolverse con la estructura actual
