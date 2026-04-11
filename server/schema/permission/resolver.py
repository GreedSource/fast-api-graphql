from ariadne import MutationType, QueryType

from server.decorators.require_permission_decorator import require_permission
from server.decorators.require_token_decorator import require_token
from server.models.permission_model import CreatePermissionModel
from server.models.response_model import ResponseModel
from server.services.permission_service import PermissionService


class PermissionResolver:
    def __init__(self):
        self.query = QueryType()
        self.mutation = MutationType()
        self.__service = PermissionService()

        self._bind_queries()
        self._bind_mutations()

    def _bind_queries(self):
        self.query.set_field("permissions", self.resolve_permissions)

    def _bind_mutations(self):
        self.mutation.set_field("createPermission", self.resolve_create)
        self.mutation.set_field("deletePermission", self.resolve_delete)

    @require_token
    @require_permission(type="permissions", action="read")
    async def resolve_permissions(self, *_):
        data = await self.__service.get_all()
        return ResponseModel(
            status=200,
            message="Permissions retrieved",
            data=data,
        )

    @require_token
    @require_permission(type="permissions", action="create")
    async def resolve_create(self, _, __, input):
        model = CreatePermissionModel(**input)
        data = await self.__service.create(model)
        return ResponseModel(
            status=200,
            message="Permission created",
            data=data,
        )

    @require_token
    @require_permission(type="permissions", action="delete")
    async def resolve_delete(self, _, __, id):
        return await self.__service.delete(id)

    def get_resolvers(self):
        return [self.query, self.mutation]
