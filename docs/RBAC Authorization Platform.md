# RBAC Authorization Platform

## 1. Overview

Este proyecto implementa un sistema de autorización basado en **Role-Based Access Control (RBAC)** diseñado para ser reutilizable por diferentes aplicaciones.

El objetivo inicial es construir un **MVP de gestión de proyectos** que permita demostrar las capacidades del sistema de autorización en un caso de uso real.

La arquitectura parte de un modelo RBAC clásico:

```text
User
  │
  ▼
Role
  │
  ▼
Permission
  │
  ├── Module
  └── Action
```

La aplicación evolucionará posteriormente hacia un modelo de autorización más granular, permitiendo:

- Roles globales.
- Roles específicos por proyecto.
- Permisos por recurso.
- Autorización contextual.
- Auditoría.
- Control de acceso desde backend y frontend.
- Políticas de autorización reutilizables.

---

# 2. Objetivos

## Objetivo principal

Construir una plataforma de gestión de proyectos que utilice un sistema RBAC propio como núcleo de autorización.

El proyecto debe servir simultáneamente como:

1. MVP funcional.
2. Demostración técnica de RBAC.
3. Proyecto de portafolio.
4. Base para futuros proyectos.
5. Ejemplo de arquitectura backend/frontend.
6. Demostración de autorización a nivel de recurso.

---

# 3. Estado actual

Actualmente el sistema implementa:

```text
Users
Roles
Modules
Actions
Permissions
Role Permissions
```

La relación actual es:

```text
User
  │
  │ role_id
  ▼
Role
  │
  │ role_permissions
  ▼
Permission
  │
  ├──────────────┐
  ▼              ▼
Module         Action
```

Una autorización puede representarse conceptualmente como:

```text
users + create
```

que corresponde a:

```text
Module = users
Action = create
```

---

# 4. Modelo actual

## 4.1 Users

Los usuarios pertenecen actualmente a un único rol.

```text
users
├── id
├── name
├── lastname
├── email
├── password
├── is_active
├── role_id
├── created_at
└── updated_at
```

Relación:

```text
User N ───── 1 Role
```

---

## 4.2 Roles

Los roles representan agrupaciones de permisos.

Ejemplos:

```text
admin
project_manager
developer
client
viewer
```

Actualmente un usuario tiene un único rol global.

---

## 4.3 Modules

Los módulos representan recursos o áreas funcionales del sistema.

Ejemplos actuales:

```text
users
roles
permissions
modules
actions
```

Para la aplicación de gestión de proyectos se agregarán:

```text
projects
tasks
teams
members
milestones
reports
documents
activity
```

---

## 4.4 Actions

Las acciones representan operaciones que pueden realizarse sobre un módulo.

Ejemplos:

```text
create
read
update
delete
```

Se pueden extender con acciones más específicas:

```text
assign
approve
archive
export
manage
publish
restore
```

---

# 5. Permissions

Una de las decisiones importantes del sistema es separar:

```text
Module
+
Action
=
Permission
```

Por ejemplo:

```text
users + create
```

representa:

```text
users.create
```

Mientras:

```text
projects + update
```

representa:

```text
projects.update
```

La tabla `permissions` actualmente garantiza que no exista más de una combinación:

```text
(module_id, action_id)
```

Esto permite construir un catálogo de permisos consistente.

---

# 6. Permisos expuestos al frontend

Actualmente el login devuelve una estructura similar a:

```json
{
  "user": {
    "id": "uuid",
    "name": "Admin",
    "lastname": "Root",
    "email": "admin@example.com",
    "role": {
      "name": "admin",
      "permissions": [
        {
          "type": "users",
          "action": "create"
        },
        {
          "type": "users",
          "action": "read"
        },
        {
          "type": "users",
          "action": "update"
        },
        {
          "type": "users",
          "action": "delete"
        }
      ]
    }
  }
}
```

Este formato es adecuado para el frontend porque permite determinar las capacidades del usuario.

