from sqlalchemy import select

from server.db.session import AsyncSessionLocal
from server.helpers.logger_helper import LoggerHelper
from server.models.orm.action_orm import ActionORM
from server.models.orm.module_orm import ModuleORM
from server.models.orm.permission_orm import PermissionORM
from server.seeders.rbac_catalog import permission_keys


async def seed():
    async with AsyncSessionLocal() as session:
        LoggerHelper.info("Insertando permisos semilla en PostgreSQL...")

        modules_res = await session.execute(select(ModuleORM))
        modules_map = {m.key: m for m in modules_res.scalars().all()}

        actions_res = await session.execute(select(ActionORM))
        actions_map = {a.key: a for a in actions_res.scalars().all()}

        permissions_res = await session.execute(select(PermissionORM))
        existing_pairs = {
            (permission.module_id, permission.action_id) for permission in permissions_res.scalars().all()
        }

        for permission_key in permission_keys():
            module_key, action_key = permission_key.split(".", 1)
            mod = modules_map.get(module_key)
            act = actions_map.get(action_key)

            if not mod or not act:
                LoggerHelper.warning(f"No se encuentra módulo o acción para {module_key}:{action_key}")
                continue

            if (mod.id, act.id) in existing_pairs:
                LoggerHelper.info(f"Permiso existente: {module_key}:{action_key}")
                continue

            try:
                perm = PermissionORM(
                    module_id=mod.id,
                    action_id=act.id,
                    description=f"Permiso {module_key}:{action_key}",
                )
                session.add(perm)
                await session.commit()
                existing_pairs.add((mod.id, act.id))
                LoggerHelper.success(f"Permiso creado: {module_key}:{action_key}")
            except Exception as exc:
                await session.rollback()
                LoggerHelper.warning(f"No se pudo crear permiso {module_key}:{action_key}: {exc}")

        LoggerHelper.success("Seeders de permisos finalizado.")
