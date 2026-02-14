import json
import logging

from ariadne import graphql
from ariadne.explorer import ExplorerGraphiQL
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse

from server.config.settings import settings
from server.core.lifespan import lifespan
from server.enums.http_error_code_enum import HTTPErrorCode
from server.helpers.logger_helper import LoggerHelper
from server.middlewares.cookie_logging_middleware import CookieLoggingMiddleware
from server.schema import schema
from server.utils.custom_error_formatter_utils import custom_format_error

# Desactivar logs ruidosos de ariadne
logging.getLogger("ariadne").setLevel(logging.CRITICAL)

explorer_html = ExplorerGraphiQL().html(None)


def create_app() -> FastAPI:
    app = FastAPI(title=settings.APP_NAME, debug=settings.DEBUG, lifespan=lifespan)

    # Middleware de logging de cookies
    app.add_middleware(CookieLoggingMiddleware)

    # Middleware para hosts confiables
    # app.add_middleware(
    #     TrustedHostMiddleware,
    #     allowed_hosts=["localhost", "127.0.0.1", "tu-dominio.com"],
    # )

    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Rutas
    @app.get("/")
    async def root():
        return {"status": "Ok", "message": "Welcome!!"}

    @app.get("/ping")
    async def health_check():
        return {"status": "Ok", "message": "Pong"}

    @app.get("/graphql")
    async def graphql_explorer():
        return HTMLResponse(explorer_html)

    # GraphQL endpoint
    @app.post("/graphql")
    async def graphql_server(request: Request, response: Response):
        data = await request.json()
        operation_name = data.get("operationName", "unnamed")

        LoggerHelper.info(f"GraphQL operation: {operation_name}")

        success, result = await graphql(
            schema,
            data,
            context_value={
                "request": request,
                "response": response,
            },
            debug=app.debug,
            error_formatter=custom_format_error,
        )

        status_code = 200 if success else HTTPErrorCode.BAD_REQUEST.status_code

        if "errors" in result:
            for err in result["errors"]:
                code = err.get("extensions", {}).get("code", "")
                for error_enum in HTTPErrorCode:
                    if code == error_enum.code_name:
                        status_code = error_enum.status_code
                        break
                if status_code != HTTPErrorCode.BAD_REQUEST.status_code:
                    break

        response.status_code = status_code
        response.body = json.dumps(result).encode()
        return response

    return app


app = create_app()
