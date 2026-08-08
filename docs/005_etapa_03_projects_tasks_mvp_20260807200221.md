# Etapa 3 - Dominio MVP de Projects y Tasks

## Objetivo

Implementar los dominios principales del MVP: proyectos y tareas, protegidos por permisos RBAC globales.

## Alcance funcional

Projects:

- crear proyecto
- listar proyectos
- ver proyecto
- actualizar proyecto
- archivar proyecto
- eliminar proyecto si se decide mantener delete fisico

Tasks:

- crear tarea
- listar tareas
- ver tarea
- actualizar tarea
- asignar tarea
- cambiar estado
- completar tarea

## Modelo sugerido

`projects`:

- `id`
- `name`
- `description`
- `status`
- `owner_id`
- `archived_at`
- `created_at`
- `updated_at`

`tasks`:

- `id`
- `project_id`
- `title`
- `description`
- `status`
- `priority`
- `assignee_id`
- `created_by_id`
- `due_date`
- `completed_at`
- `created_at`
- `updated_at`

## Cambios esperados

- `server/models/orm/project_orm.py`
- `server/models/orm/task_orm.py`
- `server/models/dto/project_dto.py`
- `server/models/dto/task_dto.py`
- `server/repositories/project_repository.py`
- `server/repositories/task_repository.py`
- `server/services/project_service.py`
- `server/services/task_service.py`
- `server/schema/projects/`
- `server/schema/tasks/`
- migraciones versionadas
- seeders opcionales para datos demo

## Autorizacion

Usar los decoradores actuales en resolvers:

- `projects.create`
- `projects.read`
- `projects.update`
- `projects.delete`
- `projects.archive`
- `tasks.create`
- `tasks.read`
- `tasks.update`
- `tasks.delete`
- `tasks.assign`
- `tasks.complete`

En esta etapa solo se exige permiso global. La autorizacion contextual por proyecto queda para etapas posteriores.

## Pruebas obligatorias

- DTOs: validacion de entrada y serializacion de salida.
- Repositories: construccion de entidades, UUID invalido, update parcial, delete/archive.
- Services: casos exitosos y recursos no encontrados.
- Resolvers: delegan al servicio correcto y aplican decoradores esperados.
- Autorizacion: usuario sin permiso recibe `403`.

Si se crea o modifica cualquier servicio, repositorio, util, helper, decorador, DTO o resolver, el mismo cambio debe incluir su prueba unitaria correspondiente.

## Verificacion

```bash
ruff check .
python -m pytest
python manage.py status
```

Validar manualmente:

- `GET /ping`
- `GET /graphql`
- queries/mutations de projects
- queries/mutations de tasks

## Criterio de salida

- Projects y tasks operan via GraphQL.
- Permisos RBAC globales bloquean operaciones no autorizadas.
- Suite unitaria cubre flujo feliz y negativos principales.
