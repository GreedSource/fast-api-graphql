from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

from server.helpers.logger_helper import LoggerHelper


class CookieLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Log de cookies entrantes (evita datos sensibles)
        cookies = request.cookies
        if cookies:
            LoggerHelper.info(f"Cookies recibidas: {list(cookies.keys())}")

        response = await call_next(request)

        # Log de cookies establecidas
        if "set-cookie" in response.headers:
            LoggerHelper.info("Cookies establecidas en la respuesta")

        return response
