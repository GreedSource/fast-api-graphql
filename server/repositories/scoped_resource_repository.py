from typing import Generic, TypeVar

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from server.db.session import AsyncSessionLocal
from server.repositories.base_repository import BaseRepository, parse_uuid

ModelT = TypeVar("ModelT")


class ScopedResourceRepository(BaseRepository[ModelT], Generic[ModelT]):
    """Consultas para recursos con organización, equipo y propietario."""

    async def find_all(self, organization_id, access: dict, session: AsyncSession | None = None) -> list[ModelT]:
        stmt = (
            select(self.model)
            .where(self.model.organization_id == parse_uuid(organization_id))
            .order_by(self.model.created_at.desc())
        )
        if access["scope"] == "OWN":
            stmt = stmt.where(self.model.owner_id == parse_uuid(access["user_id"]))
        elif access["scope"] == "TEAM":
            stmt = stmt.where(self.model.team_id == parse_uuid(access["team_id"]))
        if session:
            return list((await session.execute(stmt)).scalars().all())
        async with AsyncSessionLocal() as db:
            return list((await db.execute(stmt)).scalars().all())
