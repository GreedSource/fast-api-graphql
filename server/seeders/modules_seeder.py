from sqlalchemy import select

from server.db.session import AsyncSessionLocal
from server.helpers.logger_helper import LoggerHelper
from server.models.orm.module_orm import ModuleORM

DEFAULT_MODULES = [
    {"name": "Usuarios", "key": "users", "description": "Gestión de usuarios", "active": True},
    {"name": "Roles", "key": "roles", "description": "Gestión de roles", "active": True},
    {"name": "Permisos", "key": "permissions", "description": "Gestión de permisos", "active": True},
    {"name": "Módulos", "key": "modules", "description": "Activar módulos", "active": True},
    {"name": "Acciones", "key": "actions", "description": "Gestión de acciones", "active": True},
]


async def seed():
    async with AsyncSessionLocal() as session:
        res = await session.execute(select(ModuleORM))
        existing = len(res.scalars().all())

        if existing:
            LoggerHelper.info(f"Ya existen {existing} módulos en PostgreSQL; semilla omitida.")
            return

        LoggerHelper.info("Insertando módulos semilla en PostgreSQL...")
        for mod_data in DEFAULT_MODULES:
            try:
                module = ModuleORM(**mod_data)
                session.add(module)
                await session.commit()
                LoggerHelper.success(f"Módulo creado: {mod_data['key']}")
            except Exception as exc:
                await session.rollback()
                LoggerHelper.warning(f"No se pudo crear módulo {mod_data['key']}: {exc}")

        LoggerHelper.success("Seeders de módulos finalizado.")
