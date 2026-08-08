# Etapa 4 - Project Members y Project Roles

## Objetivo

Permitir que un usuario tenga roles distintos segun el proyecto.

Ejemplo:

```text
Joel
├── Project A -> Project Manager
├── Project B -> Developer
└── Project C -> Viewer
```

## Alcance funcional

- Agregar miembros a un proyecto.
- Remover miembros de un proyecto.
- Cambiar rol de un miembro dentro de un proyecto.
- Consultar miembros de un proyecto.
- Consultar proyectos de un usuario con rol contextual.

## Modelo sugerido

`project_members`:

- `id`
- `project_id`
- `user_id`
- `project_role_id`
- `created_at`
- `updated_at`

`project_roles`:

- `id`
- `name`
- `description`
- `active`
- `created_at`
- `updated_at`

`project_role_permissions`:

- `project_role_id`
- `permission_id`

## Cambios esperados

- modelos ORM y DTOs de project members/project roles
- repositorios y servicios especificos
- migraciones versionadas
- seeders para roles de proyecto: `project_manager`, `developer`, `client`, `viewer`
- GraphQL schema/resolvers para membresias

## Decisiones de diseno

- No reutilizar directamente `users.role_id` para rol contextual.
- Un usuario puede tener un rol global y muchos roles por proyecto.
- Los project roles pueden reutilizar `permissions`.
- Evitar checks hardcoded por nombre de rol.

## Pruebas obligatorias

- Crear membresia con usuario/proyecto/rol validos.
- Rechazar membresia duplicada.
- Rechazar usuario, proyecto o rol inexistente.
- Cambiar rol de proyecto.
- Listar miembros con rol contextual.
- Verificar que los seeders de project roles sean idempotentes.

Si se crea o modifica cualquier servicio, repositorio, util, helper, decorador, DTO o resolver, el mismo cambio debe incluir su prueba unitaria correspondiente.

## Verificacion

```bash
ruff check .
python -m pytest
python manage.py status
```

Validar manualmente:

- operaciones GraphQL de membresias
- permisos requeridos para administrar miembros

## Criterio de salida

- El mismo usuario puede tener roles distintos en proyectos distintos.
- El sistema puede resolver permisos contextuales basados en membresia.
- La siguiente etapa puede construir `Authorization Engine` sobre estos datos.