Por ejemplo:

```text
users.create
users.read
users.update
users.delete
```

El frontend puede utilizar estos permisos para:

- Mostrar u ocultar botones.
- Mostrar u ocultar módulos.
- Controlar navegación.
- Deshabilitar acciones.
- Construir menús dinámicamente.

Sin embargo, el frontend **no debe considerarse una capa de seguridad**.

La autorización real siempre debe realizarse en el backend.

---

# 7. Evolución propuesta

El sistema actual puede evolucionar de:

```text
RBAC
```

hacia:

```text
RBAC
+
Resource Authorization
+
Contextual Authorization
+
Audit Logging
```

La arquitectura propuesta es:

```text
                    USER
                      │
                      ▼
                GLOBAL ROLE
                      │
                      ▼
                PERMISSIONS
                      │
                      ▼
              AUTHORIZATION ENGINE
                      │
          ┌───────────┼────────────┐
          │           │            │
          ▼           ▼            ▼
       Project       Task        Reports
          │
          ▼
    PROJECT ROLE
          │
          ▼
    RESOURCE ACCESS
```

---

# 8. Aplicación MVP: Project Management Platform

El sistema RBAC será utilizado dentro de una aplicación de gestión de proyectos.

La aplicación tendrá como objetivo administrar:

```text
Projects
Tasks
Teams
Members
Milestones
Reports
Activity
Documents
```

El objetivo no es competir con herramientas como Jira, Linear o ClickUp.

El objetivo es demostrar cómo un sistema de autorización propio puede integrarse en una aplicación real.

---

# 9. Módulos de la aplicación

## Dashboard

```text
dashboard
```

Permite visualizar:

- Proyectos activos.
- Tareas pendientes.
- Tareas asignadas.
- Tareas atrasadas.
- Actividad reciente.
- Estadísticas.

---

## Projects

```text
projects
```

Operaciones:

```text
projects.read
projects.create
projects.update
projects.delete
projects.archive
```

---

## Tasks

```text
tasks
```

Operaciones:

```text
tasks.read
tasks.create
tasks.update
tasks.delete
tasks.assign
tasks.complete
```

---

## Teams

```text
teams
```

Operaciones:

```text
teams.read
teams.create
teams.update
teams.delete
teams.members.manage
```

---

## Reports

```text
reports
```

Operaciones:

```text
reports.read
reports.export
```

---

## Administration

Los módulos actuales pueden convertirse en el módulo administrativo:

```text
users
roles
permissions
modules
actions
```

Esto permite administrar dinámicamente el sistema RBAC desde la propia aplicación.

---

# 10. Roles iniciales

El MVP puede comenzar con los siguientes roles:

## Super Admin

Tiene acceso completo al sistema.

```text
users.*
roles.*
permissions.*
modules.*
actions.*

projects.*
tasks.*
teams.*
reports.*
```

---

## Project Manager

Puede administrar proyectos y equipos, pero no administrar el sistema RBAC.

```text
projects.read
projects.create
projects.update
projects.archive

tasks.read
tasks.create
tasks.update
tasks.delete
tasks.assign
tasks.complete

teams.read
teams.update
teams.members.manage

reports.read
reports.export
```

---

## Developer

```text
projects.read

tasks.read
tasks.create
tasks.update
tasks.complete

teams.read
```

---

## Client

```text
projects.read

tasks.read

reports.read
```

---

## Viewer

```text
projects.read

tasks.read

reports.read
```

---

# 11. Primera gran mejora: Project Roles

El sistema actual tiene:

```text
User → Role
```

Esto funciona para permisos globales, pero se vuelve limitado cuando un usuario participa en varios proyectos.

Por ejemplo:

```text
Joel
│
├── Project A → Project Manager
├── Project B → Developer
└── Project C → Viewer
```

El mismo usuario puede tener diferentes responsabilidades dependiendo del proyecto.

Para soportarlo se puede agregar:

```text
projects
project_members
project_roles
project_member_roles
```

