from server.helpers.mongo_helper import MongoHelper

MIGRATION_NAME = "0001_users"
MIGRATION_DESCRIPTION = "Crear índices y validación de usuarios"


def _user_validator():
    return {
        "$jsonSchema": {
            "bsonType": "object",
            "required": ["name", "lastname", "email", "password", "created_at", "updated_at"],
            "properties": {
                "name": {"bsonType": "string"},
                "lastname": {"bsonType": "string"},
                "email": {"bsonType": "string", "pattern": "^.+@.+$"},
                "password": {"bsonType": "string"},
                "role_id": {
                    "bsonType": "string",
                    "description": "ID del rol asociado al usuario",
                },
                "active": {"bsonType": "bool"},
                "created_at": {"bsonType": "date"},
                "updated_at": {"bsonType": "date"},
            },
        }
    }


async def upgrade(db):
    mongo = MongoHelper(db=db, allowed_collections={"users"})
    await mongo.create_index("users", [("email", 1)], unique=True, name="users_email_unique_idx")

    if "users" not in await db.list_collection_names():
        await db.create_collection(
            "users",
            validator=_user_validator(),
            validationLevel="moderate",
            validationAction="error",
        )
    else:
        await db.command(
            {
                "collMod": "users",
                "validator": _user_validator(),
                "validationLevel": "moderate",
                "validationAction": "error",
            }
        )
