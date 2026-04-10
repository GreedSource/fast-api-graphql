from graphql import GraphQLError
from pydantic import ValidationError

from server.helpers.custom_graphql_exception_helper import CustomGraphQLExceptionHelper
from server.helpers.logger_helper import LoggerHelper


def custom_format_error(error: GraphQLError, debug: bool = False):
    original = error.original_error

    # 🔥 LOG CRUDO (esto es lo que quieres ver)
    LoggerHelper.info("🔥 RAW ERROR:", repr(original))

    if isinstance(original, ValidationError):
        return {
            "message": "Error de validación",
            "extensions": {
                "code": "BAD_USER_INPUT",
                "fields": original.errors(),
            },
        }

    if isinstance(original, CustomGraphQLExceptionHelper):
        return {
            "message": original.message,
            "extensions": {
                "code": original.code,
                "details": original.details,
            },
        }

    # 🔥 Aquí metes el raw message
    return {
        "message": str(original) if original else error.message,
        "extensions": {
            "code": "INTERNAL_ERROR",
            "debug": repr(original) if debug else None,
        },
    }