Conceptualmente:

```text
User
 │
 ├── Global Role
 │
 └── Project Membership
        │
        └── Project Role
```

---

# 12. Project Membership

Una posible estructura:

```sql
project_members
----------------
id
project_id
user_id
created_at
updated_at
```

Relación:

```text
Project N ───── N User
```

---

# 13. Project Roles

Los roles específicos del proyecto pueden reutilizar el sistema de permisos existente.

Por ejemplo:

```text
project_manager
developer
viewer
```

Un proyecto podría tener:

```text
Project A

Members
├── Joel
│   └── Project Manager
├── Maria
│   └── Developer
└── Carlos
    └── Viewer
```

---

# 14. Resource Authorization

Aquí el sistema comienza a ser mucho más interesante.

Un permiso como:

```text
tasks.update
```

solamente indica:

> El usuario puede actualizar tareas.

Pero todavía falta responder:

> ¿Puede actualizar cualquier tarea?

La autorización puede evolucionar a:

```text
Can user update task?
        │
        ├── Does user have tasks.update?
        │
        ├── Is user member of the project?
        │
        ├── Is user the task owner?
        │
        └── Does project role allow this operation?
```

Por ejemplo:

```text
Developer

tasks.update = true

Task:
project_id = 123
assignee_id = user.id
```

Resultado:

```text
ALLOW
```

Mientras:

```text
Task:
project_id = 999
assignee_id = another-user
```

Resultado:

```text
DENY
```

---

# 15. Authorization Engine

La lógica de autorización debe centralizarse.

Evitar:

```python
if user.role.name == "admin":
    ...
```

Y evitar también:

```python
if user.role.name == "project_manager":
    ...
```

La aplicación debería utilizar una abstracción como:

```python
authorize(
    user=user,
    module="tasks",
    action="update",
    resource=task
)
```

El motor puede evaluar:

```text
1. User active?
2. Global permission?
3. Project membership?
4. Project role?
5. Resource ownership?
6. Contextual policy?
```

Resultado:

```text
ALLOW
```

o:

```text
DENY
```

---

# 16. Ejemplo de autorización

Solicitud:

```http
PATCH /tasks/{task_id}
```

El backend obtiene:

```text
Current User
Task
Project
Project Membership
Permissions
```

Y ejecuta:

```text
authorize(
    user,
    "tasks",
    "update",
    task
)
```

El Authorization Engine puede evaluar:

```text
User active?
        ↓
      YES
        ↓
Has tasks.update?
        ↓
      YES
        ↓
Member of project?
        ↓
      YES
        ↓
Project role allows update?
        ↓
      YES
        ↓
     ALLOW
```

---

# 17. Frontend Authorization

El frontend recibirá los permisos del usuario.

Por ejemplo:

```json
{
  "permissions": [
    "projects.read",
    "projects.create",
    "projects.update",
    "tasks.read",
    "tasks.create",
    "tasks.update",
    "tasks.assign"
  ]
}
```

El frontend puede utilizar una función:

```typescript
can("projects", "create")
```

o:

```typescript
can("projects.create")
```

Ejemplo:

```tsx
{can("projects.create") && (
    <CreateProjectButton />
)}
```

Otro ejemplo:

```tsx
{can("tasks.assign") && (
    <AssignTaskButton />
)}
```

Esto permite construir una interfaz completamente dinámica.

---

# 18. Backend vs Frontend

Una regla fundamental del proyecto:

```text
Frontend
    ↓
UX / Visibility

Backend
    ↓
Security / Authorization
```

Ocultar un botón no constituye seguridad.

Por ejemplo:

```text
Frontend
    └── oculta "Delete Project"

Backend
    └── debe rechazar projects.delete
```

Aunque un usuario intente realizar manualmente:

```http
DELETE /projects/123
```

el backend debe responder:

```http
403 Forbidden
```

---

# 19. Audit Log

Una funcionalidad importante del MVP avanzado será registrar acciones relevantes.

