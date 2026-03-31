from server.helpers.mongo_helper import MongoHelper

MIGRATION_NAME = "0004_actions"
MIGRATION_DESCRIPTION = "Crear índices y validación de acciones"


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
    mongo = MongoHelper(db=db, allowed_collections={"actions"})
    await mongo.create_index("actions", [("name", 1)], unique=True, name="actions_name_unique_idx")
    await mongo.create_index("actions", [("key", 1)], unique=True, name="actions_key_unique_idx")

    if "actions" not in await db.list_collection_names():
        await db.create_collection(
            "actions",
            validator=_default_validator(),
            validationLevel="moderate",
            validationAction="error",
        )
    else:
        await db.command(
            {
                "collMod": "actions",
                "validator": _default_validator(),
                "validationLevel": "moderate",
                "validationAction": "error",
            }
        )
