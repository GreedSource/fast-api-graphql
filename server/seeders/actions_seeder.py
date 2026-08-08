from sqlalchemy import select

from server.db.session import AsyncSessionLocal
from server.helpers.logger_helper import LoggerHelper
from server.models.orm.action_orm import ActionORM
from server.seeders.rbac_catalog import DEFAULT_ACTIONS


async def seed():
    async with AsyncSessionLocal() as session:
        res = await session.execute(select(ActionORM.key))
        existing_keys = set(res.scalars().all())

        LoggerHelper.info("Insertando acciones semilla en PostgreSQL...")
        for act_data in DEFAULT_ACTIONS:
            if act_data["key"] in existing_keys:
                LoggerHelper.info(f"Acción existente: {act_data['key']}")
                continue

            try:
                action = ActionORM(**act_data)
                session.add(action)
                await session.commit()
                existing_keys.add(act_data["key"])
                LoggerHelper.success(f"Acción creada: {act_data['key']}")
            except Exception as exc:
                await session.rollback()
                LoggerHelper.warning(f"No se pudo crear acción {act_data['key']}: {exc}")

        LoggerHelper.success("Seeders de acciones finalizado.")