Ejemplos:

```text
Admin created user
Admin assigned role to user
Admin created permission
Joel created project
Joel assigned Maria to task
Maria updated task
Carlos attempted unauthorized action
```

Una estructura posible:

```sql
audit_logs
----------------
id
user_id
action
module
resource_type
resource_id
status
metadata
created_at
```

Ejemplo:

```json
{
  "user_id": "uuid",
  "module": "tasks",
  "action": "update",
  "resource_type": "task",
  "resource_id": "uuid",
  "status": "success",
  "metadata": {
    "changed_fields": [
      "status",
      "assignee_id"
    ]
  }
}
```

También se pueden registrar intentos rechazados:

```json
{
  "module": "projects",
  "action": "delete",
  "status": "denied"
}
```

Esto permite demostrar:

- Auditoría.
- Seguridad.
- Trazabilidad.
- Detección de accesos no autorizados.

---

# 20. Estructura de permisos

Se recomienda mantener una representación lógica uniforme:

```text
module.action
```

Ejemplos:

```text
users.read
users.create
users.update
users.delete

projects.read
projects.create
projects.update
projects.delete

tasks.read
tasks.create
tasks.update
tasks.delete
tasks.assign

reports.read
reports.export
```

Esto permite utilizar los mismos permisos en:

```text
Backend
Frontend
API
Policies
Audit logs
Tests
```

---

# 21. Evolución del modelo actual

El modelo actual:

```text
users
   │
   ▼
roles
   │
   ▼
role_permissions
   │
   ▼
permissions
   │
   ├── modules
   └── actions
```

Puede evolucionar a:

```text
users
   │
   ├───────────────────┐
   │                   │
   ▼                   ▼
global_roles      project_members
   │                   │
   ▼                   ▼
permissions       project_roles
                       │
                       ▼
                  permissions
                       │
                       ▼
                Authorization Engine
                       │
                       ▼
                  Resources
```

---

# 22. Posible modelo futuro

```text
users
roles
modules
actions
permissions
role_permissions

projects
project_members
project_roles
project_role_permissions

tasks
milestones
teams

audit_logs
```

No es necesario implementar todo en la primera versión.

---

# 23. MVP - Fase 1

La primera versión debe mantenerse pequeña.

### Authentication

- Login.
- Logout.
- Password hashing.
- JWT/session.
- Current user.

### RBAC

- Users.
- Roles.
- Modules.
- Actions.
- Permissions.
- Role permissions.

### Projects

- Create project.
- List projects.
- View project.
- Update project.
- Delete/archive project.

### Tasks

- Create task.
- Update task.
- Assign task.
- Change status.
- List tasks.

### Authorization

- Backend permission checking.
- Frontend permission checking.
- 401 Unauthorized.
- 403 Forbidden.

---

# 24. MVP - Fase 2

Agregar:

```text
Project Members
Project Roles
```

Permitiendo:

```text
User A
  └── Project A → Manager

User A
  └── Project B → Developer
```

---

# 25. MVP - Fase 3

Agregar:

```text
Resource Authorization
```

Ejemplos:

```text
Developer puede editar sus propias tareas.

Project Manager puede editar cualquier tarea
dentro de su proyecto.

Client puede consultar información,
pero no modificarla.
```

---

# 26. MVP - Fase 4

Agregar:

```text
Audit Logs
```

Con:

- Usuario.
- Acción.
- Módulo.
- Recurso.
- Resultado.
- Timestamp.
- Metadata.

---

# 27. MVP - Fase 5

Agregar políticas contextuales.

Ejemplo:

```text
tasks.update
```

No significa automáticamente:

```text
puede actualizar cualquier tarea.
```

Puede requerir:

```text
user is task owner
OR
user is project manager
OR
user is admin
```

Esto permite evolucionar de:

```text
RBAC
```

hacia:

```text
RBAC + Policy Based Authorization
```

---

# 28. Arquitectura propuesta

