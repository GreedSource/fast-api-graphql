from server.helpers.mongo_helper import MongoHelper

MIGRATION_NAME = "0003_modules"
MIGRATION_DESCRIPTION = "Crear índices y validación de módulos"


def _default_validator():
    return {
        "$jsonSchema": {
            "bsonType": "object",
            "required": ["name", "key", "created_at", "updated_at"],
            "properties": {
                "name": {"bsonType": "string"},
                "key": {"bsonType": "string"},
                "description": {"bsonType": ["string", "null"]},
                "active": {"bsonType": "bool"},
                "created_at": {"bsonType": "date"},
                "updated_at": {"bsonType": "date"},
            },
        }
    }


async def upgrade(db):
    mongo = MongoHelper(db=db, allowed_collections={"modules"})
    await mongo.create_index("modules", [("name", 1)], unique=True, name="modules_name_unique_idx")
    await mongo.create_index("modules", [("key", 1)], unique=True, name="modules_key_unique_idx")

    if "modules" not in await db.list_collection_names():
        await db.create_collection(
            "modules",
            validator=_default_validator(),
            validationLevel="moderate",
            validationAction="error",
        )
    else:
        await db.command(
            {
                "collMod": "modules",
                "validator": _default_validator(),
                "validationLevel": "moderate",
                "validationAction": "error",
            }
        )
