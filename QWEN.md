# Project Context: FastAPI GraphQL API

## Project Overview

This is a backend API built with **FastAPI**, **Ariadne** (GraphQL), and **MongoDB** (via async `motor` driver). The project is designed around JWT authentication, role-based access control (RBAC), and management of users, roles, modules, actions, and permissions. It supports both HTTP and WebSocket for GraphQL operations.

### Key Features
- GraphQL API over FastAPI with Ariadne
- HTTP and WebSocket support for GraphQL
- JWT authentication with access/refresh tokens (cookie and header support)
- RBAC with roles, permissions, modules, and actions
- Async MongoDB persistence via `motor`
- Database migrations and seeders
- HTML email templates via Jinja2
- Docker Compose containerization
- Code linting with `ruff`

## Tech Stack

- **Python 3.12**
- **FastAPI** (0.115.6) — web framework
- **Ariadne** (0.26.2) — GraphQL schema-first library
- **MongoDB 7** + **Motor** (3.7.0) — async database driver
- **Pydantic Settings** (2.12.0) — environment configuration
- **Uvicorn** (0.30.6) — ASGI server
- **Ruff** (0.15.1) — linter/formatter
- **Redis** (6.4.0) — caching/session (available but optional)
- **PyJWT** (2.10.1) — JWT token handling
- **bcrypt** (4.3.0) — password hashing
- **Jinja2** (3.1.6) — email templates

## Project Structure

```
fast-api-graphql/
├── app.py                      # Entry point: creates FastAPI app
├── manage.py                   # CLI for migrations and seeders
├── requirements.txt            # Python dependencies
├── dockerfile                  # Multi-stage Docker build (lint → builder → runtime)
├── docker-compose.yml          # Compose: api + mongo + redis
├── ruff.toml                   # Linter config (line-length=120, py312)
├── .env.example                # Environment variable template
├── .pre-commit-config.yaml     # Pre-commit hooks
└── server/
    ├── __init__.py             # FastAPI app factory, middlewares, routes, WS handler
    ├── config/                 # Settings (pydantic-settings)
    ├── constants/              # Application constants
    ├── core/                   # Core application logic
    ├── db/                     # MongoDB connection, migrations, seeders
    ├── decorators/             # @require_token, @require_permission
    ├── enums/                  # Enumerations (HTTP error codes, etc.)
    ├── helpers/                # Shared utilities (logger, mail, redis, template)
    ├── middlewares/            # Cookie logging, WS logging
    ├── models/                 # Data models / response schemas
    ├── repositories/           # MongoDB data access layer
    ├── schema/                 # GraphQL SDL (.graphql files) and resolvers
    │   ├── actions/
    │   ├── auth/
    │   ├── hello/
    │   ├── modules/
    │   ├── notes/
    │   ├── permission/
    │   ├── roles/
    │   └── users/
    ├── services/               # Business logic layer
    ├── templates/              # HTML email templates
    └── utils/                  # Utility functions (auth, error formatting)
```

### Architecture Layers

| Layer | Purpose |
|-------|---------|
| `server/schema/` | GraphQL SDL and resolvers — receives requests and delegates |
| `server/services/` | Business logic — concentrates domain rules |
| `server/repositories/` | Data access — encapsulates MongoDB queries |
| `server/models/` | Data models and response schemas |
| `server/db/` | Connection, migrations, and seeders |

**Design rule:** Avoid placing complex logic directly in resolvers. Resolvers should receive the request and delegate to services/repositories.

## Building and Running

### Docker Compose (Recommended)

```bash
docker-compose up -d --build
```

This starts `api`, `mongo`, and `redis` services. On startup, the API runs migrations and seeders automatically.

- API: `http://localhost:<PORT>` (port from `.env`)
- GraphQL Explorer: `http://localhost:<PORT>/graphql`
- Health check: `http://localhost:<PORT>/ping`

Logs:
```bash
docker-compose logs -f api
docker-compose down
```

### Local Development

```bash
# 1. Create and activate venv
python -m venv .venv
source .venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure .env (copy from .env.example)
cp .env.example .env
# Edit .env with your values (MONGO_URI=mongodb://localhost:27017 for local)

# 4. Run migrations
python manage.py migrate

# 5. Seed base data (optional)
python manage.py seed-all

# 6. Start the API
uvicorn app:app --host 0.0.0.0 --port 8000 --reload --ws websockets
```

