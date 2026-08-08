from graphql import GraphQLError

from server.enums.http_error_code_enum import HTTPErrorCode
from server.helpers.custom_graphql_exception_helper import CustomGraphQLExceptionHelper
from server.helpers.mail_helper import MailHelper
from server.utils.custom_error_formatter_utils import custom_format_error


def test_custom_graphql_exception_to_dict_contains_extensions():
    error = CustomGraphQLExceptionHelper("No autorizado", HTTPErrorCode.UNAUTHORIZED, {"reason": "missing"})

    assert error.to_dict() == {
        "message": "No autorizado",
        "extensions": {
            "code": "UNAUTHORIZED",
            "details": {"reason": "missing"},
        },
    }
    assert error.status_code == 401


def test_custom_format_error_maps_custom_exception():
    original = CustomGraphQLExceptionHelper("Forbidden", HTTPErrorCode.FORBIDDEN)
    formatted = custom_format_error(GraphQLError("wrapped", original_error=original))

    assert formatted["message"] == "Forbidden"
    assert formatted["extensions"]["code"] == "FORBIDDEN"


def test_custom_format_error_hides_debug_by_default():
    formatted = custom_format_error(GraphQLError("wrapped", original_error=RuntimeError("boom")))

    assert formatted == {
        "message": "boom",
        "extensions": {
            "code": "INTERNAL_ERROR",
            "debug": None,
        },
    }


def test_mail_helper_requires_initialization_before_sending():
    helper = MailHelper()
    helper._initialized = False

    try:
        helper.send_email("Subject", ["to@example.com"], body="Body")
    except CustomGraphQLExceptionHelper as exc:
        assert exc.message == "MailHelper no está inicializado"
    else:
        raise AssertionError("Expected CustomGraphQLExceptionHelper")
