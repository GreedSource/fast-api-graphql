from server.helpers.logger_helper import LoggerHelper
from server.helpers.mongo_helper import MongoHelper

DEFAULT_ROLE_PERMISSIONS = [
    {"module_key": "users", "action_key": "create"},
    {"module_key": "users", "action_key": "read"},
    {"module_key": "users", "action_key": "update"},
    {"module_key": "users", "action_key": "delete"},
    {"module_key": "roles", "action_key": "read"},
    {"module_key": "permissions", "action_key": "read"},
    {"module_key": "modules", "action_key": "read"},
    {"module_key": "actions", "action_key": "read"},
]


async def seed(db):
    mongo = MongoHelper(db=db, allowed_collections={"permissions", "modules", "actions"})
    existing = await db["permissions"].count_documents({})

    if existing:
        LoggerHelper.info(f"Ya existen {existing} permisos; semilla permisos omitida.")
        return

    LoggerHelper.info("Insertando permisos semilla...")

    modules = {m["key"]: m for m in await db["modules"].find({}, {"_id": 1, "key": 1}).to_list(length=1000)}
    actions = {a["key"]: a for a in await db["actions"].find({}, {"_id": 1, "key": 1}).to_list(length=1000)}

    for item in DEFAULT_ROLE_PERMISSIONS:
        module = modules.get(item["module_key"])
        action = actions.get(item["action_key"])

        if not module or not action:
            LoggerHelper.warning(
                f"No se encuentra módulo o acción para permiso {item['module_key']}:{item['action_key']}"
            )
            continue

        document = {
            "module_id": module["_id"],
            "action_id": action["_id"],
            "description": f"Permiso {item['module_key']}:{item['action_key']}",
        }

        try:
            await mongo.insert_one("permissions", document)
            LoggerHelper.success(f"Permiso creado: {item['module_key']}:{item['action_key']}")
        except Exception as exc:
            LoggerHelper.warning(f"No se pudo crear permiso {item['module_key']}:{item['action_key']}: {exc}")

    LoggerHelper.success("Seeders de permisos finalizado")
