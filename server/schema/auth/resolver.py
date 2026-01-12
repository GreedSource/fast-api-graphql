from ariadne import QueryType, MutationType

from server.decorators.require_token_decorator import require_token
from server.helpers.logger_helper import LoggerHelper
from server.models.user_model import RegisterModel
from server.models.response_model import ResponseModel
from server.services.auth_service import AuthService


class AuthResolver:
    def __init__(self):
        self.query = QueryType()
        self.mutation = MutationType()

        self.auth_service = AuthService()

        self._bind_queries()
        self._bind_mutations()

        LoggerHelper.info("AuthResolver initialized")

    # -----------------
    # Bindings
    # -----------------

    def _bind_queries(self):
        self.query.set_field("profile", self.resolve_profile)

    def _bind_mutations(self):
        self.mutation.set_field("register", self.resolve_register)
        self.mutation.set_field("login", self.resolve_login)
        self.mutation.set_field("refreshToken", self.resolve_refresh_token)
        self.mutation.set_field("recoverPassword", self.resolve_recover_password)

    # -----------------
    # Mutations
    # -----------------

    async def resolve_register(self, _, info, input):
        model = RegisterModel(**input)

        user = await self.auth_service.register(user_data=model.model_dump())

        return ResponseModel(
            status=200,
            message="User registered successfully",
            data=user,
        )

    # En tu AuthResolver
    async def resolve_login(self, _, info, input):
        response = await self.auth_service.login(
            email=input["email"], password=input["password"]
        )
        return ResponseModel(
            status=200,
            message="Login successful",
            data=response,
        )

    async def resolve_refresh_token(self, _, info, refreshToken):
        response = await self.auth_service.refresh_token(
            refresh_token=refreshToken,
        )

        return ResponseModel(
            status=200,
            message="Token refreshed",
            data=response,
        )

    async def resolve_recover_password(self, _, info, email):
        request = info.context["request"]

        result = await self.auth_service.recover_password(
            email=email,
            background_tasks=request.state.background_tasks,
        )

        return ResponseModel(
            status=200,
            message="Recovery email sent",
            data=result,
        )

    # -----------------
    # Queries
    # -----------------

    @require_token
    async def resolve_profile(self, _, info):
        return ResponseModel(
            status=200,
            message="Profile retrieved",
            data=info.context["current_user"],
        )

    def get_resolvers(self):
        return [self.query, self.mutation]