```text
                         ┌──────────────┐
                         │   Frontend   │
                         │ React/Flutter│
                         └──────┬───────┘
                                │
                         GraphQL / HTTP
                                │
                         ┌──────▼───────┐
                         │   FastAPI    │
                         ├──────────────┤
                         │ Auth         │
                         │ GraphQL      │
                         │ Application  │
                         └──────┬───────┘
                                │
                    ┌───────────▼────────────┐
                    │ Authorization Engine   │
                    ├────────────────────────┤
                    │ RBAC                   │
                    │ Resource Policies      │
                    │ Contextual Policies    │
                    └───────────┬────────────┘
                                │
              ┌─────────────────┼─────────────────┐
              │                 │                 │
              ▼                 ▼                 ▼
          Projects           Tasks            Users
              │                 │
              └─────────────────┘
                                │
                         ┌──────▼──────┐
                         │ PostgreSQL  │
                         └─────────────┘
```

---

# 29. Stack tecnológico

La implementación puede utilizar:

```text
Backend
├── Python
├── FastAPI
├── GraphQL
└── Ariadne

Database
└── PostgreSQL

Frontend
├── React
└── Flutter

Infrastructure
├── Docker
└── Docker Compose
```

---

# 30. Principios de diseño

## Backend is the source of truth

Los permisos enviados al frontend únicamente sirven para mejorar la experiencia de usuario.

La autorización real ocurre en backend.

---

## Authorization debe estar centralizada

La lógica no debe estar distribuida por todos los endpoints.

Debe existir un componente central:

```text
Authorization Engine
```

---

## No depender del nombre del rol

Evitar:

```python
if role == "admin":
```

Preferir:

```python
authorize(
    user,
    "projects",
    "delete"
)
```

Esto permite crear nuevos roles sin modificar código.

---

## Permisos desacoplados de la UI

El permiso:

```text
projects.create
```

no debe depender de un botón específico.

Puede utilizarse desde:

```text
GraphQL
REST
React
Flutter
CLI
Background jobs
```

---

# 31. Ejemplo de flujo completo

Un usuario inicia sesión:

```text
POST /login
```

El sistema obtiene:

```text
User
  ↓
Role
  ↓
Role Permissions
  ↓
Permissions
```

Respuesta:

```json
{
  "user": {
    "id": "uuid",
    "name": "Joel",
    "role": {
      "name": "project_manager",
      "permissions": [
        "projects.read",
        "projects.create",
        "projects.update",
        "tasks.read",
        "tasks.create",
        "tasks.update",
        "tasks.assign"
      ]
    }
  }
}
```

El frontend construye la interfaz:

```text
Dashboard
Projects
Tasks
Reports
```

Si existe:

```text
projects.create
```

muestra:

```text
+ New Project
```

Cuando se ejecuta la operación:

```text
Create Project
```

el backend vuelve a comprobar:

```text
authorize(
    user,
    "projects",
    "create"
)
```

Si el permiso existe:

```text
200 OK
```

Si no existe:

```text
403 Forbidden
```

---

# 32. Casos de demostración para el portafolio

El proyecto debería incluir escenarios preparados para demostrar el RBAC.

## Caso 1 - Admin

```text
Admin
├── Users
├── Roles
├── Permissions
├── Modules
├── Actions
├── Projects
├── Tasks
└── Reports
```

---

## Caso 2 - Project Manager

```text
Project Manager
├── Projects
│   ├── Create
│   ├── Read
│   ├── Update
│   └── Archive
│
├── Tasks
│   ├── Create
│   ├── Update
│   ├── Assign
│   └── Complete
│
└── Reports
    ├── Read
    └── Export
```

No puede:

```text
Manage Roles
Manage Permissions
Manage Modules
```

---

## Caso 3 - Developer

Puede:

```text
Read Projects
Read Tasks
Create Tasks
Update Tasks
Complete Tasks
```

Pero no:

```text
Delete Projects
Manage Users
Manage Roles
Export Reports
```

---

## Caso 4 - Client

