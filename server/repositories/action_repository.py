import uuid
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from server.db.session import AsyncSessionLocal
from server.decorators.singleton_decorator import singleton
from server.models.orm.action_orm import ActionORM


@singleton
class ActionRepository:
    async def create(self, data: dict, session: Optional[AsyncSession] = None) -> ActionORM:
        if session:
            action = ActionORM(**data)
            session.add(action)
            await session.commit()
            await session.refresh(action)
            return action
        async with AsyncSessionLocal() as db_session:
            action = ActionORM(**data)
            db_session.add(action)
            await db_session.commit()
            await db_session.refresh(action)
            return action

    async def find_all(self, session: Optional[AsyncSession] = None) -> List[ActionORM]:
        stmt = select(ActionORM).order_by(ActionORM.name)
        if session:
            res = await session.execute(stmt)
            return list(res.scalars().all())
        async with AsyncSessionLocal() as db_session:
            res = await db_session.execute(stmt)
            return list(res.scalars().all())

    async def find_by_id(
        self, action_id: str | uuid.UUID, session: Optional[AsyncSession] = None
    ) -> Optional[ActionORM]:
        if isinstance(action_id, str):
            try:
                action_id = uuid.UUID(action_id)
            except ValueError:
                return None
        stmt = select(ActionORM).where(ActionORM.id == action_id)
        if session:
            res = await session.execute(stmt)
            return res.scalar_one_or_none()
        async with AsyncSessionLocal() as db_session:
            res = await db_session.execute(stmt)
            return res.scalar_one_or_none()

    async def find_by_key(self, key: str, session: Optional[AsyncSession] = None) -> Optional[ActionORM]:
        stmt = select(ActionORM).where(ActionORM.key == key.lower().strip())
        if session:
            res = await session.execute(stmt)
            return res.scalar_one_or_none()
        async with AsyncSessionLocal() as db_session:
            res = await db_session.execute(stmt)
            return res.scalar_one_or_none()
