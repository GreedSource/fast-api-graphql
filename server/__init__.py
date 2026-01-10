import logging
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, HTMLResponse
from ariadne import graphql
from ariadne.explorer import ExplorerGraphiQL

from server.core.lifespan import lifespan
from server.enums.http_error_code_enum import HTTPErrorCode
from server.helpers.logger_helper import LoggerHelper
from server.schema import schema
from server.utils.custom_error_formatter_utils import custom_format_error
from server.helpers.mail_helper import MailHelper

# Desactivar logs ruidosos de ariadne
logging.getLogger("ariadne").setLevel(logging.CRITICAL)

explorer_html = ExplorerGraphiQL().html(None)


def create_app() -> FastAPI:
    app = FastAPI(title="GraphQL API", lifespan=lifespan)

    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Inicializar MailHelper
    # MailHelper().init_app()

    @app.get("/")
    async def root():
        return {"status": "Ok", "message": "Welcome!!"}

    @app.get("/ping")
    async def health_check():
        return {"status": "Ok", "message": "Pong"}

    @app.get("/graphql")
    async def graphql_explorer():
        return HTMLResponse(explorer_html)

    @app.post("/graphql")
    async def graphql_server(request: Request):
        data = await request.json()
        operation_name = data.get("operationName", "unnamed")
        LoggerHelper.info(f"GraphQL operation: {operation_name}")

        success, result = await graphql(
            schema,
            data,
            context_value={"request": request},
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

        return JSONResponse(content=result, status_code=status_code)

    return app


app = create_app()
