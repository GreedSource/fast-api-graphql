from sqlalchemy import select

from server.db.session import AsyncSessionLocal
from server.helpers.logger_helper import LoggerHelper
from server.models.orm.action_orm import ActionORM
from server.models.orm.module_orm import ModuleORM
from server.models.orm.permission_orm import PermissionORM

DEFAULT_ROLE_PERMISSIONS = [
    # Users
    {"module_key": "users", "action_key": "create"},
    {"module_key": "users", "action_key": "read"},
    {"module_key": "users", "action_key": "update"},
    {"module_key": "users", "action_key": "delete"},
    # Roles
    {"module_key": "roles", "action_key": "create"},
    {"module_key": "roles", "action_key": "read"},
    {"module_key": "roles", "action_key": "update"},
    {"module_key": "roles", "action_key": "delete"},
    # Permissions
    {"module_key": "permissions", "action_key": "read"},
    {"module_key": "permissions", "action_key": "create"},
    {"module_key": "permissions", "action_key": "delete"},
    # Modules
    {"module_key": "modules", "action_key": "read"},
    {"module_key": "modules", "action_key": "create"},
    {"module_key": "modules", "action_key": "update"},
    # Actions
    {"module_key": "actions", "action_key": "read"},
    {"module_key": "actions", "action_key": "create"},
]


async def seed():
    async with AsyncSessionLocal() as session:
        res = await session.execute(select(PermissionORM))
        existing = len(res.scalars().all())

        if existing:
            LoggerHelper.info(f"Ya existen {existing} permisos en PostgreSQL; semilla omitida.")
            return

        LoggerHelper.info("Insertando permisos semilla en PostgreSQL...")

        modules_res = await session.execute(select(ModuleORM))
        modules_map = {m.key: m for m in modules_res.scalars().all()}

        actions_res = await session.execute(select(ActionORM))
        actions_map = {a.key: a for a in actions_res.scalars().all()}

        for item in DEFAULT_ROLE_PERMISSIONS:
            mod = modules_map.get(item["module_key"])
            act = actions_map.get(item["action_key"])

            if not mod or not act:
                LoggerHelper.warning(f"No se encuentra módulo o acción para {item['module_key']}:{item['action_key']}")
                continue

            try:
                perm = PermissionORM(
                    module_id=mod.id,
                    action_id=act.id,
                    description=f"Permiso {item['module_key']}:{item['action_key']}",
                )
                session.add(perm)
                await session.commit()
                LoggerHelper.success(f"Permiso creado: {item['module_key']}:{item['action_key']}")
            except Exception as exc:
                await session.rollback()
                LoggerHelper.warning(f"No se pudo crear permiso {item['module_key']}:{item['action_key']}: {exc}")

        LoggerHelper.success("Seeders de permisos finalizado.")
