from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from server.db.session import AsyncSessionLocal
from server.decorators.singleton_decorator import singleton
from server.models.orm.project_orm import ProjectORM
from server.repositories.base_repository import BaseRepository


@singleton
class ProjectRepository(BaseRepository[ProjectORM]):
    model = ProjectORM

    async def find_all(
        self, include_archived: bool = False, session: Optional[AsyncSession] = None
    ) -> list[ProjectORM]:
        stmt = select(ProjectORM).order_by(ProjectORM.created_at.desc())
        if not include_archived:
            stmt = stmt.where(ProjectORM.archived_at.is_(None))
        if session:
            return list((await session.execute(stmt)).scalars().all())
        async with AsyncSessionLocal() as db:
            return list((await db.execute(stmt)).scalars().all())

    async def archive(self, project_id, session: Optional[AsyncSession] = None) -> ProjectORM | None:
        return await self.update(
            project_id, {"status": "archived", "archived_at": datetime.now(timezone.utc)}, session=session
        )
