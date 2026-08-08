from datetime import datetime, timedelta, timezone

import jwt
import pytest

from server.config.settings import settings
from server.helpers.custom_graphql_exception_helper import CustomGraphQLExceptionHelper
from server.utils.auth_utils import create_refresh_token, create_token, hash_password, verify_password, verify_token


def test_hash_password_creates_verifiable_non_plaintext_hash():
    hashed = hash_password("Secret123!")

    assert hashed != "Secret123!"
    assert verify_password("Secret123!", hashed) is True
    assert verify_password("Wrong123!", hashed) is False


def test_create_and_verify_access_token_roundtrip():
    token = create_token({"id": "user-1"}, expires_in=1)

    assert verify_token(token)["id"] == "user-1"


def test_verify_token_rejects_expired_access_token():
    expired_token = jwt.encode(
        {"id": "user-1", "exp": datetime.now(timezone.utc) - timedelta(minutes=1)},
        settings.JWT_SECRET_KEY,
        algorithm="HS256",
    )

    with pytest.raises(CustomGraphQLExceptionHelper) as exc_info:
        verify_token(expired_token)

    assert exc_info.value.status_code == 401
    assert exc_info.value.message == "Access token expirado"


def test_create_refresh_token_uses_refresh_secret():
    token = create_refresh_token({"id": "user-1"}, expires_in=1)

    decoded = jwt.decode(token, settings.JWT_REFRESH_SECRET_KEY, algorithms=["HS256"])

    assert decoded["id"] == "user-1"
