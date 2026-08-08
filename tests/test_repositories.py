import pytest

from server.repositories.action_repository import ActionRepository
from server.repositories.module_repository import ModuleRepository


@pytest.mark.asyncio
async def test_module_repository_find_by_id_returns_none_for_invalid_uuid_without_db_call():
    assert await ModuleRepository().find_by_id("not-a-uuid") is None


@pytest.mark.asyncio
async def test_action_repository_find_by_id_returns_none_for_invalid_uuid_without_db_call():
    assert await ActionRepository().find_by_id("not-a-uuid") is None
