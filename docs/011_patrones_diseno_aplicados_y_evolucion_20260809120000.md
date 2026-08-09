# Patrones de diseño aplicados y guía de evolución

## Objetivo

Documentar los patrones que ya resuelven necesidades concretas del backend y definir puntos de extensión para evitar
introducir abstracciones antes de que exista un caso de uso real.

## Mapa actual

| Patrón | Implementación | Uso |
|---|---|---|
| Singleton | `server/decorators/singleton_decorator.py` | Mantiene una instancia por proceso de helpers, repositorios y servicios sin estado por request. |
| Strategy | `server/strategies/permission_check_strategy.py` | Encapsula las políticas `ANY` y `ALL` de permisos. |
| Factory | `PermissionCheckStrategyFactory` | Selecciona la estrategia desde `PermissionCheckMode` y centraliza modos soportados. |
| Observer | `server/observers/` | Desacopla `UserService` de la notificación Redis al actualizar un usuario. |
| Adapter | `server/adapters/websocket_request_adapter.py` | Presenta headers y cookies de WebSocket con el contrato que consume autenticación. |
| Decorator | `server/decorators/require_*` | Aplica autenticación y permisos a resolvers sin mezclar esas reglas con el resolver. |

## Criterios y límites

### Singleton

Se conserva la implementación existente. Es apropiada para objetos compartidos dentro de un único proceso, pero no
coordina estado entre workers. No debe usarse para almacenar datos de una request ni reemplazar Redis/PostgreSQL.

Evolución recomendada: si las dependencias necesitan configuración distinta por test o por tenant, migrar su creación a
factories/dependency injection y limitar Singleton a clientes de infraestructura cuya vida útil sea la del proceso.

### Strategy y Factory

Agregar una estrategia cuando aparezca una política de combinación nueva (por ejemplo, umbral mínimo o permisos
condicionados por contexto). La clase nueva debe implementar `PermissionCheckStrategy` y registrarse en
`PermissionCheckStrategyFactory._strategies`; el decorador no necesita cambiar.

### Observer

Actualmente el evento `UserUpdatedEvent` tiene un observer Redis. Se pueden adjuntar observers de auditoría, métricas o
webhooks sin modificar `UserService`. Los observers se ejecutan secuencialmente y propagan errores, manteniendo el
comportamiento previo de publicación. Si aparecen observers lentos o no críticos, conviene definir una política explícita
de errores y delegarlos a una cola; no se debe ocultar el fallo accidentalmente.

### Adapter

El adapter actual resuelve la diferencia entre request HTTP y contexto WebSocket. Si se incorpora otro transporte, crear
un adapter que exponga al menos `headers` y `cookies`, en vez de agregar condicionales de transporte a los decoradores.

Para correo, almacenamiento externo o proveedores OAuth futuros, introducir adapters solo cuando exista más de un
proveedor o sea necesario aislar un SDK externo. El contrato debe vivir en la capa de aplicación y la implementación del
proveedor en `server/adapters/`.

### Decorator

Los decorators deben limitarse a concerns transversales: autenticación, autorización, trazabilidad o rate limiting. La
lógica de negocio y el acceso a datos permanecen en servicios/repositorios. Al agregar uno, preservar metadatos con
`functools.wraps` y cubrir explícitamente los casos exitoso, 401 y 403 cuando correspondan.

## Integraciones futuras sugeridas

1. Factory de proveedores de correo cuando se soporte SMTP y al menos un proveedor API.
2. Strategy para políticas de reintento solo si aparecen operaciones externas con requisitos diferentes.
3. Observers de auditoría o métricas para eventos de proyectos y tareas, con una política de errores definida.
4. Adapter de identidad para OAuth/OIDC si se añade un proveedor externo.

No se recomienda crear estas clases antes de incorporar esos casos de uso: aumentarían el número de capas sin reducir
acoplamiento real.
