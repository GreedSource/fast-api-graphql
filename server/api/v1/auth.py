from fastapi import APIRouter, BackgroundTasks, Depends, Request, Response
from pydantic import BaseModel, EmailStr

from server.api.dependencies import get_current_user
from server.api.responses import api_response
from server.config.settings import settings
from server.enums.http_error_code_enum import HTTPErrorCode
from server.helpers.custom_graphql_exception_helper import CustomGraphQLExceptionHelper
from server.models.dto.user_dto import RegisterModel, ResetPasswordModel
from server.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["Authentication"])
service = AuthService()


class LoginBody(BaseModel):
    email: EmailStr
    password: str


class RefreshBody(BaseModel):
    refresh_token: str | None = None


class RecoverPasswordBody(BaseModel):
    email: EmailStr


def set_auth_cookies(response: Response, payload: dict):
    response.set_cookie(settings.ACCESS_COOKIE_NAME, payload["accessToken"], httponly=True, secure=True, samesite="lax")
    if payload.get("refreshToken"):
        response.set_cookie(
            settings.REFRESH_COOKIE_NAME,
            payload["refreshToken"],
            httponly=True,
            secure=True,
            samesite="lax",
        )


@router.post("/register", status_code=201)
async def register(payload: RegisterModel):
    return api_response(await service.register(payload.model_dump()), "User registered", 201)


@router.post("/login")
async def login(payload: LoginBody, response: Response):
    result = await service.login(payload.email, payload.password)
    set_auth_cookies(response, result)
    return api_response(result, "Login successful")


@router.post("/refresh")
async def refresh(payload: RefreshBody, request: Request, response: Response):
    token = payload.refresh_token or request.cookies.get(settings.REFRESH_COOKIE_NAME)
    if not token:
        raise CustomGraphQLExceptionHelper("Refresh token no proporcionado", HTTPErrorCode.UNAUTHORIZED)
    result = await service.refresh_token(token)
    set_auth_cookies(response, result)
    return api_response(result, "Token refreshed")


@router.get("/profile")
async def profile(user: dict = Depends(get_current_user)):
    return api_response(user, "Profile retrieved")


@router.post("/recover-password")
async def recover_password(payload: RecoverPasswordBody, background_tasks: BackgroundTasks):
    return api_response(await service.recover_password(payload.email, background_tasks), "Recovery email sent")


@router.post("/reset-password")
async def reset_password(payload: ResetPasswordModel):
    return api_response(await service.reset_password(payload.token, payload.password), "Password reset successful")


@router.post("/logout")
async def logout(response: Response):
    response.delete_cookie(settings.ACCESS_COOKIE_NAME)
    response.delete_cookie(settings.REFRESH_COOKIE_NAME)
    return api_response(await service.logout(), "Logout successful")
