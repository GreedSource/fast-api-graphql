from server.helpers.logger_helper import LoggerHelper
from server.helpers.mongo_helper import MongoHelper

DEFAULT_ROLES = [
    {"name": "admin", "description": "Administrador del sistema", "active": True, "permissions": []},
    {"name": "user", "description": "Usuario estándar", "active": True, "permissions": []},
]


async def seed(db):
    mongo = MongoHelper(db=db, allowed_collections={"roles"})
    existing = await db["roles"].count_documents({})

    if existing:
        LoggerHelper.info(f"Ya existen {existing} roles; semilla roles omitida.")
        return

    # Asignamos permisos admin (all permissions) si están disponibles
    permissions = await db["permissions"].find({}, {"_id": 1}).to_list(length=1000)
    permission_ids = [p["_id"] for p in permissions]

    LoggerHelper.info("Insertando roles semilla...")
    for role in DEFAULT_ROLES:
        role_payload = role.copy()

        if role_payload["name"] == "admin":
            role_payload["permissions"] = permission_ids

        try:
            await mongo.insert_one("roles", role_payload)
            LoggerHelper.success(f"Role creado: {role_payload['name']}")
        except Exception as exc:
            LoggerHelper.warning(f"No se pudo crear role {role_payload['name']}: {exc}")

    LoggerHelper.success("Seeders de roles finalizado")
