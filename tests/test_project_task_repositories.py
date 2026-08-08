import pytest

from server.repositories.project_repository import ProjectRepository
from server.repositories.task_repository import TaskRepository


@pytest.mark.asyncio
async def test_project_repository_find_by_id_returns_none_for_invalid_uuid_without_db_call():
    assert await ProjectRepository().find_by_id("not-a-uuid") is None


@pytest.mark.asyncio
async def test_project_repository_delete_returns_false_for_invalid_uuid_without_db_call():
    assert await ProjectRepository().delete("not-a-uuid") is False


@pytest.mark.asyncio
async def test_task_repository_find_by_id_returns_none_for_invalid_uuid_without_db_call():
    assert await TaskRepository().find_by_id("not-a-uuid") is None


@pytest.mark.asyncio
async def test_task_repository_find_all_returns_empty_list_for_invalid_project_uuid_without_db_call():
    assert await TaskRepository().find_all(project_id="not-a-uuid") == []