Puede:

```text
Read Project
Read Tasks
Read Reports
```

Pero no:

```text
Create Task
Update Task
Delete Task
Manage Members
```

---

# 33. Demo avanzada

Una demostración especialmente interesante sería:

```text
Joel

Project A
└── Project Manager

Project B
└── Developer

Project C
└── Viewer
```

La aplicación debe mostrar diferentes capacidades dependiendo del proyecto.

Por ejemplo:

```text
Project A
[+ Task]
[Assign]
[Edit]
[Archive]

Project B
[+ Task]
[Edit]

Project C
[View]
```

El usuario es el mismo.

La diferencia está en el contexto de autorización.

---

# 34. Testing

El sistema debe incluir pruebas de autorización.

Ejemplos:

```text
✓ Admin can delete users
✓ Project Manager can create projects
✓ Developer cannot delete projects
✓ Client cannot modify tasks
✓ Viewer cannot create tasks
✓ Project Manager can assign tasks
✓ Developer cannot modify another project's tasks
✓ User cannot access a project without membership
```

También se deben probar casos negativos:

```text
401 Unauthorized
403 Forbidden
404 Not Found
```

---

# 35. Objetivo para el portafolio

El proyecto debe presentarse como una demostración de:

```text
Backend Architecture
        +
Authentication
        +
Authorization
        +
RBAC
        +
Resource-Level Authorization
        +
GraphQL
        +
PostgreSQL
        +
Frontend Authorization
        +
Audit Logging
```

El objetivo no es simplemente demostrar que se pueden crear:

```text
Users
Roles
Permissions
```

sino demostrar que se puede diseñar y utilizar un **sistema de autorización extensible**.

---

# 36. Nombre conceptual

Un posible nombre para el proyecto:

```text
SecureFlow
```

o:

```text
AccessFlow
```

o:

```text
ProjectGuard
```

o simplemente:

```text
RBAC Project Platform
```

La aplicación puede presentarse como:

> **A project management platform powered by a custom, fine-grained authorization engine.**

---

# 37. Roadmap

```text
[✓] Users
[✓] Roles
[✓] Modules
[✓] Actions
[✓] Permissions
[✓] Role Permissions
[✓] Login
[ ] Permission middleware
[ ] Dynamic frontend authorization
[ ] Projects
[ ] Tasks
[ ] Teams
[ ] Project members
[ ] Project roles
[ ] Resource authorization
[ ] Audit logs
[ ] Contextual policies
[ ] Automated authorization tests
```

---

# 38. Long-term vision

El RBAC no debe quedar acoplado exclusivamente a la aplicación de proyectos.

La visión a largo plazo es convertirlo en un componente reutilizable:

```text
                 Authorization Platform
                         │
          ┌──────────────┼──────────────┐
          │              │              │
          ▼              ▼              ▼
      Projects         CRM          Inventory
          │              │              │
          └──────────────┼──────────────┘
                         │
                  Authorization
                      Engine
```

De esta forma, el proyecto puede convertirse en una plataforma de autorización que posteriormente pueda utilizarse en diferentes aplicaciones.

---

# 39. Resultado esperado

Al finalizar el MVP, el proyecto debe permitir demostrar el siguiente flujo:

```text
User Login
    │
    ▼
Authentication
    │
    ▼
Load Global Role
    │
    ▼
Load Permissions
    │
    ▼
Build Frontend Capabilities
    │
    ▼
User accesses Project
    │
    ▼
Resolve Project Role
    │
    ▼
Resolve Resource Permissions
    │
    ▼
Evaluate Authorization Policy
    │
    ├──── ALLOW ────► Execute operation
    │
    └──── DENY ─────► 403 Forbidden
                         │
                         ▼
                    Audit Log
```

El resultado final será una aplicación de gestión de proyectos cuyo principal diferenciador técnico sea un **sistema de autorización propio, desacoplado, extensible y capaz de manejar tanto RBAC global como autorización contextual por recurso**.
