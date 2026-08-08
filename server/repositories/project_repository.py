import uuid
from datetime import datetime, timezone
from typing import List, Optional

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from server.db.session import AsyncSessionLocal
from server.decorators.singleton_decorator import singleton
from server.models.orm.project_orm import ProjectORM


@singleton
class ProjectRepository:
    async def create(self, data: dict, session: Optional[AsyncSession] = None) -> ProjectORM:
        project = ProjectORM(**data)
        if session:
            session.add(project)
            await session.commit()
            await session.refresh(project)
            return project
        async with AsyncSessionLocal() as db_session:
            db_session.add(project)
            await db_session.commit()
            await db_session.refresh(project)
            return project

    async def find_all(
        self,
        include_archived: bool = False,
        session: Optional[AsyncSession] = None,
    ) -> List[ProjectORM]:
        stmt = select(ProjectORM).order_by(ProjectORM.created_at.desc())
        if not include_archived:
            stmt = stmt.where(ProjectORM.archived_at.is_(None))

        if session:
            res = await session.execute(stmt)
            return list(res.scalars().all())
        async with AsyncSessionLocal() as db_session:
            res = await db_session.execute(stmt)
            return list(res.scalars().all())

    async def find_by_id(
        self, project_id: str | uuid.UUID, session: Optional[AsyncSession] = None
    ) -> Optional[ProjectORM]:
        try:
            p_uuid = uuid.UUID(str(project_id)) if isinstance(project_id, str) else project_id
        except ValueError:
            return None

        stmt = select(ProjectORM).where(ProjectORM.id == p_uuid)
        if session:
            res = await session.execute(stmt)
            return res.scalar_one_or_none()
        async with AsyncSessionLocal() as db_session:
            res = await db_session.execute(stmt)
            return res.scalar_one_or_none()

    async def update(
        self, project_id: str | uuid.UUID, update_data: dict, session: Optional[AsyncSession] = None
    ) -> Optional[ProjectORM]:
        project = await self.find_by_id(project_id, session=session)
        if not project:
            return None

        for key, value in update_data.items():
            if hasattr(project, key) and value is not None:
                setattr(project, key, value)

        if session:
            await session.commit()
            await session.refresh(project)
            return project
        async with AsyncSessionLocal() as db_session:
            db_session.add(project)
            await db_session.commit()
            await db_session.refresh(project)
            return project

    async def archive(
        self,
        project_id: str | uuid.UUID,
        session: Optional[AsyncSession] = None,
    ) -> Optional[ProjectORM]:
        return await self.update(
            project_id,
            {
                "status": "archived",
                "archived_at": datetime.now(timezone.utc),
            },
            session=session,
        )

    async def delete(self, project_id: str | uuid.UUID, session: Optional[AsyncSession] = None) -> bool:
        try:
            p_uuid = uuid.UUID(str(project_id)) if isinstance(project_id, str) else project_id
        except ValueError:
            return False

        stmt = delete(ProjectORM).where(ProjectORM.id == p_uuid)
        if session:
            res = await session.execute(stmt)
            await session.commit()
            return res.rowcount > 0
        async with AsyncSessionLocal() as db_session:
            res = await db_session.execute(stmt)
            await db_session.commit()
            return res.rowcount > 0
