from sqlalchemy import select

from server.db.session import AsyncSessionLocal
from server.helpers.logger_helper import LoggerHelper
from server.models.orm.permission_orm import PermissionORM
from server.models.orm.role_orm import RoleORM
from server.seeders.rbac_catalog import DEFAULT_ROLES, role_permission_keys


async def seed():
    async with AsyncSessionLocal() as session:
        roles_res = await session.execute(select(RoleORM))
        roles_map = {role.name: role for role in roles_res.scalars().all()}

        perms_res = await session.execute(select(PermissionORM))
        all_perms = list(perms_res.scalars().all())
        permissions_by_key = {
            f"{permission.module.key}.{permission.action.key}": permission for permission in all_perms
        }

        LoggerHelper.info("Insertando roles semilla en PostgreSQL...")
        for role_data in DEFAULT_ROLES:
            try:
                role = roles_map.get(role_data["name"])
                if role:
                    role.description = role_data["description"]
                    role.active = role_data["active"]
                    LoggerHelper.info(f"Rol existente actualizado: {role_data['name']}")
                else:
                    role = RoleORM(**role_data)
                    session.add(role)
                    roles_map[role_data["name"]] = role

                allowed_permission_keys = role_permission_keys(role_data["name"])
                role.permissions = [
                    permission
                    for permission_key, permission in permissions_by_key.items()
                    if permission_key in allowed_permission_keys
                ]

                await session.commit()
                LoggerHelper.success(f"Rol sembrado: {role_data['name']}")
            except Exception as exc:
                await session.rollback()
                LoggerHelper.warning(f"No se pudo crear rol {role_data['name']}: {exc}")

        LoggerHelper.success("Seeders de roles finalizado.")
