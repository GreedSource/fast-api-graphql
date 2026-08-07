# AGENTS.md

## Propósito

Esta guía orienta a cualquier agente de IA (como Antigravity, Cursor, Windsurf, Claude Code, Qwen, etc.) y a desarrolladores que trabajen en este repositorio. El proyecto es una API backend con `FastAPI`, `Ariadne` y `PostgreSQL`, organizada por capas y enfocada en autenticación JWT, RBAC y administración de usuarios/roles/permisos.

## Stack y Tecnologías

- **Python 3.12**
- **FastAPI** — Web Framework (HTTP & WebSocket)
- **Ariadne** — GraphQL schema-first
- **PostgreSQL** async con **SQLAlchemy 2.0** y **asyncpg**
- **Pydantic Settings** — Configuración por variables de entorno
- **Uvicorn** — Servidor ASGI
- **Ruff** — Linter/Formatter (`line-length = 120`, target Python 3.12)
- **PyJWT** & **bcrypt** — Autenticación y hashing de contraseñas
- **Jinja2** — Templates HTML para correos
- **Redis** — Opcional para caché/sesiones (`RedisHelper`)

## Comandos y Ejecución

### Vía Docker Compose (Recomendado)

```bash
docker-compose up -d --build
```
Esto levanta `api`, `postgres` y `redis`. En el arranque de la API se ejecutan migraciones y seeders automáticamente.

### Desarrollo Local (Venv)

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python manage.py migrate
python manage.py seed-all
uvicorn app:app --host 0.0.0.0 --port 5000 --reload --ws websockets
```

### Comandos de Linter

```bash
ruff check .
```

## Endpoints HTTP / WebSocket

| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/` | Información raíz de la API |
| GET | `/ping` | Health check |
| GET | `/graphql` | GraphQL Explorer (GraphiQL) |
| POST | `/graphql` | Endpoint GraphQL HTTP |
| WS | `/graphql` | Endpoint GraphQL WebSocket (suscripciones) |

## Estructura del Proyecto

Entrada principal:
- `app.py`: expone `app` para `uvicorn`
- `server/__init__.py`: construye la app FastAPI, middlewares, rutas `/`, `/ping`, `/graphql` y WebSocket `/graphql`

Capas principales:
- `server/schema/`: SDL GraphQL (`.graphql`) y resolvers
- `server/services/`: lógica de negocio
- `server/repositories/`: acceso a PostgreSQL / SQLAlchemy
- `server/models/`: segmentado en `server/models/orm/` (entidades SQLAlchemy) y `server/models/dto/` (schemas Pydantic)
- `server/db/`: conexión y sesión Async de base de datos (`session.py`)
- `server/migrations/`: runner de migraciones DDL versionadas con tabla `schema_migrations`
- `server/seeders/`: seeders de carga inicial de datos para PostgreSQL
- `server/helpers/` y `server/utils/`: utilidades compartidas (logger, mail, redis, template)
- `server/templates/`: templates HTML para correo/layouts
- `server/decorators/`: decoradores para autenticación y autorización

## Cómo Extender Funcionalidad

Si agregas un nuevo dominio de GraphQL:

1. Crea el subdirectorio en `server/schema/<dominio>/`
2. Añade `schema.graphql`
3. Implementa el resolver correspondiente
4. Registra el resolver en `server/schema/__init__.py`
5. Si hace falta persistencia, crea o actualiza:
   - `server/models/`
   - `server/repositories/`
   - `server/services/`
   - `server/migrations/`
   - `server/seeders/`

Regla de diseño:
- `schema`: recibe la request GraphQL y delega
- `services`: concentra reglas de negocio
- `repositories`: encapsula consultas a PostgreSQL mediante SQLAlchemy
- Evita meter lógica compleja directamente en resolvers

## Autenticación y Autorización

### Decoradores disponibles (`server/decorators/`)

**`@require_token`** (`server/decorators/require_token_decorator.py`):
- Verifica que el usuario esté autenticado vía JWT (header `Authorization: Bearer` o cookies)
- Inyecta `current_user` en `info.context["current_user"]`
- El usuario incluye su rol con permisos resueltos: `user["role"]["permissions"] = [{"type": "users", "action": "read"}, ...]`

**`@require_permission(type, action)`** (`server/decorators/require_permission_decorator.py`):
- Verifica que el `current_user` tenga el permiso específico `{type, action}`
- `type`: key del módulo (ej: `"users"`, `"roles"`)
- `action`: key de la acción (ej: `"create"`, `"read"`, `"update"`, `"delete"`)
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
        ...
