import uuid
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from server.db.session import AsyncSessionLocal
from server.decorators.singleton_decorator import singleton
from server.models.orm.permission_orm import PermissionORM
from server.repositories.base_repository import BaseRepository


@singleton
class PermissionRepository(BaseRepository[PermissionORM]):
    model = PermissionORM

    async def create(self, data: dict, session: Optional[AsyncSession] = None) -> PermissionORM:
        module_id = uuid.UUID(str(data["module_id"])) if isinstance(data["module_id"], str) else data["module_id"]
        action_id = uuid.UUID(str(data["action_id"])) if isinstance(data["action_id"], str) else data["action_id"]

        perm = PermissionORM(
            module_id=module_id,
            action_id=action_id,
            description=data.get("description"),
        )

        if session:
            session.add(perm)
            await session.commit()
            await session.refresh(perm)
            return perm
        async with AsyncSessionLocal() as db_session:
            db_session.add(perm)
            await db_session.commit()
            await db_session.refresh(perm)
            return perm

    async def find_all(self, session: Optional[AsyncSession] = None) -> List[PermissionORM]:
        stmt = select(PermissionORM).options(joinedload(PermissionORM.module), joinedload(PermissionORM.action))
        if session:
            res = await session.execute(stmt)
            return list(res.scalars().all())
        async with AsyncSessionLocal() as db_session:
            res = await db_session.execute(stmt)
            return list(res.scalars().all())

    async def find_by_module_and_action(
        self,
        module_id: str | uuid.UUID,
        action_id: str | uuid.UUID,
        session: Optional[AsyncSession] = None,
    ) -> Optional[PermissionORM]:
        mod_uuid = uuid.UUID(str(module_id)) if isinstance(module_id, str) else module_id
        act_uuid = uuid.UUID(str(action_id)) if isinstance(action_id, str) else action_id

        stmt = (
            select(PermissionORM)
            .options(joinedload(PermissionORM.module), joinedload(PermissionORM.action))
            .where(PermissionORM.module_id == mod_uuid, PermissionORM.action_id == act_uuid)
        )
        if session:
            res = await session.execute(stmt)
            return res.scalar_one_or_none()
        async with AsyncSessionLocal() as db_session:
            res = await db_session.execute(stmt)
            return res.scalar_one_or_none()

    async def find_by_id(
        self, permission_id: str | uuid.UUID, session: Optional[AsyncSession] = None
    ) -> Optional[PermissionORM]:
        perm_uuid = uuid.UUID(str(permission_id)) if isinstance(permission_id, str) else permission_id
        stmt = (
            select(PermissionORM)
            .options(joinedload(PermissionORM.module), joinedload(PermissionORM.action))
            .where(PermissionORM.id == perm_uuid)
        )
        if session:
            res = await session.execute(stmt)
            return res.scalar_one_or_none()
        async with AsyncSessionLocal() as db_session:
            res = await db_session.execute(stmt)
            return res.scalar_one_or_none()
