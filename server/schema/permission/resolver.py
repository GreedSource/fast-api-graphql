from typing import Any, Dict

from ariadne import MutationType, QueryType
from graphql import GraphQLResolveInfo

from server.decorators.require_permission_decorator import require_permission
from server.decorators.require_token_decorator import require_token
from server.models.permission_model import CreatePermissionModel, PermissionItemModel
from server.models.response_model import ResponseModel
from server.services.permission_service import PermissionService


class PermissionResolver:
    def __init__(self) -> None:
        self.query = QueryType()
        self.mutation = MutationType()
        self.__service = PermissionService()

        self._bind_queries()
        self._bind_mutations()

    def _bind_queries(self) -> None:
        self.query.set_field("permissions", self.resolve_permissions)

    def _bind_mutations(self) -> None:
        self.mutation.set_field("createPermission", self.resolve_create)
        self.mutation.set_field("deletePermission", self.resolve_delete)

    @require_token
    @require_permission(type="permissions", action="read")
    async def resolve_permissions(self, _: object, info: GraphQLResolveInfo) -> ResponseModel[Dict[str, Any]]:
        data = await self.__service.get_all()
        return ResponseModel(
            status=200,
            message="Permissions retrieved",
            data=data,
        )

    @require_token
    @require_permission(type="permissions", action="create")
    async def resolve_create(
        self, _: object, info: GraphQLResolveInfo, input: Dict[str, Any]
    ) -> ResponseModel[PermissionItemModel]:
        model = CreatePermissionModel(**input)
        data = await self.__service.create(model)
        return ResponseModel(
            status=200,
            message="Permission created",
            data=data,
        )

    @require_token
    @require_permission(type="permissions", action="delete")
    async def resolve_delete(self, _: object, info: GraphQLResolveInfo, id: str) -> ResponseModel[bool]:
        result = await self.__service.delete(id)
        return ResponseModel(
            status=200,
            message="Permission deleted" if result else "Permission not found",
            data=result,
        )

    def get_resolvers(self) -> list[QueryType | MutationType]:
        return [self.query, self.mutation]
