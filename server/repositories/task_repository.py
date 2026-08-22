import uuid
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from server.db.session import AsyncSessionLocal
from server.decorators.singleton_decorator import singleton
from server.models.orm.task_orm import TaskORM
from server.repositories.base_repository import BaseRepository, parse_uuid


@singleton
class TaskRepository(BaseRepository[TaskORM]):
    model = TaskORM

    async def find_all(
        self, project_id: str | uuid.UUID | None = None, session: Optional[AsyncSession] = None
    ) -> list[TaskORM]:
        stmt = select(TaskORM).order_by(TaskORM.created_at.desc())
        if project_id:
            project_uuid = parse_uuid(project_id)
            if not project_uuid:
                return []
            stmt = stmt.where(TaskORM.project_id == project_uuid)
        if session:
            return list((await session.execute(stmt)).scalars().all())
        async with AsyncSessionLocal() as db:
            return list((await db.execute(stmt)).scalars().all())

    async def complete(self, task_id, session: Optional[AsyncSession] = None) -> TaskORM | None:
        return await self.update(
            task_id, {"status": "done", "completed_at": datetime.now(timezone.utc)}, session=session
        )
