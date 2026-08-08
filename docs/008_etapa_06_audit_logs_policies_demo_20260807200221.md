# Etapa 6 - Audit Logs, Politicas Contextuales y Demo

## Objetivo

Completar el MVP avanzado con trazabilidad de acciones relevantes, politicas contextuales reutilizables y datos de demostracion para portafolio.

## Alcance funcional

Audit logs:

- registrar acciones exitosas
- registrar intentos denegados
- guardar usuario, modulo, accion, recurso, estado, metadata y timestamp

Politicas:

- ownership de tareas
- rol contextual por proyecto
- permisos de lectura para clientes/viewers
- restricciones para acciones destructivas

Demo:

- usuarios de ejemplo
- proyectos de ejemplo
- tareas asignadas
- roles globales y roles por proyecto
- escenarios permitidos y denegados

## Modelo sugerido

`audit_logs`:

- `id`
- `user_id`
- `module`
- `action`
- `resource_type`
- `resource_id`
- `status`
- `metadata`
- `created_at`

## Cambios esperados

- `server/models/orm/audit_log_orm.py`
- `server/models/dto/audit_log_dto.py`
- `server/repositories/audit_log_repository.py`
- `server/services/audit_log_service.py`
- integracion con Authorization Engine
- schema/resolvers para consultar auditoria con permisos administrativos
- seeders de demo

## Decisiones de diseno

- Registrar denegaciones sin filtrar informacion sensible.
- No bloquear operaciones principales si el audit log falla, salvo que se decida modo estricto.
- Metadata debe ser JSON serializable.
- Consultar audit logs debe requerir permiso explicito, por ejemplo `activity.read` o `audit.read` si se agrega modulo dedicado.

## Pruebas obligatorias

- Registrar accion exitosa.
- Registrar accion denegada.
- Metadata se serializa correctamente.
- Fallo controlado del audit logger no rompe flujos no estrictos.
- Solo usuarios autorizados pueden consultar auditoria.
- Politicas contextuales cubren casos del documento base:
  - Project Manager puede asignar tareas.
  - Developer no modifica tareas de otro proyecto.
  - Client no modifica tareas.
  - Viewer no crea tareas.

Si se crea o modifica cualquier servicio, repositorio, util, helper, decorador, DTO o resolver, el mismo cambio debe incluir su prueba unitaria correspondiente.

## Verificacion

```bash
ruff check .
python -m pytest
python manage.py status
```

Validar manualmente:

- flujo completo de login
- acceso permitido
- acceso denegado
- registro de auditoria para ambos casos

## Criterio de salida

- El sistema demuestra RBAC global, autorizacion por recurso y auditoria.
- Existen datos de demo para mostrar roles distintos por proyecto.
- Los escenarios del portafolio son reproducibles.
