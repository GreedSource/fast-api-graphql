from sqlalchemy import select

from server.db.session import AsyncSessionLocal
from server.decorators.singleton_decorator import singleton
from server.models.orm.crm_team_orm import CRMTeamMemberORM, CRMTeamORM
from server.repositories.base_repository import BaseRepository, parse_uuid


@singleton
class CRMTeamRepository(BaseRepository[CRMTeamORM]):
    model = CRMTeamORM

    async def add_member(self, data: dict):
        async with AsyncSessionLocal() as db:
            instance = CRMTeamMemberORM(**data)
            db.add(instance)
            await db.commit()
            await db.refresh(instance)
            return instance

    async def find_all(self, organization_id):
        stmt = (
            select(CRMTeamORM)
            .where(CRMTeamORM.organization_id == parse_uuid(organization_id))
            .order_by(CRMTeamORM.name)
        )
        async with AsyncSessionLocal() as db:
            return list((await db.execute(stmt)).scalars().all())

    async def find_user_access(self, organization_id, user_id, team_id=None):
        stmt = (
            select(CRMTeamMemberORM)
            .join(CRMTeamORM, CRMTeamORM.id == CRMTeamMemberORM.team_id)
            .where(
                CRMTeamORM.organization_id == parse_uuid(organization_id),
                CRMTeamMemberORM.user_id == parse_uuid(user_id),
            )
        )
        if team_id:
            stmt = stmt.where(CRMTeamMemberORM.team_id == parse_uuid(team_id))
        async with AsyncSessionLocal() as db:
            members = list((await db.execute(stmt)).scalars().all())
        if not members:
            return None
        rank = {"OWN": 1, "TEAM": 2, "ORGANIZATION": 3, "GLOBAL": 4}
        member = max(members, key=lambda item: rank[item.scope])
        return {
            "scope": member.scope,
            "team_id": str(member.team_id),
            "user_id": str(member.user_id),
            "role": member.role,
        }
