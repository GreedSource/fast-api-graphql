from typing import Any

from server.enums.http_error_code_enum import HTTPErrorCode


class CustomGraphQLExceptionHelper(Exception):
    def __init__(
        self,
        message: str,
        code: HTTPErrorCode = HTTPErrorCode.BAD_REQUEST,
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        if isinstance(code, HTTPErrorCode):
            self.code = code.code_name
            self.status_code = code.status_code
        else:
            # En caso de que se pase un string o algo diferente
            self.code = str(code)
            self.status_code = 400
        self.details = details or {}

    def to_dict(self) -> dict[str, Any]:
        return {
            "message": self.message,
            "extensions": {
                "code": self.code,
                "details": self.details,
            },
        }
