from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock
from uuid import UUID

import pytest

from server.repositories.base_repository import BaseRepository, parse_uuid

ENTITY_ID = UUID("50000000-0000-0000-0000-000000000001")


class Entity:
    id = SimpleNamespace()

    def __init__(self, **data):
        self.id = data.pop("id", ENTITY_ID)
        for key, value in data.items():
            setattr(self, key, value)


class EntityRepository(BaseRepository[Entity]):
    model = Entity


def fake_session(result=None):
    scalar_result = SimpleNamespace(scalar_one_or_none=MagicMock(return_value=result))
    return SimpleNamespace(
        add=MagicMock(),
        flush=AsyncMock(),
        refresh=AsyncMock(),
        execute=AsyncMock(return_value=scalar_result),
    )


@pytest.mark.asyncio
async def test_base_repository_create_uses_shared_session_without_committing_it():
    repository = EntityRepository()
    session = fake_session()

    entity = await repository.create({"name": "shared"}, session=session)

    assert entity.name == "shared"
    session.add.assert_called_once_with(entity)
    session.flush.assert_awaited_once()
    session.refresh.assert_awaited_once_with(entity)


@pytest.mark.asyncio
async def test_base_repository_find_by_id_rejects_invalid_uuid_without_querying():
    repository = EntityRepository()
    session = fake_session()

    result = await repository.find_by_id("not-a-uuid", session=session)

    assert result is None
    session.execute.assert_not_awaited()


def test_parse_uuid_accepts_uuid_and_string():
    assert parse_uuid(ENTITY_ID) == ENTITY_ID
    assert parse_uuid(str(ENTITY_ID)) == ENTITY_ID
