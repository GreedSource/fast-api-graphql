# API REST y GraphQL compartida

La aplicación expone dos transportes sobre los mismos servicios, repositorios, DTOs y motor de autorización:

- GraphQL: `/graphql`
- REST versionado: `/api/v1`
- OpenAPI/Swagger: `/docs`
- ReDoc: `/redoc`

REST cubre autenticación, usuarios, roles, módulos, acciones, permisos, proyectos, miembros, tareas, auditoría y los
dominios CRM. Las operaciones comerciales especiales se representan como acciones REST, por ejemplo
`POST /api/v1/leads/{id}/convert` y `POST /api/v1/opportunities/{id}/close`.

La autenticación acepta `Authorization: Bearer <token>` o la cookie de acceso configurada. Las dependencias FastAPI
validan RBAC y los endpoints delegan en `AuthorizationService` para scopes de proyecto o CRM. GraphQL conserva sus
decoradores como adaptador independiente; ninguno de los transportes llama al otro.

Las respuestas REST tienen el contrato:

```json
{
  "status": 200,
  "message": "Projects fetched",
  "data": []
}
```
