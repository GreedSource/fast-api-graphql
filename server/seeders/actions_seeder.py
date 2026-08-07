from sqlalchemy import select

from server.db.session import AsyncSessionLocal
from server.helpers.logger_helper import LoggerHelper
from server.models.orm.action_orm import ActionORM

DEFAULT_ACTIONS = [
    {"name": "Crear", "key": "create", "description": "Permite crear entidades", "active": True},
    {"name": "Leer", "key": "read", "description": "Permite leer entidades", "active": True},
    {"name": "Actualizar", "key": "update", "description": "Permite actualizar entidades", "active": True},
    {"name": "Eliminar", "key": "delete", "description": "Permite eliminar entidades", "active": True},
]


async def seed():
    async with AsyncSessionLocal() as session:
        res = await session.execute(select(ActionORM))
        existing = len(res.scalars().all())

        if existing:
            LoggerHelper.info(f"Ya existen {existing} acciones en PostgreSQL; semilla omitida.")
            return

        LoggerHelper.info("Insertando acciones semilla en PostgreSQL...")
        for act_data in DEFAULT_ACTIONS:
            try:
                action = ActionORM(**act_data)
                session.add(action)
                await session.commit()
                LoggerHelper.success(f"Acción creada: {act_data['key']}")
            except Exception as exc:
                await session.rollback()
                LoggerHelper.warning(f"No se pudo crear acción {act_data['key']}: {exc}")

        LoggerHelper.success("Seeders de acciones finalizado.")
