from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

from server.models.dto.module_dto import CreateModuleModel, UpdateModuleModel
from server.services.module_service import ModuleService
from tests.factories import MODULE_ID, make_module


@pytest.mark.asyncio
async def test_module_service_create_serializes_created_module():
    repository = SimpleNamespace(create=AsyncMock(return_value=make_module()))
    service = ModuleService()
    service.repository = repository

    result = await service.create(CreateModuleModel(name=" Users ", key=" USERS ", description=" User management "))

    assert result == {
        "id": MODULE_ID,
        "name": "Users",
        "key": "users",
        "description": "User management",
        "active": True,
    }
    repository.create.assert_awaited_once_with(
        {
            "name": "Users",
            "key": "users",
            "description": "User management",
            "active": True,
        }
    )


@pytest.mark.asyncio
async def test_module_service_update_returns_none_when_repository_misses():
    repository = SimpleNamespace(update=AsyncMock(return_value=None))
    service = ModuleService()
    service.repository = repository

    result = await service.update(UpdateModuleModel(id=MODULE_ID, name="Users API"))

    assert result is None
    repository.update.assert_awaited_once_with(MODULE_ID, {"name": "Users API"})


@pytest.mark.asyncio
async def test_module_service_get_one_returns_none_for_missing_module():
    repository = SimpleNamespace(find_by_id=AsyncMock(return_value=None))
    service = ModuleService()
    service.repository = repository

    assert await service.get_one(str(MODULE_ID)) is None
