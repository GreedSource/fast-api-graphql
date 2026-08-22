from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from server.db.session import AsyncSessionLocal
from server.decorators.singleton_decorator import singleton
from server.models.orm.module_orm import ModuleORM
from server.repositories.base_repository import BaseRepository


@singleton
class ModuleRepository(BaseRepository[ModuleORM]):
    model = ModuleORM

    async def find_all(self, session: Optional[AsyncSession] = None) -> list[ModuleORM]:
        stmt = select(ModuleORM).order_by(ModuleORM.name)
        if session:
            return list((await session.execute(stmt)).scalars().all())
        async with AsyncSessionLocal() as db:
            return list((await db.execute(stmt)).scalars().all())

    async def find_by_key(self, key: str, session: Optional[AsyncSession] = None) -> ModuleORM | None:
        stmt = select(ModuleORM).where(ModuleORM.key == key.lower().strip())
        if session:
            return (await session.execute(stmt)).scalar_one_or_none()
        async with AsyncSessionLocal() as db:
            return (await db.execute(stmt)).scalar_one_or_none()
