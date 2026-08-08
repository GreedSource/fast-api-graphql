from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

from server.helpers.custom_graphql_exception_helper import CustomGraphQLExceptionHelper
from server.models.dto.task_dto import CreateTaskModel, UpdateTaskModel
from server.services.task_service import TaskService
from tests.factories import PROJECT_ID, TASK_ID, USER_ID, make_project, make_task


@pytest.mark.asyncio
async def test_task_service_create_requires_existing_project():
    service = TaskService()
    service._TaskService__project_repository = SimpleNamespace(find_by_id=AsyncMock(return_value=None))

    with pytest.raises(CustomGraphQLExceptionHelper) as exc_info:
        await service.create(CreateTaskModel(projectId=str(PROJECT_ID), title="Build API"))

    assert exc_info.value.message == "Proyecto no encontrado"


@pytest.mark.asyncio
async def test_task_service_create_serializes_task():
    repository = SimpleNamespace(create=AsyncMock(return_value=make_task()))
    project_repository = SimpleNamespace(find_by_id=AsyncMock(return_value=make_project()))
    service = TaskService()
    service._TaskService__repository = repository
    service._TaskService__project_repository = project_repository

    result = await service.create(
        CreateTaskModel(projectId=str(PROJECT_ID), title="Build API", assigneeId=str(USER_ID))
    )

    assert result["id"] == str(TASK_ID)
    assert result["projectId"] == str(PROJECT_ID)
    repository.create.assert_awaited_once_with(
        {
            "project_id": PROJECT_ID,
            "title": "Build API",
            "priority": "medium",
            "assignee_id": USER_ID,
        }
    )


@pytest.mark.asyncio
async def test_task_service_update_rejects_missing_task():
    service = TaskService()
    service._TaskService__repository = SimpleNamespace(update=AsyncMock(return_value=None))

    with pytest.raises(CustomGraphQLExceptionHelper) as exc_info:
        await service.update(UpdateTaskModel(id=TASK_ID, title="New title"))

    assert exc_info.value.message == "Tarea no encontrada"
    assert exc_info.value.status_code == 404


@pytest.mark.asyncio
async def test_task_service_complete_serializes_completed_task():
    repository = SimpleNamespace(complete=AsyncMock(return_value=make_task(status="done")))
    service = TaskService()
    service._TaskService__repository = repository

    result = await service.complete(str(TASK_ID))

    assert result["status"] == "done"
    repository.complete.assert_awaited_once_with(str(TASK_ID))
