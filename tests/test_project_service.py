from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

from server.helpers.custom_graphql_exception_helper import CustomGraphQLExceptionHelper
from server.models.dto.project_dto import CreateProjectModel, UpdateProjectModel
from server.services.project_service import ProjectService
from tests.factories import PROJECT_ID, USER_ID, make_project


@pytest.mark.asyncio
async def test_project_service_create_serializes_project():
    repository = SimpleNamespace(create=AsyncMock(return_value=make_project()))
    service = ProjectService()
    service._ProjectService__repository = repository

    result = await service.create(CreateProjectModel(name="Apollo", ownerId=str(USER_ID)))

    assert result["id"] == str(PROJECT_ID)
    assert result["ownerId"] == str(USER_ID)
    repository.create.assert_awaited_once_with({"name": "Apollo", "owner_id": USER_ID})


@pytest.mark.asyncio
async def test_project_service_update_rejects_missing_project():
    repository = SimpleNamespace(update=AsyncMock(return_value=None))
    service = ProjectService()
    service._ProjectService__repository = repository

    with pytest.raises(CustomGraphQLExceptionHelper) as exc_info:
        await service.update(UpdateProjectModel(id=PROJECT_ID, name="Apollo 2"))

    assert exc_info.value.message == "Proyecto no encontrado"


@pytest.mark.asyncio
async def test_project_service_archive_serializes_archived_project():
    repository = SimpleNamespace(archive=AsyncMock(return_value=make_project(status="archived")))
    service = ProjectService()
    service._ProjectService__repository = repository

    result = await service.archive(str(PROJECT_ID))

    assert result["status"] == "archived"
    repository.archive.assert_awaited_once_with(str(PROJECT_ID))
