# Etapa 1 - Base de Calidad y Contratos RBAC

## Objetivo

Dejar el sistema actual listo para crecer sin romper contratos existentes de autenticacion, permisos y GraphQL.

Esta etapa no debe agregar dominios grandes. Su proposito es ordenar contratos, pruebas y convenciones para que las siguientes etapas sean incrementales.

## Alcance

- Confirmar contrato actual de permisos expuestos como `{type, action}`.
- Confirmar representacion alternativa `module.action` para frontend sin romper compatibilidad.
- Documentar y probar decoradores `@require_token`, `@require_permission` y `@require_permissions`.
- Revisar que DTOs serialicen UUIDs de forma consistente.
- Mantener fixtures/factories de tests reutilizables.
- Agregar helpers de test para construir `current_user` con permisos.

## Cambios esperados

- `tests/factories.py`
- `tests/conftest.py`
- tests de DTOs, utils, helpers, decorators y servicios existentes
- documentacion corta de contratos si se detectan inconsistencias

## Fuera de alcance

- Crear tablas nuevas.
- Crear dominios `projects` o `tasks`.
- Cambiar el formato del login de forma incompatible.
- Implementar authorization engine.

## Pruebas obligatorias

Agregar o mantener pruebas para:

- login exitoso y credenciales invalidas
- refresh token con usuario inexistente
- token ausente, token invalido y usuario inexistente
- permisos individuales y multiples en modo `ANY`/`ALL`
- DTOs con UUID valido/invalido
- formatter de errores GraphQL

Si se crea o modifica cualquier servicio, repositorio, util, helper, decorador, DTO o resolver, el mismo cambio debe incluir su prueba unitaria correspondiente.

## Verificacion

```bash
ruff check .
python -m pytest
```

## Criterio de salida

- Suite unitaria verde.
- Contrato RBAC actual documentado y cubierto.
- Base de tests lista para reutilizar en etapas posteriores.
