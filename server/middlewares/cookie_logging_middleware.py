from typing import TYPE_CHECKING, Awaitable, Callable, cast

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware as _BaseHTTPMiddleware
from starlette.responses import Response
from starlette.types import ASGIApp, Receive, Scope, Send

from server.helpers.logger_helper import LoggerHelper

if TYPE_CHECKING:
    from starlette.middleware.base import RequestResponseEndpoint

    class _TypedBaseHTTPMiddleware:
        def __init__(
            self,
            app: ASGIApp,
            dispatch: Callable[[Request, RequestResponseEndpoint], Awaitable[Response]] | None = None,
        ) -> None: ...

        async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None: ...

        async def dispatch(
            self,
            request: Request,
            call_next: RequestResponseEndpoint,
        ) -> Response: ...

    BaseHTTPMiddlewareBase = _TypedBaseHTTPMiddleware
else:
    BaseHTTPMiddlewareBase = cast(type[object], _BaseHTTPMiddleware)


class CookieLoggingMiddleware(BaseHTTPMiddlewareBase):
    async def dispatch(self, request: Request, call_next: Callable[[Request], Awaitable[Response]]) -> Response:
        # Log de cookies entrantes (evita datos sensibles)
        cookies = request.cookies
        if cookies:
            LoggerHelper.info(f"Cookies recibidas: {list(cookies.keys())}")

        response = await call_next(request)

        # Log de cookies establecidas
        if "set-cookie" in response.headers:
            LoggerHelper.info("Cookies establecidas en la respuesta")

        return response
