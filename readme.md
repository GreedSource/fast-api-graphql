# FastAPI GraphQL API

A modern GraphQL API built with FastAPI, Ariadne, and MongoDB. This project implements a role-based access control (RBAC) system with JWT authentication, user management, permissions, and role administration.

## 📋 Table of Contents

- [Features](#features)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Configuration](#configuration)
- [Running the Application](#running-the-application)
- [Docker Support](#docker-support)
- [API Documentation](#api-documentation)
- [Project Architecture](#project-architecture)

## ✨ Features

- **GraphQL API** - Built with Ariadne for flexible query language
- **Authentication** - JWT-based token authentication
- **Role-Based Access Control (RBAC)** - Comprehensive permission system
- **User Management** - Create, read, update, and delete users
- **MongoDB Integration** - Async MongoDB support with Motor
- **Email Notifications** - Password reset and email verification
- **Error Handling** - Custom GraphQL exception handling
- **Logging** - Structured logging for debugging and monitoring
- **Docker Support** - Containerized deployment with Docker Compose
- **Code Quality** - Ruff linting and formatting

## 🛠 Tech Stack

- **Framework**: FastAPI 0.115.6
- **GraphQL**: Ariadne 0.26.2
- **Database**: MongoDB 4.16.0 with Motor 3.7.0 (async driver)
- **Authentication**: PyJWT 2.10.1, bcrypt 4.3.0
- **Validation**: Pydantic 2.11.7
- **Server**: Uvicorn 0.30.6 with uvloop 0.22.1
- **Linting**: Ruff 0.15.1
- **Dev Tools**: Pre-commit hooks

## 📁 Project Structure

```
fast-api-graphql/
├── app.py                          # Application entry point
├── requirements.txt                # Python dependencies
├── dockerfile                      # Docker image definition
├── docker-compose.yml              # Docker Compose configuration
├── ruff.toml                       # Ruff linting configuration
├── readme.md                       # This file
└── server/
    ├── __init__.py                 # Application factory
    ├── config/
    │   └── settings.py             # Configuration settings
    ├── constants/
    │   └── error_messages.py       # Error message constants
    ├── core/
    │   └── lifespan.py             # Application lifecycle management
    ├── db/
    │   └── mongo.py                # MongoDB client configuration
    ├── decorators/
    │   ├── require_token_decorator.py    # JWT token validation
    │   └── singleton_decorator.py        # Singleton pattern
    ├── enums/
    │   └── http_error_code_enum.py      # HTTP error code enums
    ├── helpers/
    │   ├── custom_graphql_exception_helper.py  # GraphQL exceptions
    │   ├── logger_helper.py             # Logging utilities
    │   ├── mail_helper.py               # Email sending
    │   └── mongo_helper.py              # MongoDB utilities
    ├── middlewares/
    │   └── cookie_logging_middleware.py # Request logging middleware
    ├── models/
    │   ├── action_model.py              # Action data model
    │   ├── module_model.py              # Module data model
    │   ├── permission_model.py          # Permission data model
    │   ├── response_model.py            # API response model
    │   ├── role_model.py                # Role data model
    │   └── user_model.py                # User data model
    ├── repositories/
    │   ├── action_repository.py         # Action database access
    │   ├── module_repository.py         # Module database access
    │   ├── permission_repository.py     # Permission database access
    │   ├── role_repository.py           # Role database access
    │   └── user_repository.py           # User database access
    ├── schema/
    │   ├── __init__.py
    │   ├── schema.graphql               # Main GraphQL schema
    │   ├── actions/
    │   │   ├── action_resolver.py       # Action resolvers
    │   │   └── schema.graphql           # Action schema
    │   ├── auth/
    │   │   ├── resolver.py              # Authentication resolvers
    │   │   └── schema.graphql           # Auth schema
    │   ├── hello/
    │   │   ├── resolver.py              # Health check resolver
    │   │   └── schema.graphql           # Hello schema
    │   ├── modules/
    │   │   ├── resolver.py              # Module resolvers
    │   │   └── schema.graphql           # Module schema
    │   ├── permission/
    │   │   ├── resolver.py              # Permission resolvers
    │   │   └── schema.graphql           # Permission schema
    │   ├── roles/
    │   │   ├── resolver.py              # Role resolvers
    │   │   └── schema.graphql           # Role schema
    │   └── users/
    │       ├── resolver.py              # User resolvers
    │       └── schema.graphql           # User schema
    ├── services/
    │   ├── action_service.py            # Action business logic
    │   ├── auth_service.py              # Authentication logic
    │   ├── module_service.py            # Module business logic
    │   ├── permission_service.py        # Permission business logic
    │   ├── role_service.py              # Role business logic
    │   └── user_service.py              # User business logic
    ├── templates/
    │   └── emails/
    │       └── reset_password.html      # Password reset email template
    │   └── layouts/
    │       └── base_template.html       # Base email template
    └── utils/
        ├── auth_utils.py                # Authentication utilities
        └── custom_error_formatter_utils.py  # Error formatting
```

## 📋 Prerequisites

### For Docker (Recommended)

- Docker 20.10+
- Docker Compose 2.0+
- Git

### For Local Development (Optional)

- Python 3.9+
- MongoDB 4.0+
- Git

## 🚀 Quick Start

### 1. Clone the Repository

```bash
git clone <repository-url>
cd fast-api-graphql
```

### 2. Start with Docker Compose

```bash
# Build and start the application
docker-compose up -d --build
```

The application will be running at `http://localhost:5000`

### Local Development Setup (Optional)

If you prefer developing locally without Docker:

```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the application
python app.py
```

## 🧱 Migraciones y Seeders

Este proyecto ahora incluye un pequeño sistema de migraciones para MongoDB y un seeder de usuarios:

- `manage.py migrate`: aplica migraciones (`migrations` collection + índices + validadores JSON Schema)
- `manage.py seed-modules`: crea módulos básicos
- `manage.py seed-actions`: crea acciones básicas
- `manage.py seed-permissions`: crea permisos básicos a partir de módulos y acciones existentes
- `manage.py seed-roles`: crea roles admin/user
- `manage.py seed-users`: crea users admin/user base
- `manage.py seed-all`: ejecuta migraciones + todos los seeders
- `manage.py status`: lista migraciones aplicadas

Uso:

```bash
# Desde la raíz del proyecto
python manage.py migrate
python manage.py seed-users
python manage.py status
```

> Nota: Las migraciones aplican esquema utilizando `collMod` y `create_collection` con `validationAction="error"` para que Mongo valide los campos.

## ⚙️ Configuration

When using Docker Compose, the application is pre-configured and ready to run out of the box.

For custom configuration or local development, create a `.env` file in the project root:

```env
# MongoDB Configuration
MONGODB_URL=mongodb://localhost:27017
MONGODB_DB_NAME=rbac

# JWT Configuration
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Email Configuration
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SENDER_EMAIL=noreply@example.com

# Environment
ENVIRONMENT=development
DEBUG=True

# Seeders control
# Si true, manage.py seed-all correrá los seeders
# Si false, solo corre migraciones (ó corre cada seeder explícito si se quiere)
RUN_SEEDERS=false
```

## 🏃 Running the Application

### 🐳 Recommended: Docker Compose (with Hot Reload)

The project is pre-configured for hot reload development using Docker Compose:

```bash
# Build and start containers in detached mode
docker-compose up -d --build

# View logs in real-time
docker-compose logs -f app

# Stop containers
docker-compose down
```

The API will be available at `http://localhost:5000`

GraphQL playground: `http://localhost:5000/graphql`

**Benefits**: Hot reload on code changes, MongoDB pre-configured, isolated environment, no local setup required.

### Local Development (Optional)

For local development without Docker:

```bash
# Ensure MongoDB is running locally
python app.py
```

### Production Mode

```bash
uvicorn server:create_app --host 0.0.0.0 --port 5000 --workers 4
```

## 🐳 Docker Support

### Quick Start with Docker Compose (Recommended)

The recommended way to run this project is with Docker Compose, which includes hot reload for development:

```bash
# Build and start containers in detached mode with hot reload
docker-compose up -d --build

# View application logs
docker-compose logs -f app

# Stop containers
docker-compose down
```

The application will be available at `http://localhost:5000`

The Docker setup includes:

- **Hot Reload**: Automatic restart on code changes
- **MongoDB Integration**: Pre-configured MongoDB instance
- **Development-Ready**: All dependencies installed and configured
- **Volume Mounting**: Source code synced for live development

### Build Docker Image (Manual)

```bash
docker build -t fastapi-graphql:latest .
```

### Run Docker Container (Manual)

```bash
# Con base en la nueva Dockerfile, migraciones se ejecutan automáticamente en start
# y seeders se ejecutan solo si RUN_SEEDERS=true

# Sin seeders:
docker run -e RUN_SEEDERS=false -p 5000:8000 fastapi-graphql:latest

# Con seeders:
docker run -e RUN_SEEDERS=true -p 5000:8000 fastapi-graphql:latest

# Si deseas solo migraciones:
docker run -e RUN_SEEDERS=false -p 5000:8000 fastapi-graphql:latest

```
docker run -p 5000:5000 \
  -e MONGODB_URL=mongodb://mongo:27017 \
  -e SECRET_KEY=your-secret \
  fastapi-graphql:latest
```

## 📚 API Documentation

### Authentication

All protected endpoints require a JWT token in the Authorization header:

```
Authorization: Bearer <your-jwt-token>
```

### GraphQL Endpoints

- **Main Endpoint**: POST `/graphql`
- **Subscriptions**: WebSocket `/subscriptions`
- **GraphQL Playground**: GET `/graphql` (development only)
- **Health Check**: GET `/hello`

### Core Queries & Mutations

The API includes the following GraphQL operations:

- **Authentication**: Login, logout, token refresh
- **User Management**: Create, read, update, delete users
- **Roles**: Create and manage user roles
- **Permissions**: Define and assign permissions
- **Modules**: Manage application modules
- **Actions**: Track user actions and audit logs

## 🏗 Project Architecture

### Design Patterns

- **Repository Pattern**: Database access layer separation
- **Service Layer**: Business logic encapsulation
- **Factory Pattern**: Application initialization
- **Singleton Pattern**: Shared resource management
- **Middleware Pattern**: Request/response processing

### Authentication Flow

1. User submits credentials via `login` mutation
2. System verifies credentials against hashed passwords
3. JWT token is generated with user claims
4. Token is returned to client
5. Client includes token in subsequent requests
6. Token is validated via decorator before accessing protected resolvers

### Database Layer

- MongoDB is the primary data store
- Motor provides async database operations
- Repositories handle all database queries
- Services contain business logic

### Error Handling

- Custom GraphQL exceptions for consistent error responses
- Error formatting utility for standardized error messages
- HTTP error code enums for consistency
- Detailed logging for debugging

## 🧪 Code Quality

### Linting & Formatting

```bash
# Run Ruff linter
ruff check .

# Format code with Ruff
ruff format .
```

### Pre-commit Hooks

```bash
# Install pre-commit hooks
pre-commit install

# Run all hooks
pre-commit run --all-files
```

## 📝 License

This project is proprietary and confidential.

## 💬 Support

For questions or issues, please contact the development team or open an issue in the repository.

---

**Last Updated**: February 2026
