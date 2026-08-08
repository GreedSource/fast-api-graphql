from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

from server.helpers.custom_graphql_exception_helper import CustomGraphQLExceptionHelper
from server.models.dto.permission_dto import CreatePermissionModel
from server.services.permission_service import PermissionService
from tests.factories import ACTION_ID, MODULE_ID, PERMISSION_ID, make_action, make_module, make_permission


@pytest.mark.asyncio
async def test_permission_service_create_accepts_uuid_or_key_and_serializes_aliases():
    permission_repo = SimpleNamespace(
        find_by_module_and_action=AsyncMock(return_value=None),
        create=AsyncMock(return_value=make_permission(module=None, action=None)),
    )
    module_service = SimpleNamespace(
        find_by_id=AsyncMock(return_value=None),
        find_by_key=AsyncMock(return_value=make_module()),
    )
    action_service = SimpleNamespace(
        find_by_id=AsyncMock(return_value=make_action()),
        find_by_key=AsyncMock(),
    )
    service = PermissionService()
    service._PermissionService__permission_repo = permission_repo
    service._PermissionService__module_service = module_service
    service._PermissionService__action_service = action_service

    result = await service.create(
        CreatePermissionModel(moduleId="users", actionId=str(ACTION_ID), description="Users read permission")
    )

    assert result == {
        "id": PERMISSION_ID,
        "moduleId": MODULE_ID,
        "actionId": ACTION_ID,
        "moduleKey": "users",
        "actionKey": "read",
        "description": "Users read permission",
    }
    module_service.find_by_id.assert_awaited_once_with("users")
    module_service.find_by_key.assert_awaited_once_with("users")
    action_service.find_by_id.assert_awaited_once_with(str(ACTION_ID))
    action_service.find_by_key.assert_not_called()
    permission_repo.find_by_module_and_action.assert_awaited_once_with(MODULE_ID, ACTION_ID)


@pytest.mark.asyncio
async def test_permission_service_create_rejects_missing_module():
    service = PermissionService()
    service._PermissionService__module_service = SimpleNamespace(
        find_by_id=AsyncMock(return_value=None),
        find_by_key=AsyncMock(return_value=None),
    )

    with pytest.raises(CustomGraphQLExceptionHelper) as exc_info:
        await service.create(CreatePermissionModel(moduleId="missing", actionId="read"))

    assert exc_info.value.message == "Module not found"


@pytest.mark.asyncio
async def test_permission_service_create_rejects_duplicate_permission():
    service = PermissionService()
    service._PermissionService__module_service = SimpleNamespace(
        find_by_id=AsyncMock(return_value=make_module()),
        find_by_key=AsyncMock(),
    )
    service._PermissionService__action_service = SimpleNamespace(
        find_by_id=AsyncMock(return_value=make_action()),
        find_by_key=AsyncMock(),
    )
    service._PermissionService__permission_repo = SimpleNamespace(
        find_by_module_and_action=AsyncMock(return_value=make_permission()),
    )

    with pytest.raises(CustomGraphQLExceptionHelper) as exc_info:
        await service.create(CreatePermissionModel(moduleId=str(MODULE_ID), actionId=str(ACTION_ID)))

    assert exc_info.value.message == "El permiso ya existe para ese módulo y acción"


@pytest.mark.asyncio
async def test_permission_service_get_all_maps_missing_relations_as_unknown():
    service = PermissionService()
    service._PermissionService__permission_repo = SimpleNamespace(
        find_all=AsyncMock(return_value=[make_permission(module=None, action=None)])
    )

    result = await service.get_all()

    assert result[0]["moduleKey"] == "unknown"
    assert result[0]["actionKey"] == "unknown"
