import uuid
from typing import List, Optional

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from server.db.session import AsyncSessionLocal
from server.decorators.singleton_decorator import singleton
from server.models.orm.permission_orm import PermissionORM
from server.models.orm.role_orm import RoleORM


@singleton
class RoleRepository:
    async def create(self, role_data: dict, session: Optional[AsyncSession] = None) -> RoleORM:
        role = RoleORM(**role_data)
        if session:
            session.add(role)
            await session.commit()
            await session.refresh(role)
            return role
        async with AsyncSessionLocal() as db_session:
            db_session.add(role)
            await db_session.commit()
            await db_session.refresh(role)
            return role

    async def find_by_id(self, role_id: str | uuid.UUID, session: Optional[AsyncSession] = None) -> Optional[RoleORM]:
        r_uuid = uuid.UUID(str(role_id)) if isinstance(role_id, str) else role_id
        stmt = (
            select(RoleORM)
            .options(
                selectinload(RoleORM.permissions).selectinload(PermissionORM.module),
                selectinload(RoleORM.permissions).selectinload(PermissionORM.action),
            )
            .where(RoleORM.id == r_uuid)
        )
        if session:
            res = await session.execute(stmt)
            return res.scalar_one_or_none()
        async with AsyncSessionLocal() as db_session:
            res = await db_session.execute(stmt)
            return res.scalar_one_or_none()

    async def find_by_name(self, name: str, session: Optional[AsyncSession] = None) -> Optional[RoleORM]:
        stmt = (
            select(RoleORM)
            .options(
                selectinload(RoleORM.permissions).selectinload(PermissionORM.module),
                selectinload(RoleORM.permissions).selectinload(PermissionORM.action),
            )
            .where(RoleORM.name == name.strip())
        )
        if session:
            res = await session.execute(stmt)
            return res.scalar_one_or_none()
        async with AsyncSessionLocal() as db_session:
            res = await db_session.execute(stmt)
            return res.scalar_one_or_none()

    async def find_all(self, session: Optional[AsyncSession] = None) -> List[RoleORM]:
        stmt = (
            select(RoleORM)
            .options(
                selectinload(RoleORM.permissions).selectinload(PermissionORM.module),
                selectinload(RoleORM.permissions).selectinload(PermissionORM.action),
            )
            .order_by(RoleORM.name)
        )
        if session:
            res = await session.execute(stmt)
            return list(res.scalars().all())
        async with AsyncSessionLocal() as db_session:
            res = await db_session.execute(stmt)
            return list(res.scalars().all())

    async def update(
        self, role_id: str | uuid.UUID, update_data: dict, session: Optional[AsyncSession] = None
    ) -> Optional[RoleORM]:
        role = await self.find_by_id(role_id, session=session)
        if not role:
            return None
        for key, val in update_data.items():
            if hasattr(role, key) and val is not None:
                setattr(role, key, val)
        if session:
            await session.commit()
            await session.refresh(role)
            return role
        async with AsyncSessionLocal() as db_session:
            db_session.add(role)
            await db_session.commit()
            await db_session.refresh(role)
            return role

    async def assign_permissions(
        self,
        role_id: str | uuid.UUID,
        permission_ids: list[str | uuid.UUID],
        session: Optional[AsyncSession] = None,
    ) -> Optional[RoleORM]:
        r_uuid = uuid.UUID(str(role_id)) if isinstance(role_id, str) else role_id
        p_uuids = [uuid.UUID(str(pid)) if isinstance(pid, str) else pid for pid in permission_ids]

        async def _assign(s: AsyncSession):
            stmt_role = select(RoleORM).options(selectinload(RoleORM.permissions)).where(RoleORM.id == r_uuid)
            res_role = await s.execute(stmt_role)
            role = res_role.scalar_one_or_none()
            if not role:
                return None

            stmt_perms = select(PermissionORM).where(PermissionORM.id.in_(p_uuids))
            res_perms = await s.execute(stmt_perms)
            perms = list(res_perms.scalars().all())

            role.permissions = perms
            await s.commit()
            await s.refresh(role)
            return role

        if session:
            return await _assign(session)
        async with AsyncSessionLocal() as db_session:
            return await _assign(db_session)

    async def add_permissions(
        self,
        role_id: str | uuid.UUID,
        permission_ids: list[str | uuid.UUID],
        session: Optional[AsyncSession] = None,
    ) -> Optional[RoleORM]:
        return await self._update_permissions(role_id, permission_ids, mode="add", session=session)

    async def remove_permissions(
        self,
        role_id: str | uuid.UUID,
        permission_ids: list[str | uuid.UUID],
        session: Optional[AsyncSession] = None,
    ) -> Optional[RoleORM]:
        return await self._update_permissions(role_id, permission_ids, mode="remove", session=session)

    async def _update_permissions(
        self,
        role_id: str | uuid.UUID,
        permission_ids: list[str | uuid.UUID],
        mode: str,
        session: Optional[AsyncSession] = None,
    ) -> Optional[RoleORM]:
        r_uuid = uuid.UUID(str(role_id)) if isinstance(role_id, str) else role_id
        p_uuids = {uuid.UUID(str(pid)) if isinstance(pid, str) else pid for pid in permission_ids}

        async def _update(s: AsyncSession):
            stmt_role = select(RoleORM).options(selectinload(RoleORM.permissions)).where(RoleORM.id == r_uuid)
            res_role = await s.execute(stmt_role)
            role = res_role.scalar_one_or_none()
            if not role:
                return None

            current_by_id = {permission.id: permission for permission in role.permissions}

            if mode == "add":
                missing_ids = p_uuids.difference(current_by_id)
                if missing_ids:
                    stmt_perms = select(PermissionORM).where(PermissionORM.id.in_(missing_ids))
                    res_perms = await s.execute(stmt_perms)
                    for permission in res_perms.scalars().all():
                        current_by_id[permission.id] = permission
            else:
                for permission_id in p_uuids:
                    current_by_id.pop(permission_id, None)

            role.permissions = list(current_by_id.values())
            await s.commit()
            await s.refresh(role)
            return role

        if session:
            return await _update(session)
        async with AsyncSessionLocal() as db_session:
            return await _update(db_session)

    async def delete(self, role_id: str | uuid.UUID, session: Optional[AsyncSession] = None) -> bool:
        r_uuid = uuid.UUID(str(role_id)) if isinstance(role_id, str) else role_id
        stmt = delete(RoleORM).where(RoleORM.id == r_uuid)
        if session:
            res = await session.execute(stmt)
            await session.commit()
            return res.rowcount > 0
        async with AsyncSessionLocal() as db_session:
            res = await db_session.execute(stmt)
            await db_session.commit()
            return res.rowcount > 0
