import json
from collections.abc import AsyncIterator

from redis.asyncio import Redis

from server.config.settings import settings
from server.decorators.singleton_decorator import singleton
from server.helpers.logger_helper import LoggerHelper


@singleton
class RedisHelper:
    def __init__(self):
        self._client: Redis | None = None
        LoggerHelper.success(f"RedisHelper initialized with URL: {settings.REDIS_URL}")

    def get_client(self) -> Redis:
        if self._client is None:
            self._client = Redis.from_url(settings.REDIS_URL, decode_responses=True)
        return self._client

    async def publish_json(self, channel: str, payload: dict) -> None:
        message = json.dumps(payload)
        await self.get_client().publish(channel, message)

    async def subscribe(self, channel: str) -> AsyncIterator[dict]:
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
            await pubsub.aclose()

    async def close(self) -> None:
        if self._client is not None:
            await self._client.aclose()
            self._client = None
            LoggerHelper.info("Redis connection closed")
