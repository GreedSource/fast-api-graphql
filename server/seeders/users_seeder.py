from sqlalchemy import select

from server.db.session import AsyncSessionLocal
from server.helpers.logger_helper import LoggerHelper
from server.models.orm.role_orm import RoleORM
from server.models.orm.user_orm import UserORM
from server.utils.auth_utils import hash_password

DEFAULT_USERS = [
    {
        "name": "Admin",
        "lastname": "Root",
        "email": "admin@example.com",
        "password": hash_password("Admin1234!"),
        "role_name": "admin",
    },
    {
        "name": "User",
        "lastname": "Default",
        "email": "user@example.com",
        "password": hash_password("User1234!"),
        "role_name": "user",
    },
]


async def seed():
    async with AsyncSessionLocal() as session:
        res = await session.execute(select(UserORM))
        existing = len(res.scalars().all())

        if existing:
            LoggerHelper.info(f"Ya existen {existing} usuarios en PostgreSQL; semilla omitida.")
            return

        roles_res = await session.execute(select(RoleORM))
        roles_map = {r.name: r for r in roles_res.scalars().all()}

        LoggerHelper.info("Insertando usuarios semilla en PostgreSQL...")
        for u_data in DEFAULT_USERS:
            r_name = u_data.get("role_name")
            role = roles_map.get(r_name)

            try:
                user = UserORM(
                    name=u_data["name"],
                    lastname=u_data["lastname"],
                    email=u_data["email"],
                    password=u_data["password"],
                    role_id=role.id if role else None,
                )
                session.add(user)
                await session.commit()
                LoggerHelper.success(f"Usuario creado: {u_data['email']}")
            except Exception as exc:
                await session.rollback()
                LoggerHelper.warning(f"No se pudo crear usuario {u_data['email']}: {exc}")

        LoggerHelper.success("Seeders de usuarios finalizado.")
