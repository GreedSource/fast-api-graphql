import json
from collections.abc import AsyncIterator
from typing import Any, Protocol, cast

from redis.asyncio import Redis

from server.config.settings import settings
from server.decorators.singleton_decorator import singleton
from server.helpers.logger_helper import LoggerHelper


class RedisPubSubProtocol(Protocol):
    async def subscribe(self, *channels: str) -> None: ...
    def listen(self) -> AsyncIterator[dict[str, Any]]: ...
    async def unsubscribe(self, *channels: str) -> None: ...
    async def aclose(self) -> None: ...


class RedisClientProtocol(Protocol):
    async def publish(self, channel: str, message: str) -> int: ...
    def pubsub(self) -> RedisPubSubProtocol: ...
    async def aclose(self) -> None: ...


@singleton
class RedisHelper:
    def __init__(self) -> None:
        self._client: RedisClientProtocol | None = None
        LoggerHelper.success(f"RedisHelper initialized with URL: {settings.REDIS_URL}")

    def get_client(self) -> RedisClientProtocol:
        if self._client is None:
            self._client = cast(RedisClientProtocol, Redis.from_url(settings.REDIS_URL, decode_responses=True))
        return self._client

    async def publish_json(self, channel: str, payload: dict[str, Any]) -> None:
        message = json.dumps(payload)
        await self.get_client().publish(channel, message)

    async def subscribe(self, channel: str) -> AsyncIterator[dict[str, Any]]:
        pubsub = self.get_client().pubsub()
        await pubsub.subscribe(channel)

        try:
            async for message in pubsub.listen():
                if message.get("type") != "message":
                    continue

                data = message.get("data")
                if not data:
                    continue

                yield json.loads(data)
        finally:
            await pubsub.unsubscribe(channel)
            await cast(Any, pubsub).aclose()

    async def close(self) -> None:
        if self._client is not None:
            await cast(Any, self._client).aclose()
            self._client = None
            LoggerHelper.info("Redis connection closed")
