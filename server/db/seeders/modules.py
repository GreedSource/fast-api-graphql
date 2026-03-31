from server.helpers.logger_helper import LoggerHelper
from server.helpers.mongo_helper import MongoHelper

DEFAULT_MODULES = [
    {"name": "Usuarios", "key": "users", "description": "Gestión de usuarios", "active": True},
    {"name": "Roles", "key": "roles", "description": "Gestión de roles", "active": True},
    {"name": "Permisos", "key": "permissions", "description": "Gestión de permisos", "active": True},
    {"name": "Módulos", "key": "modules", "description": "Activar módulos", "active": True},
    {"name": "Acciones", "key": "actions", "description": "Gestión de acciones", "active": True},
]


async def seed(db):
    mongo = MongoHelper(db=db, allowed_collections={"modules"})
    existing = await db["modules"].count_documents({})

    if existing:
        LoggerHelper.info(f"Ya existen {existing} módulos; semilla módulos omitida.")
        return

    LoggerHelper.info("Insertando módulos semilla...")
    for module in DEFAULT_MODULES:
        try:
            await mongo.insert_one("modules", module)
            LoggerHelper.success(f"Módulo creado: {module['key']}")
        except Exception as exc:
            LoggerHelper.warning(f"No se pudo crear módulo {module['key']}: {exc}")

    LoggerHelper.success("Seeders de módulos finalizado")
