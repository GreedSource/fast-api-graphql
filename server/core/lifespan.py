from contextlib import asynccontextmanager

from fastapi import FastAPI

from server.db.mongo import close_mongo, get_mongo_db
from server.helpers.logger_helper import LoggerHelper
from server.helpers.mongo_helper import MongoHelper


@asynccontextmanager
async def lifespan(app: FastAPI):
    LoggerHelper.info("Starting application...")

    db = get_mongo_db()

    mongo = MongoHelper(
        db=db,
        allowed_collections={"users", "roles", "modules", "actions", "permissions"},
    )

    await mongo.create_index(
        collection_name="users",
        keys=[("email", 1)],
        unique=True,
        name="users_email_unique_idx",
    )

    await mongo.create_index(
        collection_name="roles",
        keys=[("name", 1)],
        unique=True,
        name="roles_name_unique_idx",
    )

    await mongo.create_index(
        collection_name="modules",
        keys=[("name", 1)],
        unique=True,
        name="modules_name_unique_idx",
    )

    await mongo.create_index(
        collection_name="modules",
        keys=[("key", 1)],
        unique=True,
        name="modules_key_unique_idx",
    )

    await mongo.create_index(
        collection_name="actions",
        keys=[("name", 1)],
        unique=True,
        name="actions_name_unique_idx",
    )

    await mongo.create_index(
        collection_name="actions",
        keys=[("key", 1)],
        unique=True,
        name="actions_key_unique_idx",
    )

    await mongo.create_index(
        collection_name="permissions",
        keys=[("action_id", 1), ("module_id", 1)],
        unique=True,
        name="permission_unique_idx",
    )

    LoggerHelper.success("MongoDB ready")

    yield

    LoggerHelper.info("Shutting down application...")
    await close_mongo()
    LoggerHelper.info("Application shutdown complete.")
