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
- **Redis** — Publicación/suscripción de eventos (`RedisHelper`); el servicio debe estar disponible para esos flujos
- **Pytest** y **pytest-asyncio** — Pruebas unitarias async

## Comandos y Ejecución

### Vía Docker Compose (Recomendado)

```bash
docker-compose up -d --build
```
Esto levanta `api`, `postgres` y `redis`. En el arranque de la API se ejecutan migraciones y seeders automáticamente.

`seed-all` solo carga datos cuando `RUN_SEEDERS=true`; las migraciones se ejecutan siempre antes de iniciar Uvicorn.

### Desarrollo Local (Venv)

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python manage.py migrate
python manage.py seed-all
uvicorn app:app --host 0.0.0.0 --port 8000 --reload --ws websockets
```

### Comandos de Linter

```bash
ruff check .
python -m pytest
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
- `server/adapters/`: adaptación de transportes/proveedores a contratos internos
- `server/strategies/`: políticas intercambiables y factories para seleccionarlas
- `server/observers/`: eventos y observers async de aplicación/infraestructura
- `tests/`: pruebas unitarias
- `docs/`: análisis, contratos y guías de evolución

Dominios GraphQL registrados actualmente:

- `hello`, `auth`, `users`, `roles`, `modules`, `actions`, `permission`
- `projects`, `project_members`, `tasks`, `audit_logs`

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
- Todo dominio con lógica ejecutable debe incluir pruebas unitarias en el mismo cambio

## Patrones de Diseño

Patrones implementados y responsabilidades:

| Patrón | Ubicación | Uso |
|--------|-----------|-----|
| Singleton | `server/decorators/singleton_decorator.py` | Reutiliza helpers, servicios y repositorios dentro de un proceso. |
| Strategy | `server/strategies/permission_check_strategy.py` | Encapsula evaluación `ANY`/`ALL` de permisos. |
| Factory | `PermissionCheckStrategyFactory` | Selecciona estrategias mediante `PermissionCheckMode`. |
| Observer | `server/observers/` | Publica `UserUpdatedEvent` sin acoplar `UserService` a cada consumidor. |
| Adapter | `server/adapters/websocket_request_adapter.py` | Adapta WebSocket al contrato de headers/cookies usado por autenticación. |
| Decorator | `server/decorators/require_*` | Aplica autenticación y autorización como concerns transversales. |

Reglas al extenderlos:

- Usa Strategy cuando una política tenga variantes reales; agrega la estrategia a la factory y cubre cada resultado.
- Usa Observer para reacciones independientes a eventos. Define si los errores se propagan, registran o aíslan antes de añadir observers no críticos.
- Usa Adapter para aislar transportes o SDKs externos; el contrato interno no debe depender del proveedor.
- Limita Decorator a concerns transversales. La lógica de negocio permanece en servicios.
- Singleton representa una instancia por proceso, no estado distribuido entre workers. Nunca almacenes estado de request allí.
- No introduzcas un patrón solo por uniformidad; documenta la integración futura cuando aún no exista una variación o consumidor real.

La explicación ampliada y los puntos de evolución están en `docs/011_patrones_diseno_aplicados_y_evolucion_20260809120000.md`.

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
| `python manage.py seed-project-roles` | Siembra roles y permisos por proyecto |
| `python manage.py seed-demo` | Siembra escenarios demo de proyectos, miembros y tareas |
| `python manage.py seed-users` | Siembra usuarios iniciales |
| `python manage.py seed-all` | Ejecuta todos los seeders si `RUN_SEEDERS=true`; no ejecuta migraciones |
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
- `PORT` se usa en Docker Compose/Uvicorn, pero no pertenece a `Settings`
- `.env.example` puede quedar desactualizado; valida siempre contra `settings.py`
- Antes de editar configuración, valida nombres reales en `server/config/settings.py`
- No renombres variables de entorno sin revisar uso en auth, cookies, mail y Docker Compose

## Convenciones y Cuidado al Editar

- Mantén cambios pequeños y coherentes con la arquitectura existente
- Respeta el estilo async donde ya se usa SQLAlchemy async
- Si tocas GraphQL, revisa tanto HTTP como WebSocket en `server/__init__.py`
- Si agregas errores de negocio, revisa `server/enums/http_error_code_enum.py` y el formatter custom
- Si cambias autenticación/cookies, revisa middlewares, decorators y utils relacionados
- Si cambias correo, revisa `MailHelper`, `TemplateHelper` y templates HTML
- Si cambias eventos de usuario, revisa `AsyncEventPublisher`, sus observers y el canal Redis consumido por suscripciones
- Si cambias políticas múltiples de permisos, revisa Strategy, Factory, decorators y pruebas 401/403
- Preserva cambios preexistentes y archivos no rastreados que no pertenezcan a la tarea

## Regla Obligatoria de Pruebas Unitarias

- Todo cambio que cree o modifique lógica ejecutable debe crear o actualizar pruebas unitarias en el mismo cambio
- Esta regla aplica a servicios, repositorios, utils, helpers, decoradores, DTOs, resolvers, middlewares, seeders y cualquier archivo nuevo que contenga lógica de negocio, validación, autorización, serialización o efectos laterales
- Como mínimo, las pruebas deben cubrir el caso exitoso principal y al menos un caso negativo relevante
- Si el cambio toca autenticación o autorización, debe cubrir explícitamente errores `401 Unauthorized` y/o `403 Forbidden` cuando aplique
- Si el cambio toca persistencia, debe probar el comportamiento del repositorio o servicio con mocks/fakes cuando no sea viable usar PostgreSQL real
- Si el cambio toca GraphQL, debe probar que el resolver delega correctamente al servicio y que aplica los decoradores/permisos esperados
- No se considera terminada una feature nueva sin sus pruebas unitarias correspondientes

## Regla Obligatoria de Commits

- Los commits deben tener mensajes descriptivos y contextualizados para que cualquier persona pueda entender el impacto del cambio sin abrir inmediatamente el diff
- Evita mensajes genéricos como `fix`, `update`, `changes` o textos que solo digan que "se actualizó algo"
- El título del commit debe resumir el propósito del cambio y el cuerpo debe explicar qué se modificó, por qué se hizo y qué validaciones se ejecutaron cuando aplique
- Si el commit incluye cambios de arquitectura, migraciones, autorización, autenticación, pruebas o configuración, el mensaje debe mencionarlo explícitamente

## Verificación Mínima

Después de cambios relevantes, intenta validar al menos:

```bash
ruff check .
python -m pytest
python manage.py status
git diff --check
```

Si el cambio toca GraphQL o persistencia, además valida manualmente:
- `GET /ping`
- `GET /graphql`
- La operación GraphQL afectada
- Migraciones/seeders involucrados

## Preferencias para Agentes

- Prioriza corregir la fuente real del problema en lugar de parchear el resolver
- Si una nueva feature necesita datos persistidos, no omitas migración/seeder cuando aplique
- Documenta cualquier inconsistencia encontrada entre README, `.env.example`, Docker Compose y `settings.py`
- No introduzcas nuevas capas o patrones si la necesidad puede resolverse con la estructura actual
