# Contrato de Permisos RBAC - Etapa 1

## Objetivo

Formalizar el contrato actual de permisos antes de implementar nuevos dominios de proyectos, tareas y autorizacion contextual.

## Contrato backend actual

El backend sigue resolviendo permisos como objetos:

```json
{
  "type": "users",
  "action": "read"
}
```

Este formato se mantiene para no romper resolvers, decoradores ni respuestas GraphQL existentes.

## Representacion frontend-friendly

Para navegacion, menus y controles de interfaz, un permiso tambien puede representarse como:

```text
users.read
```

Esta representacion es derivada. La fuente de verdad sigue siendo la combinacion:

```text
module + action
```

## Reglas

- Los permisos se normalizan a lowercase.
- Espacios alrededor de `type`, `action` o `module.action` se eliminan.
- Entradas invalidas se ignoran en helpers de conversion por lote.
- El frontend puede usar `module.action` para UX, pero el backend siempre revalida seguridad.

## Utilidad central

La conversion y evaluacion vive en:

```text
server/utils/permission_utils.py
```

Funciones principales:

- `normalize_permission(...)`
- `permission_to_key(...)`
- `permissions_to_keys(...)`
- `permission_set(...)`
- `has_permission(...)`

## Criterio de compatibilidad

Los decoradores de permisos aceptan tanto:

```python
{"type": "users", "action": "read"}
```

como:

```python
"users.read"
```

Esto permite preparar la evolucion a `module.action` sin cambiar el contrato GraphQL actual.
