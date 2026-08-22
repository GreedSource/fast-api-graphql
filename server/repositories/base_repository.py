import uuid
from typing import Generic, TypeVar

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from server.db.session import AsyncSessionLocal

ModelT = TypeVar("ModelT")


def parse_uuid(value):
    if isinstance(value, uuid.UUID):
        return value
    try:
        return uuid.UUID(str(value))
    except (ValueError, TypeError, AttributeError):
        return None


class BaseRepository(Generic[ModelT]):
    """CRUD común para entidades SQLAlchemy con una llave primaria `id`."""

    model: type[ModelT]

    async def create(self, data: dict, session: AsyncSession | None = None) -> ModelT:
        instance = self.model(**data)
        if session:
            session.add(instance)
            await session.flush()
            await session.refresh(instance)
            return instance
        async with AsyncSessionLocal() as db:
            db.add(instance)
            await db.commit()
            await db.refresh(instance)
            return instance

    async def find_by_id(self, entity_id, session: AsyncSession | None = None) -> ModelT | None:
        parsed_id = parse_uuid(entity_id)
        if not parsed_id:
            return None
        stmt = select(self.model).where(self.model.id == parsed_id)
        if session:
            return (await session.execute(stmt)).scalar_one_or_none()
        async with AsyncSessionLocal() as db:
            return (await db.execute(stmt)).scalar_one_or_none()

    async def update(self, entity_id, data: dict, session: AsyncSession | None = None) -> ModelT | None:
        instance = await self.find_by_id(entity_id, session)
        if not instance:
            return None
        for key, value in data.items():
            if hasattr(instance, key) and value is not None:
                setattr(instance, key, value)
        if session:
            await session.flush()
            await session.refresh(instance)
            return instance
        async with AsyncSessionLocal() as db:
            db.add(instance)
            await db.commit()
            await db.refresh(instance)
            return instance

    async def delete(self, entity_id, session: AsyncSession | None = None) -> bool:
        parsed_id = parse_uuid(entity_id)
        if not parsed_id:
            return False
        stmt = delete(self.model).where(self.model.id == parsed_id)
        if session:
            result = await session.execute(stmt)
            await session.flush()
            return result.rowcount > 0
        async with AsyncSessionLocal() as db:
            result = await db.execute(stmt)
            await db.commit()
            return result.rowcount > 0
