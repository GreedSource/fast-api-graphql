from sqlalchemy import select

from server.db.session import AsyncSessionLocal
from server.helpers.logger_helper import LoggerHelper
from server.models.orm.permission_orm import PermissionORM
from server.models.orm.role_orm import RoleORM

DEFAULT_ROLES = [
    {"name": "admin", "description": "Administrador del sistema", "active": True},
    {"name": "user", "description": "Usuario estándar", "active": True},
]


async def seed():
    async with AsyncSessionLocal() as session:
        res = await session.execute(select(RoleORM))
        existing = len(res.scalars().all())

        if existing:
            LoggerHelper.info(f"Ya existen {existing} roles en PostgreSQL; semilla omitida.")
            return

        # Cargar todos los permisos para el rol admin
        perms_res = await session.execute(select(PermissionORM))
        all_perms = list(perms_res.scalars().all())

        LoggerHelper.info("Insertando roles semilla en PostgreSQL...")
        for role_data in DEFAULT_ROLES:
            try:
                role = RoleORM(**role_data)
                if role_data["name"] == "admin":
                    role.permissions = all_perms

                session.add(role)
                await session.commit()
                LoggerHelper.success(f"Rol creado: {role_data['name']}")
            except Exception as exc:
                await session.rollback()
                LoggerHelper.warning(f"No se pudo crear rol {role_data['name']}: {exc}")

        LoggerHelper.success("Seeders de roles finalizado.")
