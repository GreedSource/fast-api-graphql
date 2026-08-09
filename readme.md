# FastAPI GraphQL API

API backend construida con `FastAPI`, `Ariadne` y `PostgreSQL`, orientada a autenticación JWT, RBAC global y por proyecto, administración de usuarios y gestión de proyectos, miembros, tareas y auditoría.

## Características

- API GraphQL sobre `FastAPI`
- Soporte HTTP y WebSocket para GraphQL
- Autenticación con JWT
- RBAC con roles, permisos, módulos y acciones
- Autorización contextual por proyecto y rol de proyecto
- Gestión de proyectos, miembros, tareas y logs de auditoría
- Persistencia async con `SQLAlchemy 2.0` y `asyncpg`
- Redis para eventos de actualización y suscripciones
- Migraciones y seeders para PostgreSQL
- Plantillas HTML para correo
- Patrones de diseño aplicados a concerns transversales e infraestructura
- Pruebas unitarias con `pytest` y `pytest-asyncio`
- Contenedorización con Docker Compose
- Linting con `ruff`

## Stack

- Python 3.12
- FastAPI
- Ariadne
- PostgreSQL + SQLAlchemy async
- Redis
- Pydantic Settings
- Uvicorn
- PyJWT + bcrypt
- Jinja2
- Pytest
- Ruff

## Estructura del proyecto

```text
fast-api-graphql/
├── app.py
├── manage.py
├── requirements.txt
├── dockerfile
├── docker-compose.yml
├── ruff.toml
├── .env.example
└── server/
    ├── __init__.py
    ├── adapters/
    ├── config/
    ├── constants/
    ├── core/
    ├── db/
    ├── decorators/
    ├── enums/
    ├── helpers/
    ├── middlewares/
    ├── models/
    ├── observers/
    ├── repositories/
    ├── schema/
    ├── services/
    ├── strategies/
    ├── templates/
    └── utils/
```

Capas principales:

- `server/schema/`: SDL GraphQL y resolvers
- `server/services/`: lógica de negocio
- `server/repositories/`: acceso a datos
- `server/models/`: modelos DTO y entidades ORM
- `server/db/`: conexión y sesión async
- `server/migrations/`: migraciones DDL versionadas con tabla `schema_migrations`
- `server/seeders/`: datos base
- `server/adapters/`: adaptación de transportes o proveedores externos a contratos internos
- `server/strategies/`: políticas intercambiables de negocio/autorización
- `server/observers/`: eventos de dominio y observers de infraestructura
- `server/decorators/`: autenticación, autorización y ciclo de vida Singleton
- `tests/`: pruebas unitarias de servicios, repositorios, resolvers, DTOs, seguridad y patrones
- `docs/`: análisis y documentación de evolución del proyecto

## Requisitos

### Opción recomendada

- Docker
- Docker Compose

### Opción local

- Python 3.12
- PostgreSQL
- Redis, requerido para publicación/suscripción de eventos de usuario

## Configuración

La fuente de verdad para variables de entorno es `server/config/settings.py`.

1. Copia el archivo de ejemplo:

```bash
cp .env.example .env
```

2. Ajusta los valores según tu entorno.

Variables esperadas por la aplicación:

```env
PORT=8000
APP_NAME=GraphQL API
DEBUG=true

JWT_SECRET_KEY=change_this_to_a_strong_access_secret
JWT_REFRESH_SECRET_KEY=change_this_to_a_strong_refresh_secret

ACCESS_COOKIE_NAME=access_token
REFRESH_COOKIE_NAME=refresh_token
SESSION_SECRET_KEY=change_this_to_a_strong_session_secret
SESSION_MAX_AGE=86400

POSTGRES_SERVER=postgres
POSTGRES_PORT=5432
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=graphqlapp
REDIS_URL=redis://redis:6379/0
RUN_SEEDERS=true

MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=true
MAIL_USE_SSL=false
MAIL_USERNAME=your_email@example.com
MAIL_PASSWORD=your_app_password
MAIL_DEFAULT_SENDER=no-reply@example.com

FRONTEND_URL=http://localhost:5173/
CORS_ORIGINS=http://localhost:5000,http://localhost:5173,http://127.0.0.1:5173,http://localhost:3000,https://studio.apollographql.com
```

Notas:

