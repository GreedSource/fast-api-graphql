from sqlalchemy import select

from server.db.session import AsyncSessionLocal
from server.decorators.singleton_decorator import singleton
from server.models.orm.crm_organization_orm import CRMOrganizationORM
from server.repositories.base_repository import BaseRepository


@singleton
class CRMOrganizationRepository(BaseRepository[CRMOrganizationORM]):
    model = CRMOrganizationORM

    async def find_all(self):
        stmt = select(CRMOrganizationORM).order_by(CRMOrganizationORM.name)
        async with AsyncSessionLocal() as db:
            return list((await db.execute(stmt)).scalars().all())
