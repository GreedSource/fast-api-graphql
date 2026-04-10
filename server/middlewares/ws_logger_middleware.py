class WSLoggerMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] == "websocket":
            print("WS ORIGIN:", dict(scope["headers"]).get(b"origin"))
            print("WS HEADERS:", scope["headers"])
        await self.app(scope, receive, send)
