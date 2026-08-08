from sqlalchemy import select

from server.db.session import AsyncSessionLocal
from server.helpers.logger_helper import LoggerHelper
from server.models.orm.module_orm import ModuleORM
from server.seeders.rbac_catalog import DEFAULT_MODULES


async def seed():
    async with AsyncSessionLocal() as session:
        res = await session.execute(select(ModuleORM.key))
        existing_keys = set(res.scalars().all())

        LoggerHelper.info("Insertando módulos semilla en PostgreSQL...")
        for mod_data in DEFAULT_MODULES:
            if mod_data["key"] in existing_keys:
                LoggerHelper.info(f"Módulo existente: {mod_data['key']}")
                continue

            try:
                module = ModuleORM(**mod_data)
                session.add(module)
                await session.commit()
                existing_keys.add(mod_data["key"])
                LoggerHelper.success(f"Módulo creado: {mod_data['key']}")
            except Exception as exc:
                await session.rollback()
                LoggerHelper.warning(f"No se pudo crear módulo {mod_data['key']}: {exc}")

        LoggerHelper.success("Seeders de módulos finalizado.")
