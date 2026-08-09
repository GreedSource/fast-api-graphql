from types import SimpleNamespace
from unittest.mock import AsyncMock
from uuid import UUID

import pytest

from server.helpers.custom_graphql_exception_helper import CustomGraphQLExceptionHelper
from server.services.user_service import UserService

USER_ID = UUID("22222222-2222-2222-2222-222222222222")
ROLE_ID = UUID("33333333-3333-3333-3333-333333333333")


def make_user():
    return SimpleNamespace(
        id=USER_ID,
        name="Grace",
        lastname="Hopper",
        email="grace@example.com",
        role=SimpleNamespace(
            id=ROLE_ID,
            name="Admin",
            description="System administrator",
            active=True,
            permissions=[],
        ),
    )


@pytest.mark.asyncio
async def test_update_user_validates_role_updates_and_publishes_payload():
    repository = SimpleNamespace(
        update=AsyncMock(return_value=make_user()),
        find_by_id=AsyncMock(return_value=make_user()),
    )
    role_service = SimpleNamespace(get_role=AsyncMock(return_value={"id": str(ROLE_ID)}))
    redis = SimpleNamespace(publish_json=AsyncMock())
    publisher = SimpleNamespace(notify=AsyncMock())

    service = UserService()
    service._UserService__repository = repository
    service._UserService__role_service = role_service
    service._UserService__redis = redis
    service._UserService__event_publisher = publisher

    result = await service.update_user(str(USER_ID), {"name": "Grace B.", "role_id": str(ROLE_ID)})

    assert result["id"] == str(USER_ID)
    assert result["role"]["id"] == str(ROLE_ID)
    role_service.get_role.assert_awaited_once_with(str(ROLE_ID))
    repository.update.assert_awaited_once_with(str(USER_ID), {"name": "Grace B.", "role_id": str(ROLE_ID)})
    publisher.notify.assert_awaited_once()
    event = publisher.notify.await_args.args[0]
    assert event.user_id == str(USER_ID)
    assert event.payload == result


@pytest.mark.asyncio
async def test_update_user_rejects_missing_role_before_updating():
    repository = SimpleNamespace(update=AsyncMock(), find_by_id=AsyncMock())
    role_service = SimpleNamespace(get_role=AsyncMock(return_value=None))

    service = UserService()
    service._UserService__repository = repository
    service._UserService__role_service = role_service

    with pytest.raises(CustomGraphQLExceptionHelper) as exc_info:
        await service.update_user(str(USER_ID), {"role_id": str(ROLE_ID)})

    assert exc_info.value.message == "Role not found"
    repository.update.assert_not_called()
