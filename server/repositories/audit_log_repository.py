from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from server.db.session import AsyncSessionLocal
from server.decorators.singleton_decorator import singleton
from server.models.orm.audit_log_orm import AuditLogORM


@singleton
class AuditLogRepository:
    async def create(self, data: dict, session: Optional[AsyncSession] = None) -> AuditLogORM:
        audit_log = AuditLogORM(**data)
        if session:
            session.add(audit_log)
            await session.commit()
            await session.refresh(audit_log)
            return audit_log
        async with AsyncSessionLocal() as db_session:
            db_session.add(audit_log)
            await db_session.commit()
            await db_session.refresh(audit_log)
            return audit_log

    async def find_all(self, limit: int = 100, session: Optional[AsyncSession] = None) -> List[AuditLogORM]:
        stmt = select(AuditLogORM).order_by(AuditLogORM.created_at.desc()).limit(limit)
        if session:
            res = await session.execute(stmt)
            return list(res.scalars().all())
        async with AsyncSessionLocal() as db_session:
            res = await db_session.execute(stmt)
            return list(res.scalars().all())
