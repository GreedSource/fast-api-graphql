from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

from server.helpers.custom_graphql_exception_helper import CustomGraphQLExceptionHelper
from server.models.dto.role_dto import CreateRoleModel, UpdateRoleModel
from server.services.role_service import RoleService
from tests.factories import PERMISSION_ID, ROLE_ID, make_role


@pytest.mark.asyncio
async def test_role_service_create_serializes_permissions():
    repository = SimpleNamespace(create=AsyncMock(return_value=make_role()))
    service = RoleService()
    service._RoleService__repository = repository

    result = await service.create(CreateRoleModel(name="Admin", description="System administrator"))

    assert result["id"] == ROLE_ID
    assert result["permissions"] == [{"action": "read", "type": "users"}]
    repository.create.assert_awaited_once_with(
        {
            "name": "Admin",
            "description": "System administrator",
            "active": True,
        }
    )


@pytest.mark.asyncio
async def test_role_service_update_rejects_missing_role():
    repository = SimpleNamespace(update=AsyncMock(return_value=None))
    service = RoleService()
    service._RoleService__repository = repository

    with pytest.raises(CustomGraphQLExceptionHelper) as exc_info:
        await service.update(UpdateRoleModel(id=ROLE_ID, name="Admin"))

    assert exc_info.value.message == "No se encontró el rol para actualizar"


@pytest.mark.asyncio
async def test_role_service_assign_permissions_returns_true_when_repository_succeeds():
    repository = SimpleNamespace(assign_permissions=AsyncMock(return_value=make_role()))
    service = RoleService()
    service._RoleService__repository = repository

    assert await service.assign_permissions(str(ROLE_ID), [str(PERMISSION_ID)]) is True
    repository.assign_permissions.assert_awaited_once_with(str(ROLE_ID), [str(PERMISSION_ID)])


@pytest.mark.asyncio
async def test_role_service_add_permissions_rejects_repository_failure():
    repository = SimpleNamespace(add_permissions=AsyncMock(return_value=None))
    service = RoleService()
    service._RoleService__repository = repository

    with pytest.raises(CustomGraphQLExceptionHelper) as exc_info:
        await service.add_permissions(str(ROLE_ID), [str(PERMISSION_ID)])

    assert exc_info.value.message == "No se pudo agregar permisos al rol"
