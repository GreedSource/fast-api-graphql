from ariadne import MutationType, QueryType
from graphql import GraphQLResolveInfo

from server.decorators.require_token_decorator import require_token
from server.helpers.logger_helper import LoggerHelper
from server.models.response_model import ResponseModel
from server.models.role_model import (
    CreateRoleModel,
    RoleItemModel,
    UpdateRoleModel,
)
from server.services.role_service import RoleService


class RoleResolver:
    def __init__(self):
        self.query = QueryType()
        self.mutation = MutationType()

        self.__service = RoleService()

        self._bind_queries()
        self._bind_mutations()

        LoggerHelper.info("RoleResolver initialized")

    # -----------------
    # Bindings
    # -----------------

    def _bind_queries(self):
        self.query.set_field("roles", self.resolve_roles)
        self.query.set_field("role", self.resolve_role)

    def _bind_mutations(self):
        self.mutation.set_field("createRole", self.resolve_create)
        self.mutation.set_field("updateRole", self.resolve_update)
        self.mutation.set_field("deleteRole", self.resolve_delete)
        self.mutation.set_field("addPermissionsToRole", self.resolve_add_permissions)
        self.mutation.set_field("removePermissionsFromRole", self.resolve_remove_permissions)

    # -----------------
    # Mutations
    # -----------------

    @require_token
    async def resolve_create(self, _, info: GraphQLResolveInfo, input):
        model = CreateRoleModel(**input)
        response = await self.__service.create(model)

        return ResponseModel[RoleItemModel](
            status=200,
            message="Role created successfully",
            data=response,
        )

    @require_token
    async def resolve_update(self, _, info: GraphQLResolveInfo, input):
        model = UpdateRoleModel(**input)
        response = await self.__service.update(model)
        return ResponseModel[RoleItemModel](
            status=200,
            message="Role updated successfully",
            data=response,
        )

    @require_token
    async def resolve_delete(self, _, info: GraphQLResolveInfo, id: str):
        result = await self.__service.delete_role(id)

        return ResponseModel[bool](
            status=200,
            message="Role deleted successfully" if result else "Role not found",
            data=result,
        )

    @require_token
    async def resolve_add_permissions(self, _, __, roleId: str, permissionIds: list[str]):
        await self.__service.add_permissions(roleId, permissionIds)
        return ResponseModel[bool](
            status=200,
            message="Permissions added to role successfully",
            data=True,
        )

    @require_token
    async def resolve_remove_permissions(self, _, __, roleId: str, permissionIds: list[str]):
        await self.__service.remove_permissions(roleId, permissionIds)
        return ResponseModel[bool](
            status=200,
            message="Permissions removed from role successfully",
            data=True,
        )

    # -----------------
    # Queries
    # -----------------

    @require_token
    async def resolve_roles(self, *_):
        roles = await self.__service.get_roles()

        return ResponseModel[list[RoleItemModel]](
            status=200,
            message="Roles fetched successfully",
            data=roles,
        )

    @require_token
    async def resolve_role(self, _, __, id: str):
        role = await self.__service.get_role(id)

        return ResponseModel[RoleItemModel](
            status=200,
            message="Role fetched successfully" if role else "Role not found",
            data=role,
        )

    # -----------------
    # Export
    # -----------------

    def get_resolvers(self):
        return [self.query, self.mutation]
