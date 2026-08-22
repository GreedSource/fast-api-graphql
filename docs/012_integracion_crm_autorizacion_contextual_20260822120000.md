# Integración CRM con autorización contextual compartida

## Resultado

El CRM convive en la misma API con usuarios, RBAC, proyectos, tareas y auditoría. No introduce un segundo sistema de
autorización. Los módulos comerciales registran permisos en el catálogo existente y consumen `AuthorizationService`.

## Límites de dominio

Cada recurso (`companies`, `contacts`, `leads`, `opportunities`, `activities`) tiene modelo ORM, DTO, repositorio,
servicio, SDL GraphQL y resolver independientes. `BaseRepository`, `ScopedResourceRepository`, `BaseService`,
los mixins ORM y el resolver base contienen únicamente comportamiento transversal. La conversión pertenece a
`LeadService` y el
cierre comercial pertenece a `OpportunityService`.

`BaseRepository` no pertenece al CRM: puede ser heredado por cualquier repositorio cuya entidad tenga una llave
primaria UUID llamada `id`. Las extensiones de contexto, como `ScopedResourceRepository`, se mantienen separadas para
no obligar a usuarios, roles, proyectos u otros dominios a conocer campos de organización o equipo.

`BaseService` tampoco pertenece al CRM. Proyectos y tareas lo utilizan para serialización y casos CRUD, mientras
mantienen `archive`, validación de proyecto, asignación y `complete` en sus servicios concretos.

## Contexto de autorización

Los recursos contienen `organization_id`, `team_id` y `owner_id`. La membresía comercial define uno de los scopes:
`OWN`, `TEAM`, `ORGANIZATION` o `GLOBAL`. El motor primero valida el permiso RBAC y después aplica el scope al recurso.
Las consultas de colección filtran en PostgreSQL según el scope, evitando cargar filas no autorizadas.

## Persistencia y puesta en marcha

La migración `v011_create_crm_platform_postgresql_20260822120000` crea organizaciones, equipos, membresías y recursos
comerciales. Después de migrar deben ejecutarse los seeders de módulos, acciones, permisos y roles para incorporar los
roles `sales_director`, `sales_manager`, `sales_representative` y `sales_assistant`.

```bash
python manage.py migrate
python manage.py seed-modules
python manage.py seed-actions
python manage.py seed-permissions
python manage.py seed-roles
```
