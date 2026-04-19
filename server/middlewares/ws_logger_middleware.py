from starlette.types import ASGIApp, Receive, Scope, Send


class WSLoggerMiddleware:
    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(
        self,
        scope: Scope,
        receive: Receive,
        send: Send,
    ) -> None:
        if scope["type"] == "websocket":
            print("WS ORIGIN:", dict(scope["headers"]).get(b"origin"))
            print("WS HEADERS:", scope["headers"])

        await self.app(scope, receive, send)
