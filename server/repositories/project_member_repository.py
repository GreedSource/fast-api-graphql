import uuid
from typing import List, Optional

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from server.db.session import AsyncSessionLocal
from server.decorators.singleton_decorator import singleton
from server.models.orm.permission_orm import PermissionORM
from server.models.orm.project_member_orm import ProjectMemberORM
from server.models.orm.project_role_orm import ProjectRoleORM


@singleton
class ProjectMemberRepository:
    async def create(self, data: dict, session: Optional[AsyncSession] = None) -> ProjectMemberORM:
        member = ProjectMemberORM(**data)
        if session:
            session.add(member)
            await session.commit()
            await session.refresh(member)
            return member
        async with AsyncSessionLocal() as db_session:
            db_session.add(member)
            await db_session.commit()
            await db_session.refresh(member)
            return member

    async def find_by_project_and_user(
        self,
        project_id: str | uuid.UUID,
        user_id: str | uuid.UUID,
        session: Optional[AsyncSession] = None,
    ) -> Optional[ProjectMemberORM]:
        try:
            p_uuid = uuid.UUID(str(project_id)) if isinstance(project_id, str) else project_id
            u_uuid = uuid.UUID(str(user_id)) if isinstance(user_id, str) else user_id
        except ValueError:
            return None

        stmt = (
            select(ProjectMemberORM)
            .options(
                selectinload(ProjectMemberORM.project_role)
                .selectinload(ProjectRoleORM.permissions)
                .selectinload(PermissionORM.module),
                selectinload(ProjectMemberORM.project_role)
                .selectinload(ProjectRoleORM.permissions)
                .selectinload(PermissionORM.action),
            )
            .where(ProjectMemberORM.project_id == p_uuid, ProjectMemberORM.user_id == u_uuid)
        )
        if session:
            res = await session.execute(stmt)
            return res.scalar_one_or_none()
        async with AsyncSessionLocal() as db_session:
            res = await db_session.execute(stmt)
            return res.scalar_one_or_none()

    async def find_by_project(
        self, project_id: str | uuid.UUID, session: Optional[AsyncSession] = None
    ) -> List[ProjectMemberORM]:
        try:
            p_uuid = uuid.UUID(str(project_id)) if isinstance(project_id, str) else project_id
        except ValueError:
            return []

        stmt = (
            select(ProjectMemberORM)
            .options(
                selectinload(ProjectMemberORM.project_role)
                .selectinload(ProjectRoleORM.permissions)
                .selectinload(PermissionORM.module),
                selectinload(ProjectMemberORM.project_role)
                .selectinload(ProjectRoleORM.permissions)
                .selectinload(PermissionORM.action),
            )
            .where(ProjectMemberORM.project_id == p_uuid)
            .order_by(ProjectMemberORM.created_at.desc())
        )
        if session:
            res = await session.execute(stmt)
            return list(res.scalars().all())
        async with AsyncSessionLocal() as db_session:
            res = await db_session.execute(stmt)
            return list(res.scalars().all())

    async def update_role(
        self,
        member_id: str | uuid.UUID,
        project_role_id: str | uuid.UUID,
        session: Optional[AsyncSession] = None,
    ) -> Optional[ProjectMemberORM]:
        try:
            m_uuid = uuid.UUID(str(member_id)) if isinstance(member_id, str) else member_id
            r_uuid = uuid.UUID(str(project_role_id)) if isinstance(project_role_id, str) else project_role_id
        except ValueError:
            return None

        stmt = select(ProjectMemberORM).where(ProjectMemberORM.id == m_uuid)

        if session:
            res = await session.execute(stmt)
            member = res.scalar_one_or_none()
            if not member:
                return None
            member.project_role_id = r_uuid
            await session.commit()
            await session.refresh(member)
            return member

        async with AsyncSessionLocal() as db_session:
            res = await db_session.execute(stmt)
            member = res.scalar_one_or_none()
            if not member:
                return None
            member.project_role_id = r_uuid
            await db_session.commit()
            await db_session.refresh(member)
            return member

    async def delete(self, member_id: str | uuid.UUID, session: Optional[AsyncSession] = None) -> bool:
        try:
            m_uuid = uuid.UUID(str(member_id)) if isinstance(member_id, str) else member_id
        except ValueError:
            return False

        stmt = delete(ProjectMemberORM).where(ProjectMemberORM.id == m_uuid)
        if session:
            res = await session.execute(stmt)
            await session.commit()
            return res.rowcount > 0
        async with AsyncSessionLocal() as db_session:
            res = await db_session.execute(stmt)
            await db_session.commit()
            return res.rowcount > 0

    async def find_project_role_by_id(
        self, project_role_id: str | uuid.UUID, session: Optional[AsyncSession] = None
    ) -> Optional[ProjectRoleORM]:
        try:
            r_uuid = uuid.UUID(str(project_role_id)) if isinstance(project_role_id, str) else project_role_id
        except ValueError:
            return None

        stmt = select(ProjectRoleORM).where(ProjectRoleORM.id == r_uuid)
        if session:
            res = await session.execute(stmt)
            return res.scalar_one_or_none()
        async with AsyncSessionLocal() as db_session:
            res = await db_session.execute(stmt)
            return res.scalar_one_or_none()
