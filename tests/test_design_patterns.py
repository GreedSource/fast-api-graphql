from unittest.mock import AsyncMock

import pytest

from server.adapters.websocket_request_adapter import WebSocketRequestAdapter
from server.decorators.singleton_decorator import singleton
from server.observers.event_publisher import AsyncEventPublisher
from server.observers.user_updated_observer import UserUpdatedEvent, UserUpdatedRedisObserver
from server.strategies.permission_check_strategy import (
    AllPermissionsStrategy,
    AnyPermissionStrategy,
    PermissionCheckStrategyFactory,
)


def test_singleton_decorator_reuses_the_first_instance():
    @singleton
    class Example:
        def __init__(self, value):
            self.value = value

    assert Example("first") is Example("second")
    assert Example().value == "first"


def test_permission_strategy_factory_creates_supported_strategies():
    assert isinstance(PermissionCheckStrategyFactory.create("any"), AnyPermissionStrategy)
    assert isinstance(PermissionCheckStrategyFactory.create("all"), AllPermissionsStrategy)


def test_permission_strategies_apply_any_and_all_semantics():
    user_permissions = [{"type": "users", "action": "read"}]
    required = [
        {"type": "users", "action": "read"},
        {"type": "roles", "action": "update"},
    ]

    assert PermissionCheckStrategyFactory.create("any").is_allowed(user_permissions, required) is True
    assert PermissionCheckStrategyFactory.create("all").is_allowed(user_permissions, required) is False


def test_permission_strategy_factory_rejects_unknown_mode():
    with pytest.raises(ValueError, match="no soportado"):
        PermissionCheckStrategyFactory.create("unknown")


@pytest.mark.asyncio
async def test_event_publisher_notifies_and_can_detach_observer():
    observer = AsyncMock()
    publisher = AsyncEventPublisher()
    event = UserUpdatedEvent(user_id="user-1", payload={"name": "Ada"})

    publisher.attach(observer)
    await publisher.notify(event)
    publisher.detach(observer)
    await publisher.notify(event)

    observer.update.assert_awaited_once_with(event)


@pytest.mark.asyncio
async def test_user_updated_redis_observer_adapts_event_to_channel():
    redis = AsyncMock()
    observer = UserUpdatedRedisObserver(redis)
    event = UserUpdatedEvent(user_id="user-1", payload={"name": "Ada"})

    await observer.update(event)

    redis.publish_json.assert_awaited_once_with("user_updated:user-1", event.payload)


def test_websocket_request_adapter_exposes_request_contract():
    adapter = WebSocketRequestAdapter(
        headers={"authorization": "Bearer token"},
        cookies={"access_token": "token"},
    )

    assert adapter.headers["authorization"] == "Bearer token"
    assert adapter.cookies["access_token"] == "token"
