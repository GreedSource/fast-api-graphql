from server.helpers.mongo_helper import MongoHelper

MIGRATION_NAME = "0002_roles"
MIGRATION_DESCRIPTION = "Crear índices y validación de roles"


def _default_validator():
    return {
        "$jsonSchema": {
            "bsonType": "object",
            "required": ["name", "created_at", "updated_at"],
            "properties": {
                "name": {"bsonType": "string"},
                "description": {"bsonType": ["string", "null"]},
                "active": {"bsonType": "bool"},
                "permissions": {"bsonType": ["array", "null"]},
                "created_at": {"bsonType": "date"},
                "updated_at": {"bsonType": "date"},
            },
        }
    }


async def upgrade(db):
    mongo = MongoHelper(db=db, allowed_collections={"roles"})
    await mongo.create_index("roles", [("name", 1)], unique=True, name="roles_name_unique_idx")

    if "roles" not in await db.list_collection_names():
        await db.create_collection(
            "roles",
            validator=_default_validator(),
            validationLevel="moderate",
            validationAction="error",
        )
    else:
        await db.command(
            {
                "collMod": "roles",
                "validator": _default_validator(),
                "validationLevel": "moderate",
                "validationAction": "error",
            }
        )
