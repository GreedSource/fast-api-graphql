# Plan de Integracion - RBAC Authorization Platform

## Fuente

Documento base: `docs/RBAC Authorization Platform.md`

## Objetivo

Implementar la evolucion del backend actual hacia una plataforma de gestion de proyectos con autorizacion RBAC global, autorizacion por recurso, auditoria y politicas contextuales.

Este plan divide el trabajo en etapas pequenas para que cada etapa pueda completarse, probarse y validarse aunque una sesion no tenga presupuesto suficiente para implementar todo el sistema.

## Regla obligatoria de pruebas

Cada vez que se cree o modifique un archivo con comportamiento ejecutable, se deben agregar o actualizar pruebas unitarias en el mismo cambio.

Aplica como minimo a:

- `server/services/`
- `server/repositories/`
- `server/utils/`
- `server/helpers/`
- `server/decorators/`
- `server/models/dto/`
- `server/schema/*/resolver.py`
- `server/core/`
- `server/middlewares/`
- cualquier archivo nuevo con logica de negocio, validacion, autorizacion, serializacion o efectos laterales

No basta con agregar la implementacion. La etapa no se considera terminada si no incluye pruebas para:

- caso exitoso principal
- al menos un caso negativo relevante
- errores de autorizacion `401` / `403` cuando aplique
- validacion de DTOs cuando cambie el contrato de entrada/salida
- rutas sin I/O real mockeadas cuando el componente dependa de PostgreSQL, Redis, SMTP o servicios externos

## Verificacion minima por etapa

Antes de cerrar cualquier etapa:

```bash
ruff check .
python -m pytest
```

Si la etapa toca persistencia:

```bash
python manage.py status
```

Si la etapa toca GraphQL o app runtime, validar manualmente:

- `GET /ping`
- `GET /graphql`
- operacion GraphQL afectada

## Orden de integracion

1. Etapa 1 - Base de calidad, contratos y convenciones.
2. Etapa 2 - Catalogo RBAC para project management.
3. Etapa 3 - Dominio MVP de projects y tasks.
4. Etapa 4 - Project members y project roles.
5. Etapa 5 - Authorization Engine y resource authorization.
6. Etapa 6 - Audit logs, politicas contextuales y demo.

## Principios de implementacion

- Backend es la fuente de verdad para seguridad.
- Frontend solo consume permisos para UX y visibilidad.
- La autorizacion debe estar centralizada.
- Evitar checks por nombre de rol como `if role == "admin"`.
- Mantener permisos con representacion uniforme `module.action`.
- No introducir capas nuevas si el patron actual `schema -> services -> repositories` resuelve el caso.
- Cada migracion debe tener su seeder o ajuste de seeders si agrega datos base.

## Criterio global de finalizacion

El sistema debe permitir demostrar:

- login con permisos resueltos
- administracion de usuarios, roles, modulos, acciones y permisos
- proyectos y tareas protegidos por permisos
- membresia por proyecto
- rol distinto por proyecto para el mismo usuario
- evaluacion centralizada con `authorize(...)`
- denegacion backend con `403 Forbidden`
- auditoria de acciones permitidas y rechazadas
