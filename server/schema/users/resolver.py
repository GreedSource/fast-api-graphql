# server/resolvers/user_resolver.py
from ariadne import QueryType, MutationType

from server.decorators.singleton_decorator import singleton
from server.decorators.require_token_decorator import require_token
from server.helpers.logger_helper import LoggerHelper
from server.models.user_model import UpdateUserModel

from server.services.user_service import UserService


@singleton
class UserResolver:
    def __init__(self):
        self.query = QueryType()
        self.mutation = MutationType()

        self.user_service = UserService()

        self._bind_queries()
        self._bind_mutations()

        LoggerHelper.info("UserResolver initialized")

    # -----------------
    # Bindings
    # -----------------

    def _bind_queries(self):
        self.query.set_field("users", self.resolve_users)
        self.query.set_field("user", self.resolve_user)

    def _bind_mutations(self):
        self.mutation.set_field("updateUser", self.resolve_update_user)
        self.mutation.set_field("deleteUser", self.resolve_delete_user)

    # -----------------
    # Queries
    # -----------------

    @require_token
    async def resolve_users(self, _, info):
        return await self.user_service.get_users()

    @require_token
    async def resolve_user(self, _, info, id):
        return await self.user_service.get_user(id)

    # -----------------
    # Mutations
    # -----------------

    @require_token
    async def resolve_update_user(self, _, info, input):
        model = UpdateUserModel(**input)
        update_data = model.model_dump(exclude_unset=True)

        return await self.user_service.update_user(input["id"], update_data)

    @require_token
    async def resolve_delete_user(self, _, info, id):
        return await self.user_service.delete_user(id)

    # -----------------
    # Export
    # -----------------

    def get_resolvers(self):
        return [self.query, self.mutation]
