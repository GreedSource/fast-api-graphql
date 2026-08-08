import pytest

from server.repositories.project_member_repository import ProjectMemberRepository


@pytest.mark.asyncio
async def test_project_member_repository_find_by_project_returns_empty_for_invalid_uuid_without_db_call():
    assert await ProjectMemberRepository().find_by_project("not-a-uuid") == []


@pytest.mark.asyncio
async def test_project_member_repository_delete_returns_false_for_invalid_uuid_without_db_call():
    assert await ProjectMemberRepository().delete("not-a-uuid") is False
