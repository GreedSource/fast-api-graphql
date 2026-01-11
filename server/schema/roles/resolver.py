# server/resolvers/auth_resolver.py
from ariadne import QueryType, MutationType

from server.decorators.require_token_decorator import require_token
from server.helpers.logger_helper import LoggerHelper
from server.models.response_model import ResponseModel
from server.models.role_model import CreateRoleModel, RoleItemModel, UpdateRoleModel
from server.services.role_service import RoleService


class RoleResolver:
    def __init__(self):
        self.query = QueryType()
        self.mutation = MutationType()

        self.__service = RoleService()

        self._bind_queries()
        self._bind_mutations()

        LoggerHelper.info("AuthResolver initialized")

    # -----------------
    # Bindings
    # -----------------

    def _bind_queries(self):
        # self.query.set_field("profile", self.resolve_profile)
        pass

    def _bind_mutations(self):
        self.mutation.set_field("createRole", self.resolve_create)
        self.mutation.set_field("updateRole", self.resolve_update)

    # -----------------
    # Mutations
    # -----------------

    async def resolve_create(self, _, info, input):
        model = CreateRoleModel(**input)
        response = await self.__service.create(model)
        return ResponseModel[RoleItemModel](
            status=200,
            message="Role created successfully",
            data=response,
        )

    async def resolve_update(self, _, info, input):
        model = UpdateRoleModel(**input)
        response = await self.__service.update(model)
        return ResponseModel[RoleItemModel](
            status=200,
            message="Role updated successfully",
            data=response,
        )

    # -----------------
    # Queries
    # -----------------

    def get_resolvers(self):
        return [self.query, self.mutation]
