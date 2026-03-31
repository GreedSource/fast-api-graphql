from server.helpers.mongo_helper import MongoHelper

MIGRATION_NAME = "0005_permissions"
MIGRATION_DESCRIPTION = "Crear índices y validación de permisos"


def _default_validator():
    return {
        "$jsonSchema": {
            "bsonType": "object",
            "required": ["action_id", "module_id", "created_at", "updated_at"],
            "properties": {
                "action_id": {"bsonType": "objectId"},
                "module_id": {"bsonType": "objectId"},
                "created_at": {"bsonType": "date"},
                "updated_at": {"bsonType": "date"},
            },
        }
    }


async def upgrade(db):
    mongo = MongoHelper(db=db, allowed_collections={"permissions"})
    await mongo.create_index(
        "permissions",
        [("action_id", 1), ("module_id", 1)],
        unique=True,
        name="permission_unique_idx",
    )

    if "permissions" not in await db.list_collection_names():
        await db.create_collection(
            "permissions",
            validator=_default_validator(),
            validationLevel="moderate",
            validationAction="error",
        )
    else:
        await db.command(
            {
                "collMod": "permissions",
                "validator": _default_validator(),
                "validationLevel": "moderate",
                "validationAction": "error",
            }
        )