```

### Estructura de Permisos

Los permisos se almacenan como objetos `{type, action}` donde:
- `type`: key del módulo (ej: `"users"`, `"roles"`, `"permissions"`)
- `action`: key de la acción (ej: `"create"`, `"read"`, `"update"`, `"delete"`)

El repositorio `UserRepository.aggregate_user_with_role_permissions()` resuelve los permisos del usuario haciendo joins/relaciones con `roles`, `permissions`, `modules` y `actions`.

## Base de Datos y CLI

La conexión a PostgreSQL sale de `server/db/session.py` mediante `engine`, `AsyncSessionLocal` y `get_db_session()`.

Comandos administrativos disponibles en `manage.py`:

| Comando | Descripción |
|---------|-------------|
| `python manage.py migrate` | Aplica migraciones DDL en PostgreSQL |
| `python manage.py seed-modules` | Siembra módulos base |
| `python manage.py seed-actions` | Siembra acciones base |
| `python manage.py seed-permissions` | Genera matriz de permisos (módulos x acciones) |
| `python manage.py seed-roles` | Siembra roles base |
| `python manage.py seed-users` | Siembra usuarios iniciales |
| `python manage.py seed-all` | Ejecuta migraciones y todos los seeders |
| `python manage.py status` | Muestra el estado de migraciones aplicadas |

Antes de asumir que una tabla, relación o índice existe, revisa las migraciones y agrega una migración si el cambio modifica estructura, validaciones o índices.

### Convención de Documentación y Migraciones
- **Documentación de análisis**: Guardar en la carpeta `docs/` con el formato `NNN_nombre_descriptivo_timestamp.md` (ejemplo: `docs/001_analisis_migracion_postgresql_sqlalchemy_20260806222244.md`).
- **Migraciones**: Formato `vNNN_nombre_descriptivo_del_ddl_timestamp.py` en `server/migrations/versions/`. Cada archivo define `version`, `description` y `upgrade(conn)`.

## Configuración

La fuente de verdad para variables de entorno es `server/config/settings.py`, no el README.

Variables relevantes que el código espera:
- `JWT_SECRET_KEY`
- `JWT_REFRESH_SECRET_KEY`
- `SESSION_SECRET_KEY`
- `POSTGRES_SERVER`
- `POSTGRES_PORT`
- `POSTGRES_USER`
- `POSTGRES_PASSWORD`
- `POSTGRES_DB`
- `REDIS_URL`
- `MAIL_SERVER`, `MAIL_PORT`, `MAIL_USERNAME`, `MAIL_PASSWORD`, `MAIL_DEFAULT_SENDER`
- `FRONTEND_URL`
- `CORS_ORIGINS`
- `RUN_SEEDERS`

Nota importante:
- `readme.md` y `.env.example` no están totalmente alineados con `settings.py`
- Antes de editar configuración, valida nombres reales en `server/config/settings.py`
- No renombres variables de entorno sin revisar uso en auth, cookies, mail y Docker Compose

## Convenciones y Cuidado al Editar

- Mantén cambios pequeños y coherentes con la arquitectura existente
- Respeta el estilo async donde ya se usa SQLAlchemy async
- Si tocas GraphQL, revisa tanto HTTP como WebSocket en `server/__init__.py`
- Si agregas errores de negocio, revisa `server/enums/http_error_code_enum.py` y el formatter custom
- Si cambias autenticación/cookies, revisa middlewares, decorators y utils relacionados
- Si cambias correo, revisa `MailHelper`, `TemplateHelper` y templates HTML

## Verificación Mínima

Después de cambios relevantes, intenta validar al menos:

```bash
ruff check .
python manage.py status
```

Si el cambio toca GraphQL o persistencia, además valida manualmente:
- `GET /ping`
- `GET /graphql`
- La operación GraphQL afectada
- Migraciones/seeders involucrados

## Preferencias para Agentes

- Prioriza corregir la fuente real del problema en lugar de parchear el resolver
- Si una nueva feature necesita datos persistidos, no omitas migración/seeder cuando aplique
- Documenta inconsistencias del repo al encontrarlas; varias ya existen entre README, `.env.example` y `settings.py`
- No introduzcas nuevas capas o patrones si la necesidad puede resolverse con la estructura actual