- `CORS_ORIGINS` se parsea como una cadena separada por comas
- `PORT` lo consume Docker Compose/Uvicorn; no forma parte de `Settings`
- `RUN_SEEDERS=true` permite que `seed-all` ejecute los seeders; las migraciones se ejecutan independientemente
- en Docker Compose el contenedor usa `POSTGRES_SERVER=postgres`
- en desarrollo local normalmente se usan `POSTGRES_SERVER=localhost` y `REDIS_URL=redis://localhost:6379/0`
- nunca publiques `.env`; usa `.env.example` como plantilla sin secretos reales

## Ejecutar con Docker Compose

La forma más simple de levantar el proyecto es con Docker Compose:

```bash
docker-compose up -d --build
```

Esto levanta:

- `api`
- `postgres`
- `redis`

El servicio `api` ejecuta al iniciar:

```bash
python manage.py migrate
python manage.py seed-all  # se omite internamente si RUN_SEEDERS=false
uvicorn app:app --host 0.0.0.0 --port $PORT --reload --ws websockets --proxy-headers
```

Comandos útiles:

```bash
docker-compose up -d --build
docker-compose logs -f api
docker-compose down
```

La API queda disponible en:

- `http://localhost:<PORT>`
- GraphQL Explorer: `http://localhost:<PORT>/graphql`
- Health check: `http://localhost:<PORT>/ping`

## Ejecutar localmente

1. Crea y activa un entorno virtual:

```bash
python -m venv .venv
source .venv/bin/activate
```

2. Instala dependencias:

```bash
pip install -r requirements.txt
```

3. Asegúrate de tener PostgreSQL y Redis disponibles y configura `.env`

Ejemplo local:

```env
POSTGRES_SERVER=localhost
POSTGRES_PORT=5432
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=graphqlapp
REDIS_URL=redis://localhost:6379/0
```

4. Corre migraciones:

```bash
python manage.py migrate
```

5. Si quieres datos base, ejecuta seeders:

```bash
python manage.py seed-all
```

6. Levanta la API:

```bash
uvicorn app:app --host 0.0.0.0 --port 8000 --reload --ws websockets
```

## Migraciones y seeders

`manage.py` expone los siguientes comandos:

- `python manage.py migrate`
- `python manage.py seed-modules`
- `python manage.py seed-actions`
- `python manage.py seed-permissions`
- `python manage.py seed-roles`
- `python manage.py seed-project-roles`
- `python manage.py seed-demo`
- `python manage.py seed-users`
- `python manage.py seed-all`
- `python manage.py status`

Qué hace cada uno:

- `migrate`: aplica migraciones DDL pendientes en PostgreSQL y las registra en `schema_migrations`
- `seed-modules`: crea módulos base
- `seed-actions`: crea acciones base
- `seed-permissions`: genera permisos a partir de módulos y acciones
- `seed-roles`: crea roles base
- `seed-project-roles`: crea roles y permisos propios de proyecto
- `seed-demo`: crea escenarios demostrativos de proyectos, miembros y tareas
- `seed-users`: crea usuarios base
- `seed-all`: ejecuta todos los seeders si `RUN_SEEDERS=true`; no sustituye a `migrate`
- `status`: muestra migraciones aplicadas

## Endpoints disponibles

Rutas HTTP principales:

- `GET /`
- `GET /ping`
- `GET /graphql`
- `POST /graphql`

También existe soporte WebSocket en:

- `WS /graphql`

## Desarrollo

Validación recomendada:

```bash
ruff check .
python -m pytest
python manage.py status
```

`manage.py status` necesita una instancia PostgreSQL accesible. Para cambios GraphQL o de persistencia valida también
`GET /ping`, `GET /graphql`, la operación afectada y las migraciones/seeders involucrados.

Formato/estilo actual:

- `ruff.toml` usa `line-length = 120`
- `target-version = "py312"`

El repositorio también incluye hooks de `pre-commit` para Ruff, validaciones de archivos, detección de secretos y pytest:

```bash
pre-commit install
pre-commit run --all-files
```

## Arquitectura de GraphQL

El esquema se compone cargando todos los archivos `.graphql` desde `server/schema/` y uniendo resolvers desde:

- `hello`
- `auth`
- `users`
- `roles`
- `modules`
- `actions`
- `permission`
- `projects`
- `project_members`
- `tasks`
- `audit_logs`

