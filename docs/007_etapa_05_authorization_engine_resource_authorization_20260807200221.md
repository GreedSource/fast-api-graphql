# Etapa 5 - Authorization Engine y Resource Authorization

## Objetivo

Centralizar la autorizacion en un motor reutilizable que evalue permisos globales, membresia, rol de proyecto, propiedad del recurso y politicas contextuales.

## API propuesta

```python
authorize(
    user=current_user,
    module="tasks",
    action="update",
    resource=task,
    context={"project_id": task.project_id},
)
```

Resultado sugerido:

```python
AuthorizationResult(
    allowed=True,
    reason="allowed_by_project_role",
)
```

## Alcance funcional

- Crear servicio o util central de autorizacion.
- Resolver permisos globales del usuario.
- Resolver membresia y rol por proyecto cuando exista `project_id`.
- Evaluar ownership de recursos como tareas asignadas.
- Reemplazar checks dispersos en servicios/resolvers nuevos.
- Preparar un decorador/context helper para resolvers GraphQL.

## Reglas iniciales

- Usuario no autenticado: `401`.
- Usuario autenticado sin permiso global/contextual: `403`.
- `super_admin` no debe depender del nombre del rol; debe tener permisos concretos.
- `tasks.update` puede requerir:
  - permiso `tasks.update`
  - membresia en el proyecto
  - ownership o permiso contextual de manager
- `projects.delete/archive` debe validar permiso y alcance.

## Cambios esperados

- `server/services/authorization_service.py` o `server/utils/authorization_utils.py`
- DTOs internos para resultado de autorizacion si ayudan
- decorador/context helper nuevo si se decide
- ajustes en resolvers/services de projects/tasks
- tests extensivos de matriz de permisos

## Pruebas obligatorias

- Admin con permiso concreto puede ejecutar accion.
- Project Manager puede modificar recursos dentro de su proyecto.
- Developer puede modificar sus tareas asignadas.
- Developer no puede modificar tareas de otro proyecto.
- Client/Viewer no pueden modificar tareas.
- Usuario sin membresia no puede acceder al proyecto.
- Recurso inexistente debe seguir siendo `404`, no convertirse en `403` por accidente.
- Intento no autenticado debe ser `401`.

Si se crea o modifica cualquier servicio, repositorio, util, helper, decorador, DTO o resolver, el mismo cambio debe incluir su prueba unitaria correspondiente.

## Verificacion

```bash
ruff check .
python -m pytest
```

Validar manualmente:

- operaciones GraphQL con usuarios de demo distintos
- escenarios de permiso permitido y denegado

## Criterio de salida

- La autorizacion sensible vive en un componente central.
- Projects/tasks usan resource authorization.
- La matriz critica de permisos esta cubierta por tests unitarios.
