class WebSocketRequestAdapter:
    """Adapta headers/cookies de WebSocket al contrato consumido por autenticación."""

    def __init__(self, headers: dict[str, str], cookies: dict[str, str]) -> None:
        self.headers = headers
        self.cookies = cookies
