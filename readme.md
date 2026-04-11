# FastAPI GraphQL API

API backend construida con `FastAPI`, `Ariadne` y `MongoDB`, orientada a autenticación JWT, control de acceso por roles (RBAC) y administración de usuarios, roles, módulos, acciones y permisos.

## Características

- API GraphQL sobre `FastAPI`
- Soporte HTTP y WebSocket para GraphQL
- Autenticación con JWT
- RBAC con roles, permisos, módulos y acciones
- Persistencia async con `motor`
- Migraciones y seeders para MongoDB
- Plantillas HTML para correo
- Contenedorización con Docker Compose
- Linting con `ruff`

## Stack

- Python 3.12
- FastAPI
- Ariadne
- MongoDB + Motor
- Pydantic Settings
- Uvicorn
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
    ├── config/
    ├── constants/
    ├── core/
    ├── db/
    ├── decorators/
    ├── enums/
    ├── helpers/
    ├── middlewares/
    ├── models/
    ├── repositories/
    ├── schema/
    ├── services/
    ├── templates/
    └── utils/
```

Capas principales:

- `server/schema/`: SDL GraphQL y resolvers
- `server/services/`: lógica de negocio
- `server/repositories/`: acceso a datos
- `server/models/`: modelos usados por el dominio
- `server/db/`: conexión, migraciones y seeders

## Requisitos

### Opción recomendada

- Docker
- Docker Compose

### Opción local

- Python 3.12
- MongoDB

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

MONGO_URI=mongodb://root:example@mongo:27017
MONGO_DB_NAME=graphqlapp
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
- `RUN_SEEDERS=true` permite que `seed-all` ejecute seeders
- en Docker Compose el contenedor usa `MONGO_URI=mongodb://root:example@mongo:27017`

## Ejecutar con Docker Compose

La forma más simple de levantar el proyecto es con Docker Compose:

```bash
docker-compose up -d --build
```

Esto levanta:

- `api`
- `mongo`

El servicio `api` ejecuta al iniciar:

```bash
python manage.py migrate
python manage.py seed-all
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

3. Asegúrate de tener MongoDB disponible y configura `.env`

Ejemplo local:

```env
MONGO_URI=mongodb://localhost:27017
MONGO_DB_NAME=graphqlapp
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
- `python manage.py seed-users`
- `python manage.py seed-all`
- `python manage.py status`

Qué hace cada uno:

- `migrate`: aplica migraciones e índices/validaciones en MongoDB
- `seed-modules`: crea módulos base
- `seed-actions`: crea acciones base
- `seed-permissions`: genera permisos a partir de módulos y acciones
- `seed-roles`: crea roles base
- `seed-users`: crea usuarios base
- `seed-all`: corre migraciones y seeders
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

Lint:

```bash
ruff check .
```

Formato/estilo actual:

- `ruff.toml` usa `line-length = 120`
- `target-version = "py312"`

## Arquitectura de GraphQL

El esquema se compone cargando todos los archivos `.graphql` desde `server/schema/` y uniendo resolvers desde:

- `hello`
- `auth`
- `users`
- `roles`
- `modules`
- `actions`
- `permission`

Cuando agregues un nuevo dominio:

1. crea `server/schema/<dominio>/schema.graphql`
2. implementa su resolver
3. regístralo en `server/schema/__init__.py`
4. añade servicio/repositorio/migración si aplica

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

- No se observan tests automatizados en el repositorio
- `.env.example` ya está alineado con `settings.py`
- algunas credenciales reales pueden existir en `.env`; no las copies al repositorio
