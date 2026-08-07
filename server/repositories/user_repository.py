import uuid
from typing import List, Optional

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from server.db.session import AsyncSessionLocal
from server.decorators.singleton_decorator import singleton
from server.models.orm.permission_orm import PermissionORM
from server.models.orm.role_orm import RoleORM
from server.models.orm.user_orm import UserORM


@singleton
class UserRepository:
    async def create(self, user_data: dict, session: Optional[AsyncSession] = None) -> UserORM:
        data = dict(user_data)
        if "role_id" in data and isinstance(data["role_id"], str):
            data["role_id"] = uuid.UUID(data["role_id"])

        user = UserORM(**data)
        if session:
            session.add(user)
            await session.commit()
            await session.refresh(user)
            return user
        async with AsyncSessionLocal() as db_session:
            db_session.add(user)
            await db_session.commit()
            await db_session.refresh(user)
            return user

    async def find_by_email(self, email: str, session: Optional[AsyncSession] = None) -> Optional[UserORM]:
        stmt = (
            select(UserORM)
            .options(
                joinedload(UserORM.role).selectinload(RoleORM.permissions).selectinload(PermissionORM.module),
                joinedload(UserORM.role).selectinload(RoleORM.permissions).selectinload(PermissionORM.action),
            )
            .where(UserORM.email == email.strip().lower())
        )
        if session:
            res = await session.execute(stmt)
            return res.scalar_one_or_none()
        async with AsyncSessionLocal() as db_session:
            res = await db_session.execute(stmt)
            return res.scalar_one_or_none()

    async def find_by_id(self, user_id: str | uuid.UUID, session: Optional[AsyncSession] = None) -> Optional[UserORM]:
        u_uuid = uuid.UUID(str(user_id)) if isinstance(user_id, str) else user_id
        stmt = (
            select(UserORM)
            .options(
                joinedload(UserORM.role).selectinload(RoleORM.permissions).selectinload(PermissionORM.module),
                joinedload(UserORM.role).selectinload(RoleORM.permissions).selectinload(PermissionORM.action),
            )
            .where(UserORM.id == u_uuid)
        )
        if session:
            res = await session.execute(stmt)
            return res.scalar_one_or_none()
        async with AsyncSessionLocal() as db_session:
            res = await db_session.execute(stmt)
            return res.scalar_one_or_none()

    async def find_all(self, session: Optional[AsyncSession] = None) -> List[UserORM]:
        stmt = select(UserORM).options(joinedload(UserORM.role)).order_by(UserORM.name)
        if session:
            res = await session.execute(stmt)
            return list(res.scalars().all())
        async with AsyncSessionLocal() as db_session:
            res = await db_session.execute(stmt)
            return list(res.scalars().all())

    async def aggregate_users_with_roles(self, session: Optional[AsyncSession] = None) -> List[dict]:
        users = await self.find_all(session=session)
        result = []
        for u in users:
            result.append(
                {
                    "_id": str(u.id),
                    "id": str(u.id),
                    "name": u.name,
                    "lastname": u.lastname,
                    "email": u.email,
                    "role": (
                        {
                            "_id": str(u.role.id),
                            "id": str(u.role.id),
                            "name": u.role.name,
                            "description": u.role.description,
                            "active": u.role.active,
                            "permissions": [],
                        }
                        if u.role
                        else None
                    ),
                }
            )
        return result

    async def aggregate_user_with_role(
        self, user_id: str | uuid.UUID, session: Optional[AsyncSession] = None
    ) -> Optional[dict]:
        user = await self.find_by_id(user_id, session=session)
        if not user:
            return None
        return {
            "_id": str(user.id),
            "id": str(user.id),
            "name": user.name,
            "lastname": user.lastname,
            "email": user.email,
            "role": (
                {
                    "_id": str(user.role.id),
                    "id": str(user.role.id),
                    "name": user.role.name,
                    "description": user.role.description,
                    "active": True,
                    "permissions": [],
                }
                if user.role
                else None
            ),
        }

    async def aggregate_user_with_role_permissions(
        self, user_id: str | uuid.UUID, session: Optional[AsyncSession] = None
    ) -> Optional[dict]:
        user = await self.find_by_id(user_id, session=session)
        if not user:
            return None

        mapped_permissions = []
        if user.role and user.role.permissions:
            for p in user.role.permissions:
                if p.module and p.action:
                    mapped_permissions.append({"type": p.module.key, "action": p.action.key})

        return {
            "_id": str(user.id),
            "id": str(user.id),
            "name": user.name,
            "lastname": user.lastname,
            "email": user.email,
            "role": (
                {
                    "_id": str(user.role.id),
                    "id": str(user.role.id),
                    "name": user.role.name,
                    "description": user.role.description,
                    "active": user.role.active,
                    "permissions": mapped_permissions,
                }
                if user.role
                else None
            ),
        }

    async def update(
        self, user_id: str | uuid.UUID, update_data: dict, session: Optional[AsyncSession] = None
    ) -> Optional[UserORM]:
        user = await self.find_by_id(user_id, session=session)
        if not user:
            return None

        data = dict(update_data)
        if "role_id" in data and isinstance(data["role_id"], str):
            data["role_id"] = uuid.UUID(data["role_id"])

        for key, val in data.items():
            if hasattr(user, key) and val is not None:
                setattr(user, key, val)

        if session:
            await session.commit()
            await session.refresh(user)
            return user
        async with AsyncSessionLocal() as db_session:
            db_session.add(user)
            await db_session.commit()
            await db_session.refresh(user)
            return user

    async def delete(self, user_id: str | uuid.UUID, session: Optional[AsyncSession] = None) -> bool:
        u_uuid = uuid.UUID(str(user_id)) if isinstance(user_id, str) else user_id
        stmt = delete(UserORM).where(UserORM.id == u_uuid)
        if session:
            res = await session.execute(stmt)
            await session.commit()
            return res.rowcount > 0
        async with AsyncSessionLocal() as db_session:
            res = await db_session.execute(stmt)
            await db_session.commit()
            return res.rowcount > 0
