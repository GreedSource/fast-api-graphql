from server.helpers.logger_helper import LoggerHelper
from server.helpers.mongo_helper import MongoHelper
from server.utils.auth_utils import hash_password

DEFAULT_USERS = [
    {
        "name": "Admin",
        "lastname": "Root",
        "email": "admin@example.com",
        "password": hash_password("Admin1234!"),
        "role_name": "admin",
        "active": True,
    },
    {
        "name": "User",
        "lastname": "Default",
        "email": "user@example.com",
        "password": hash_password("User1234!"),
        "role_name": "user",
        "active": True,
    },
]


async def seed(db):
    mongo = MongoHelper(db=db, allowed_collections={"users"})
    existing = await db["users"].count_documents({})

    if existing:
        LoggerHelper.info(f"Ya existen {existing} usuarios; semilla de usuario omitida.")
        return

    LoggerHelper.info("Insertando usuarios semilla...")

    # Cargamos rol por nombre para usar role_id (ObjectId) en usuario
    roles_cursor = await db["roles"].find({}, {"_id": 1, "name": 1}).to_list(length=1000)
    roles_map = {r["name"]: str(r["_id"]) for r in roles_cursor}

    for user in DEFAULT_USERS:
        role_name = user.pop("role_name", None)
        user_payload = user.copy()

        if role_name and role_name in roles_map:
            user_payload["role_id"] = roles_map[role_name]
        else:
            LoggerHelper.warning(f"Rol no encontrado para usuario {user['email']}: {role_name}")

        try:
            await mongo.insert_one("users", user_payload)
            LoggerHelper.success(f"Usuario creado: {user_payload['email']}")
        except Exception as exc:
            LoggerHelper.warning(f"No se pudo crear usuario {user_payload['email']}: {exc}")

    LoggerHelper.success("Seeders de usuarios finalizado")