### Linting

```bash
ruff check .
```

## Configuration

The source of truth for environment variables is `server/config/settings.py`. Key variables:

| Variable | Purpose |
|----------|---------|
| `JWT_SECRET_KEY` | Access token signing secret |
| `JWT_REFRESH_SECRET_KEY` | Refresh token signing secret |
| `SESSION_SECRET_KEY` | Session cookie secret |
| `MONGO_URI` | MongoDB connection string |
| `MONGO_DB_NAME` | Database name |
| `REDIS_URL` | Redis connection URL (default: `redis://redis:6379/0`) |
| `MAIL_*` | SMTP settings for email sending |
| `FRONTEND_URL` | Frontend base URL (for CORS/links) |
| `CORS_ORIGINS` | Comma-separated list of allowed origins |
| `RUN_SEEDERS` | Enable/disable global seeders (`true`/`false`) |

## Database Management

`manage.py` provides these commands:

| Command | Description |
|---------|-------------|
| `python manage.py migrate` | Apply migrations and indexes |
| `python manage.py seed-modules` | Seed base modules |
| `python manage.py seed-actions` | Seed base actions |
| `python manage.py seed-permissions` | Generate permissions from modules + actions |
| `python manage.py seed-roles` | Seed base roles |
| `python manage.py seed-users` | Seed base users |
| `python manage.py seed-all` | Run migrations + all seeders |
| `python manage.py status` | Show applied migrations |

## Authentication & Authorization

### JWT Decorators

Located in `server/decorators/`:

**`@require_token`** — Verifies JWT (from `Authorization: Bearer` header or cookies). Injects `current_user` into `info.context["current_user"]`.

**`@require_permission(type, action)`** — Checks a single permission. Must be used after `@require_token`.

**`@require_permissions(permissions, mode)`** — Checks multiple permissions simultaneously. `mode` can be `PermissionCheckMode.ANY` (at least one) or `PermissionCheckMode.ALL` (all required).

Example:
```python
from server.decorators.require_token_decorator import require_token
from server.decorators.require_permission_decorator import require_permission

class UserResolver:
    @require_token
    @require_permission(type="users", action="create")
    async def resolve_create_user(self, _, info, input):
        ...
```

### Permission Structure

Permissions are objects `{type, action}` where:
- `type`: module key (e.g., `"users"`, `"roles"`, `"permissions"`)
- `action`: action key (e.g., `"create"`, `"read"`, `"update"`, `"delete"`)

The `UserRepository.aggregate_user_with_role_permissions()` resolves user permissions by joining `users`, `roles`, `permissions`, `modules`, and `actions` collections.

## Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/` | Root info |
| GET | `/ping` | Health check |
| GET | `/graphql` | GraphQL Explorer (GraphiQL) |
| POST | `/graphql` | GraphQL HTTP endpoint |
| WS | `/graphql` | GraphQL WebSocket (subscriptions) |

## GraphQL Schema Architecture

The schema is built by loading all `.graphql` files from `server/schema/` and merging resolvers from:
- `hello`
- `auth`
- `users`
- `roles`
- `modules`
- `actions`
- `permission`

### Adding a New Domain

1. Create `server/schema/<domain>/schema.graphql`
2. Implement the resolver class
3. Register it in `server/schema/__init__.py`
4. Add service/repository/migration if persistence is needed

## Docker Image

Multi-stage build:
1. **lint** — runs `ruff check .`
2. **builder** — installs dependencies in a virtualenv
3. **runtime** — copies venv, runs migrations (and optional seed-all), starts uvicorn

## Code Conventions

- Async/await throughout (motor is async)
- `ruff.toml`: `line-length = 120`, `target-version = "py312"`
- Pre-commit hooks configured (`.pre-commit-config.yaml`)
- No automated tests currently in the repository
- Business logic belongs in `services/`, not in resolvers

## Important Notes

- The `AGENTS.md` file provides detailed guidance for AI agents working on this repo
- Some README/env details may not be fully aligned with `server/config/settings.py` — always check settings.py first
- Do not commit real credentials or sensitive `.env` values
- Redis is available but optional — check `RedisHelper` for usage patterns
