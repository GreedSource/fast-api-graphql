from server.helpers.logger_helper import LoggerHelper
from server.helpers.mongo_helper import MongoHelper

DEFAULT_ACTIONS = [
    {"name": "Crear", "key": "create", "description": "Permite crear entidades", "active": True},
    {"name": "Leer", "key": "read", "description": "Permite leer entidades", "active": True},
    {"name": "Actualizar", "key": "update", "description": "Permite actualizar entidades", "active": True},
    {"name": "Eliminar", "key": "delete", "description": "Permite eliminar entidades", "active": True},
]


async def seed(db):
    mongo = MongoHelper(db=db, allowed_collections={"actions"})
    existing = await db["actions"].count_documents({})

    if existing:
        LoggerHelper.info(f"Ya existen {existing} acciones; semilla acciones omitida.")
        return

    LoggerHelper.info("Insertando acciones semilla...")
    for action in DEFAULT_ACTIONS:
        try:
            await mongo.insert_one("actions", action)
            LoggerHelper.success(f"Acción creada: {action['key']}")
        except Exception as exc:
            LoggerHelper.warning(f"No se pudo crear acción {action['key']}: {exc}")

    LoggerHelper.success("Seeders de acciones finalizado")
