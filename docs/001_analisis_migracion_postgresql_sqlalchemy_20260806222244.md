# Documentación de Cambio: 001_analisis_migracion_postgresql_sqlalchemy_20260806222244

**Fecha / Timestamp**: 2026-08-06 22:22:44 (-06:00)  
**Autor**: Antigravity Assistant  
**Tipo**: Análisis y Plan de Arquitectura  

---

## 1. Objetivo del Cambio

Migrar el backend de la API GraphQL en FastAPI desde **MongoDB (Motor)** hacia **PostgreSQL** usando **SQLAlchemy 2.0 (Async)**, **Alembic** para migraciones relacionales y **UUIDv4** para claves primarias en lugar de `ObjectId`.

Asimismo, reestructurar la arquitectura de archivos del backend extrayendo las migraciones y seeders fuera de `server/db/` (a `server/migrations/` y `server/seeders/`), y segmentando `server/models/` claramente entre entidades ORM (`server/models/orm/`) y objetos DTO de Pydantic (`server/models/dto/`).

---

## 2. Modificaciones Realizadas

### 2.1. `docker-compose.yml`
Se sustituyó el servicio de MongoDB por PostgreSQL 16 Alpine y se ajustaron las variables de entorno de la API:

- **Servicio `postgres`**:
  - Imagen: `postgres:16-alpine`
  - Puerto: `5432:5432`
  - Variables: `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB`
  - Volumen: `postgres_data:/var/lib/postgresql/data`
- **Servicio `api`**:
  - Dependencia actualizada a `postgres` y `redis`.
  - Variables añadidas: `POSTGRES_SERVER`, `POSTGRES_PORT`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB`.

### 2.2. `dockerfile`
Se añadieron los paquetes necesarios para compilar y ejecutar **`psycopg2`** nativo desde código fuente:
- **Etapa `builder`**: Paquetes `libpq-dev` y `build-essential` para poder compilar la extensión C de `psycopg2`.
- **Etapa `runtime`**: Paquete `libpq5` necesario para ejecutar las librerías dinámicas del cliente de PostgreSQL en producción sin requerir herramientas de compilación.

---

## 3. Plan de Arquitectura e Integración de SQLAlchemy 2.0

### 3.1. Reorganización del Módulo `server/`

Se segmenta el proyecto por capas claras y desacopladas:

```
server/
├── db/                         # Únicamente conexión y motor SQLAlchemy Async
│   ├── __init__.py
│   └── session.py              # Engine, AsyncSession, get_db_session()
├── migrations/                 # Migraciones DDL (scripts numerados / Alembic)
│   ├── env.py
│   └── versions/
│       └── 001_initial_schema_postgresql_20260806222244.py
├── models/                     # Modelos segmentados por responsabilidad
│   ├── dto/                    # Schemas de entrada/salida Pydantic (DTOs)
│   │   ├── user_dto.py
│   │   ├── role_dto.py
│   │   ├── module_dto.py
│   │   ├── action_dto.py
│   │   └── permission_dto.py
│   └── orm/                    # Entidades declarativas SQLAlchemy (ORM)
│       ├── user_orm.py
│       ├── role_orm.py
│       ├── module_orm.py
│       ├── action_orm.py
│       └── permission_orm.py
└── seeders/                    # Carga de datos base (Módulos, Acciones, Permisos, Roles, Usuarios)
    ├── __init__.py
    ├── actions_seeder.py
    ├── modules_seeder.py
    ├── permissions_seeder.py
    ├── roles_seeder.py
    └── users_seeder.py
```

### 3.2. Dependencias (`requirements.txt`)
Se reemplaza `motor` por:
- `sqlalchemy>=2.0.30`
- `asyncpg>=0.29.0`
- `alembic>=1.13.0`
- `psycopg2>=2.9.9` (driver nativo C)

### 3.3. Configuración de Base de Datos (`server/db/session.py`)
Reemplazo de `server/db/mongo.py` por motor asíncrono con `create_async_engine` y `async_sessionmaker` usando la URL `postgresql+asyncpg://...`.

### 3.4. Modelos ORM (`server/models/orm/`)
Creación de clases declarativas heredando de `Base` con claves primarias `UUID(as_uuid=True)` predeterminadas a `uuid.uuid4`:
- `UserORM` (`users`)
- `RoleORM` (`roles`)
- `PermissionORM` (`permissions`)
- `ModuleORM` (`modules`)
- `ActionORM` (`actions`)
- Tabla intermedia `role_permissions` (`role_id`, `permission_id`)

### 3.5. Modelos DTO de Pydantic (`server/models/dto/`)
- Eliminación de validadores `ObjectId.is_valid()` y alias `_id`.
- Sustitución por `uuid.UUID`.
- Configuración de `from_attributes = True` para mapeo directo desde modelos ORM de SQLAlchemy.

### 3.6. Capa de Repositorios (`server/repositories/`)
Sustitución de llamadas a `motor` por consultas asíncronas de SQLAlchemy (`select()`, `join()`, `selectinload()`, `execute()`, `commit()`).

### 3.7. Migraciones y Seeders (`server/migrations/` y `server/seeders/`)
- Las migraciones DDL seguirán el formato: `vNNN_nombre_descriptivo_del_ddl_timestamp.py` en `server/migrations/versions/`.
- Cada migración define metadatos `version`, `description` y una función `upgrade(conn)`.
- `manage.py migrate` aplica únicamente migraciones pendientes, registradas en la tabla `schema_migrations`.
- `manage.py seed-all` instanciará los seeders desde `server/seeders/` usando `AsyncSession` de SQLAlchemy.

---

## 4. Convención de Archivos de Documentación y Migraciones

A partir de este cambio:
- **Documentación de análisis**: `/docs/NNN_nombre_descriptivo_timestamp.md`
- **Migraciones DDL/SQL**: `/server/migrations/versions/001_nombre_descriptivo_del_ddl_timestamp`
- **Modelos DTO**: `/server/models/dto/`
- **Modelos ORM**: `/server/models/orm/`
- **Seeders**: `/server/seeders/`
