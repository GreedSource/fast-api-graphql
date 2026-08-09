from dataclasses import dataclass

from server.helpers.redis_helper import RedisHelper


@dataclass(frozen=True)
class UserUpdatedEvent:
    user_id: str
    payload: dict


class UserUpdatedRedisObserver:
    """Adapter/observer que traduce eventos de usuario al contrato de Redis."""

    def __init__(self, redis: RedisHelper) -> None:
        self._redis = redis

    async def update(self, event: UserUpdatedEvent) -> None:
        await self._redis.publish_json(f"user_updated:{event.user_id}", event.payload)
