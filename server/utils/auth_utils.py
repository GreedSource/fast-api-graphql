from datetime import datetime, timedelta, timezone
from typing import Any, Dict

import bcrypt
import jwt

from server.config.settings import settings
from server.enums.http_error_code_enum import HTTPErrorCode
from server.helpers.custom_graphql_exception_helper import CustomGraphQLExceptionHelper


def hash_password(password):
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(password, hashed):
    return bcrypt.checkpw(password.encode(), hashed.encode())


def create_token(payload: dict, expires_in: int = 15) -> str:
    data = payload.copy()
    data["exp"] = datetime.now(timezone.utc) + timedelta(minutes=expires_in)
    return jwt.encode(data, settings.JWT_SECRET_KEY, algorithm="HS256")


def create_refresh_token(payload: dict, expires_in: int = 60 * 24 * 7) -> str:
    data = payload.copy()
    data["exp"] = datetime.now(timezone.utc) + timedelta(minutes=expires_in)
    return jwt.encode(data, settings.JWT_REFRESH_SECRET_KEY, algorithm="HS256")


def verify_refresh_token(token: str) -> Dict[str, Any]:
    try:
        return jwt.decode(token, settings.JWT_REFRESH_SECRET_KEY, algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        raise CustomGraphQLExceptionHelper("Refresh token expirado")
    except jwt.InvalidTokenError:
        raise CustomGraphQLExceptionHelper("Refresh token inválido")


def verify_token(token: str) -> Dict[str, Any]:
    try:
        return jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        raise CustomGraphQLExceptionHelper("Access token expirado", HTTPErrorCode.UNAUTHORIZED)
    except jwt.InvalidTokenError:
        raise CustomGraphQLExceptionHelper("Access token inválido", HTTPErrorCode.UNAUTHORIZED)
