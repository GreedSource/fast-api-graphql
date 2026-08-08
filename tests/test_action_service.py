from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

from server.models.dto.action_dto import CreateActionModel
from server.services.action_service import ActionService
from tests.factories import ACTION_ID, make_action


@pytest.mark.asyncio
async def test_action_service_create_serializes_created_action():
    repository = SimpleNamespace(create=AsyncMock(return_value=make_action()))
    service = ActionService()
    service._ActionService__repository = repository

    result = await service.create(CreateActionModel(name=" Read ", key=" READ ", description=" Read records "))

    assert result == {
        "id": ACTION_ID,
        "name": "Read",
        "key": "read",
        "description": "Read records",
        "active": True,
    }
    repository.create.assert_awaited_once_with(
        {
            "name": "Read",
            "key": "read",
            "description": "Read records",
            "active": True,
        }
    )


@pytest.mark.asyncio
async def test_action_service_get_all_serializes_list():
    repository = SimpleNamespace(find_all=AsyncMock(return_value=[make_action()]))
    service = ActionService()
    service._ActionService__repository = repository

    result = await service.get_all()

    assert result[0]["id"] == ACTION_ID
    assert result[0]["key"] == "read"
