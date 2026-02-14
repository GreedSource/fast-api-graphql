from ariadne import MutationType, QueryType
from graphql import GraphQLResolveInfo

from server.config.settings import settings
from server.decorators.require_token_decorator import require_token
from server.enums.http_error_code_enum import HTTPErrorCode
from server.helpers.custom_graphql_exception_helper import CustomGraphQLExceptionHelper
from server.helpers.logger_helper import LoggerHelper
from server.models.response_model import ResponseModel
from server.models.user_model import RegisterModel
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

    async def resolve_register(self, _, info: GraphQLResolveInfo, input):
        model = RegisterModel(**input)

        user = await self.auth_service.register(user_data=model.model_dump())

        return ResponseModel(
            status=200,
            message="User registered successfully",
            data=user,
        )

    # En tu AuthResolver
    async def resolve_login(self, _, info: GraphQLResolveInfo, input):
        response = info.context["response"]

        payload = await self.auth_service.login(email=input["email"], password=input["password"])
        # Actualizar access token en cookie
        response.set_cookie(
            key=settings.ACCESS_COOKIE_NAME,
            value=payload["accessToken"],
            httponly=True,
            secure=True,
            samesite="lax",
            max_age=60 * 60,
        )
        # Refresh token en cookie
        response.set_cookie(
            key=settings.REFRESH_COOKIE_NAME,
            value=payload["refreshToken"],
            httponly=True,
            secure=True,  # HTTPS
            samesite="lax",  # "none" si frontend en otro dominio
            max_age=7 * 24 * 60 * 60,  # 7
        )

        return ResponseModel(
            status=200,
            message="Login successful",
            data=payload,
        )

    async def resolve_refresh_token(self, _, info: GraphQLResolveInfo, refreshToken=None):
        request = info.context["request"]
        response = info.context["response"]

        # 1️⃣ Prioridad: argumento GraphQL
        token = refreshToken

        # 2️⃣ Fallback: cookie
        if not token:
            token = request.cookies.get(settings.REFRESH_COOKIE_NAME)

        if not token:
            raise CustomGraphQLExceptionHelper(
                "Refresh token no proporcionado",
                HTTPErrorCode.UNAUTHORIZED,
            )

        result = await self.auth_service.refresh_token(token)

        # Nuevo access token → cookie
        response.set_cookie(
            key=settings.ACCESS_COOKIE_NAME,
            value=result["accessToken"],
            httponly=True,
            secure=True,
            samesite="lax",
            max_age=60 * 60,
        )

        return ResponseModel(
            status=200,
            message="Token refreshed",
            data=result,
        )

    async def resolve_recover_password(self, _, info: GraphQLResolveInfo, email):
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
    async def resolve_profile(self, _, info: GraphQLResolveInfo):
        return ResponseModel(
            status=200,
            message="Profile retrieved",
            data=info.context["current_user"],
        )

    def get_resolvers(self):
        return [self.query, self.mutation]