Cuando agregues un nuevo dominio:

1. crea `server/schema/<dominio>/schema.graphql`
2. implementa su resolver
3. regístralo en `server/schema/__init__.py`
4. añade servicio/repositorio/migración si aplica
5. crea o actualiza pruebas unitarias para el caso exitoso y al menos un caso negativo relevante

Regla de capas:

- El resolver recibe la operación GraphQL y delega.
- El servicio concentra reglas de negocio.
- El repositorio encapsula SQLAlchemy/PostgreSQL.
- Los cambios de estructura, restricciones o índices requieren una migración versionada.

## Autenticación y autorización

- `@require_token` valida JWT desde `Authorization: Bearer` o cookies e inyecta `current_user`.
- `@require_permission(type, action)` exige un permiso global concreto.
- `@require_permissions(permissions, mode)` combina permisos mediante `PermissionCheckMode.ANY` o `.ALL`.
- `AuthorizationService` aplica autorización contextual sobre proyectos, membresías, roles de proyecto y ownership de tareas.
- Los rechazos de autenticación/autorización se expresan como errores GraphQL con códigos HTTP `401` o `403`.

Ejemplo:

```python
from server.decorators.require_permission_decorator import PermissionCheckMode, require_permissions
from server.decorators.require_token_decorator import require_token


@require_token
@require_permissions(
    permissions=[
        {"type": "users", "action": "read"},
        {"type": "roles", "action": "read"},
    ],
    mode=PermissionCheckMode.ALL,
)
async def resolve_admin_view(self, parent, info):
    ...
```

## Patrones de diseño

Los patrones se usan únicamente donde reducen acoplamiento o aíslan una política que puede variar:

| Patrón | Ubicación | Uso actual |
|---|---|---|
| Singleton | `server/decorators/singleton_decorator.py` | Una instancia por proceso para helpers, repositorios y servicios compartidos. |
| Strategy | `server/strategies/permission_check_strategy.py` | Políticas `ANY` y `ALL` para combinar permisos. |
| Factory | `PermissionCheckStrategyFactory` | Construye la estrategia correspondiente a `PermissionCheckMode`. |
| Observer | `server/observers/` | Desacopla `UserService` de la publicación del evento `UserUpdatedEvent`. |
| Adapter | `server/adapters/websocket_request_adapter.py` | Expone headers/cookies de WebSocket con el contrato esperado por autenticación. |
| Decorator | `server/decorators/require_*` | Aplica autenticación y RBAC sin mezclar esas reglas con resolvers. |

Para agregar un modo de permisos, implementa `PermissionCheckStrategy`, registra la clase en
`PermissionCheckStrategyFactory` y añade pruebas de aceptación/rechazo. Para reaccionar a una actualización de usuario,
implementa un observer async con `update(event)` y adjúntalo al publisher; define explícitamente si sus fallos deben
propagarse o aislarse.

No uses Singleton para estado por request o compartido entre workers. No agregues factories, adapters u observers sin un
contrato o una variación real. La guía completa está en
`docs/011_patrones_diseno_aplicados_y_evolucion_20260809120000.md`.

## Pruebas

La suite cubre servicios, repositorios con mocks/fakes, resolvers, DTOs, autenticación, autorización, seeders y patrones:

```bash
python -m pytest
```

Toda modificación de lógica ejecutable debe incluir o actualizar pruebas para el flujo exitoso y al menos un caso negativo.

## Dockerfile

La imagen usa una estrategia multi-stage:

- `lint`: ejecuta `ruff check .`
- `builder`: instala dependencias en un virtualenv
- `runtime`: copia el entorno y levanta `uvicorn`

En runtime, el contenedor ejecuta:

```bash
python manage.py migrate && \
if [ "$RUN_SEEDERS" = "true" ]; then python manage.py seed-all; fi && \
uvicorn app:app --host 0.0.0.0 --port 8000 --ws websockets --proxy-headers
```

## Estado actual

- El esquema incluye autenticación, catálogo RBAC, usuarios, proyectos, miembros, tareas y auditoría.
- Existen migraciones versionadas y seeders administrados desde `manage.py`.
- `.env.example` documenta la configuración principal, pero `server/config/settings.py` sigue siendo la fuente de verdad.
- `.env` puede contener credenciales reales y no debe incorporarse al repositorio.
