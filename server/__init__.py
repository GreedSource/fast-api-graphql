import json
import logging

from ariadne import graphql
from ariadne.explorer import ExplorerGraphiQL
from ariadne.types import ExecutionResult
from fastapi import FastAPI, Request, Response, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from graphql import parse
from graphql import subscribe as graphql_subscribe
from starlette.background import BackgroundTasks

from server.config.settings import settings
from server.enums.http_error_code_enum import HTTPErrorCode
from server.helpers.logger_helper import LoggerHelper
from server.helpers.mail_helper import MailHelper
from server.helpers.template_helper import TemplateHelper
from server.middlewares.cookie_logging_middleware import CookieLoggingMiddleware
from server.middlewares.ws_logger_middleware import WSLoggerMiddleware
from server.schema import schema
from server.utils.custom_error_formatter_utils import custom_format_error

# Desactivar logs ruidosos de ariadne
logging.getLogger("ariadne").setLevel(logging.CRITICAL)

explorer_html = ExplorerGraphiQL().html(None)


def create_app() -> FastAPI:
    app = FastAPI(title=settings.APP_NAME, debug=settings.DEBUG)

    # ✅ Inicializar MailHelper AQUÍ
    MailHelper().init_app()

    TemplateHelper().init_app()

    # Middleware de logging de cookies
    app.add_middleware(CookieLoggingMiddleware)
    app.add_middleware(WSLoggerMiddleware)

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
    async def graphql_server(request: Request, response: Response, background_tasks: BackgroundTasks):
        data = await request.json()
        operation_name = data.get("operationName", "unnamed")

        LoggerHelper.info(f"GraphQL operation: {operation_name}")

        success, result = await graphql(
            schema,
            data,
            context_value={
                "request": request,
                "response": response,
                "background_tasks": background_tasks,  # 👈 aquí
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

    @app.websocket("/graphql")
    async def graphql_websocket(websocket: WebSocket):
        """GraphQL WebSocket subscriptions (graphql-transport-ws protocol)"""
        await websocket.accept(subprotocol="graphql-transport-ws")
        LoggerHelper.info(f"WS connected from {websocket.client}")

        try:
            while True:
                data = await websocket.receive_json()
                msg_type = data.get("type")
                LoggerHelper.info(f"WS msg type: {msg_type}")

                if msg_type == "connection_init":
                    await websocket.send_json({"type": "connection_ack"})
                    LoggerHelper.info("Sent connection_ack")

                elif msg_type == "subscribe":
                    sub_id = data.get("id")
                    payload = data.get("payload", {})
                    LoggerHelper.info(f"Subscribe {sub_id}")

                    try:
                        query_string = payload.get("query", "")
                        variables = payload.get("variables", {})
                        operation_name = payload.get("operationName")

                        document = parse(query_string)

                        # 🔥 FIX: primero await
                        result = await graphql_subscribe(
                            schema,
                            document,
                            variable_values=variables,
                            operation_name=operation_name,
                            context_value={"request": None, "response": None},
                        )

                        # 🔥 Si hay error inmediato (no subscription válida)
                        if isinstance(result, ExecutionResult):
                            await websocket.send_json(
                                {
                                    "id": sub_id,
                                    "type": "error",
                                    "payload": [{"message": str(err)} for err in (result.errors or [])],
                                }
                            )
                            continue

                        # 🔥 Ahora sí es async iterable
                        async for item in result:
                            await websocket.send_json(
                                {
                                    "id": sub_id,
                                    "type": "next",
                                    "payload": {
                                        "data": item.data,
                                        "errors": [{"message": str(err)} for err in (item.errors or [])]
                                        if item.errors
                                        else None,
                                    },
                                }
                            )

                        await websocket.send_json({"id": sub_id, "type": "complete"})

                    except Exception as e:
                        LoggerHelper.error(f"Sub error: {str(e)}")
                        await websocket.send_json(
                            {
                                "id": sub_id,
                                "type": "error",
                                "payload": [{"message": str(e)}],
                            }
                        )

        except WebSocketDisconnect:
            LoggerHelper.info("WS disconnected")

        except Exception as e:
            LoggerHelper.error(f"WS error: {str(e)}")
            try:
                await websocket.close(code=1011)
            except Exception:
                pass

    return app


app = create_app()
