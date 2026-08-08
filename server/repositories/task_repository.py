import uuid
from datetime import datetime, timezone
from typing import List, Optional

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from server.db.session import AsyncSessionLocal
from server.decorators.singleton_decorator import singleton
from server.models.orm.task_orm import TaskORM


@singleton
class TaskRepository:
    async def create(self, data: dict, session: Optional[AsyncSession] = None) -> TaskORM:
        task = TaskORM(**data)
        if session:
            session.add(task)
            await session.commit()
            await session.refresh(task)
            return task
        async with AsyncSessionLocal() as db_session:
            db_session.add(task)
            await db_session.commit()
            await db_session.refresh(task)
            return task

    async def find_all(
        self, project_id: str | uuid.UUID | None = None, session: Optional[AsyncSession] = None
    ) -> List[TaskORM]:
        stmt = select(TaskORM).order_by(TaskORM.created_at.desc())
        if project_id:
            try:
                p_uuid = uuid.UUID(str(project_id)) if isinstance(project_id, str) else project_id
            except ValueError:
                return []
            stmt = stmt.where(TaskORM.project_id == p_uuid)

        if session:
            res = await session.execute(stmt)
            return list(res.scalars().all())
        async with AsyncSessionLocal() as db_session:
            res = await db_session.execute(stmt)
            return list(res.scalars().all())

    async def find_by_id(self, task_id: str | uuid.UUID, session: Optional[AsyncSession] = None) -> Optional[TaskORM]:
        try:
            t_uuid = uuid.UUID(str(task_id)) if isinstance(task_id, str) else task_id
        except ValueError:
            return None

        stmt = select(TaskORM).where(TaskORM.id == t_uuid)
        if session:
            res = await session.execute(stmt)
            return res.scalar_one_or_none()
        async with AsyncSessionLocal() as db_session:
            res = await db_session.execute(stmt)
            return res.scalar_one_or_none()

    async def update(
        self, task_id: str | uuid.UUID, update_data: dict, session: Optional[AsyncSession] = None
    ) -> Optional[TaskORM]:
        task = await self.find_by_id(task_id, session=session)
        if not task:
            return None

        for key, value in update_data.items():
            if hasattr(task, key) and value is not None:
                setattr(task, key, value)

        if session:
            await session.commit()
            await session.refresh(task)
            return task
        async with AsyncSessionLocal() as db_session:
            db_session.add(task)
            await db_session.commit()
            await db_session.refresh(task)
            return task

    async def complete(self, task_id: str | uuid.UUID, session: Optional[AsyncSession] = None) -> Optional[TaskORM]:
        return await self.update(
            task_id,
            {
                "status": "done",
                "completed_at": datetime.now(timezone.utc),
            },
            session=session,
        )

    async def delete(self, task_id: str | uuid.UUID, session: Optional[AsyncSession] = None) -> bool:
        try:
            t_uuid = uuid.UUID(str(task_id)) if isinstance(task_id, str) else task_id
        except ValueError:
            return False

        stmt = delete(TaskORM).where(TaskORM.id == t_uuid)
        if session:
            res = await session.execute(stmt)
            await session.commit()
            return res.rowcount > 0
        async with AsyncSessionLocal() as db_session:
            res = await db_session.execute(stmt)
            await db_session.commit()
            return res.rowcount > 0
