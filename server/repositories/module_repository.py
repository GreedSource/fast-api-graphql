import uuid
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from server.db.session import AsyncSessionLocal
from server.decorators.singleton_decorator import singleton
from server.models.orm.module_orm import ModuleORM


@singleton
class ModuleRepository:
    async def create(self, data: dict, session: Optional[AsyncSession] = None) -> ModuleORM:
        if session:
            module = ModuleORM(**data)
            session.add(module)
            await session.commit()
            await session.refresh(module)
            return module
        async with AsyncSessionLocal() as db_session:
            module = ModuleORM(**data)
            db_session.add(module)
            await db_session.commit()
            await db_session.refresh(module)
            return module

    async def find_all(self, session: Optional[AsyncSession] = None) -> List[ModuleORM]:
        stmt = select(ModuleORM).order_by(ModuleORM.name)
        if session:
            res = await session.execute(stmt)
            return list(res.scalars().all())
        async with AsyncSessionLocal() as db_session:
            res = await db_session.execute(stmt)
            return list(res.scalars().all())

    async def find_by_id(
        self, module_id: str | uuid.UUID, session: Optional[AsyncSession] = None
    ) -> Optional[ModuleORM]:
        if isinstance(module_id, str):
            try:
                module_id = uuid.UUID(module_id)
            except ValueError:
                return None
        stmt = select(ModuleORM).where(ModuleORM.id == module_id)
        if session:
            res = await session.execute(stmt)
            return res.scalar_one_or_none()
        async with AsyncSessionLocal() as db_session:
            res = await db_session.execute(stmt)
            return res.scalar_one_or_none()

    async def find_by_key(self, key: str, session: Optional[AsyncSession] = None) -> Optional[ModuleORM]:
        stmt = select(ModuleORM).where(ModuleORM.key == key.lower().strip())
        if session:
            res = await session.execute(stmt)
            return res.scalar_one_or_none()
        async with AsyncSessionLocal() as db_session:
            res = await db_session.execute(stmt)
            return res.scalar_one_or_none()

    async def update(
        self, module_id: str | uuid.UUID, data: dict, session: Optional[AsyncSession] = None
    ) -> Optional[ModuleORM]:
        module = await self.find_by_id(module_id, session=session)
        if not module:
            return None
        for key, val in data.items():
            if hasattr(module, key) and val is not None:
                setattr(module, key, val)
        if session:
            await session.commit()
            await session.refresh(module)
            return module
        async with AsyncSessionLocal() as db_session:
            db_session.add(module)
            await db_session.commit()
            await db_session.refresh(module)
            return module
