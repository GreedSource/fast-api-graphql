# Etapa 2 - Catalogo RBAC para Project Management

## Objetivo

Extender el catalogo actual de modulos, acciones y permisos para soportar la aplicacion MVP de gestion de proyectos.

## Alcance funcional

Agregar modulos:

- `dashboard`
- `projects`
- `tasks`
- `teams`
- `members`
- `milestones`
- `reports`
- `documents`
- `activity`

Agregar acciones base y especificas:

- `create`
- `read`
- `update`
- `delete`
- `archive`
- `assign`
- `complete`
- `export`
- `manage`
- `restore`

Actualizar roles iniciales:

- `super_admin`
- `project_manager`
- `developer`
- `client`
- `viewer`

## Cambios esperados

- migracion si el catalogo requiere columnas, indices o restricciones nuevas
- seeders de `modules`, `actions`, `permissions`, `roles` y `role_permissions`
- servicios/repositorios si se requiere idempotencia adicional
- tests de seeders o funciones puras de construccion de matrices de permisos si se extraen helpers

## Decisiones de diseno

- Mantener `permissions` como combinacion unica de `module_id + action_id`.
- Mantener permisos resueltos para backend como `{type, action}`.
- Si se expone `module.action`, hacerlo como campo derivado, no como fuente de verdad.
- No usar comodines persistidos como `projects.*` en esta etapa; expandirlos a permisos concretos.

## Pruebas obligatorias

- El seeder de modulos debe ser idempotente.
- El seeder de acciones debe ser idempotente.
- El seeder de permisos debe crear la matriz esperada sin duplicados.
- Cada rol inicial debe recibir exactamente los permisos definidos por el documento base.
- Casos negativos: modulo/accion faltante no debe producir permisos corruptos.

Si se crea o modifica cualquier servicio, repositorio, util, helper, decorador, DTO o resolver, el mismo cambio debe incluir su prueba unitaria correspondiente.

## Verificacion

```bash
ruff check .
python -m pytest
python manage.py status
```

Validar tambien:

```bash
python manage.py seed-all
```

## Criterio de salida

- Catalogo RBAC del MVP disponible.
- Roles iniciales listos para demo.
- Seeders repetibles sin duplicar datos.
