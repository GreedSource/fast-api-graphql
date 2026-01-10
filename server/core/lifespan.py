from contextlib import asynccontextmanager
from fastapi import FastAPI

from server.db.mongo import get_mongo_db, close_mongo
from server.helpers.mongo_helper import MongoHelper
from server.helpers.logger_helper import LoggerHelper


@asynccontextmanager
async def lifespan(app: FastAPI):
    LoggerHelper.info("Starting application...")

    db = get_mongo_db()

    mongo = MongoHelper(
        db=db,
        allowed_collections={"users"},
    )

    await mongo.create_index(
        collection_name="users",
        keys=[("email", 1)],
        unique=True,
        name="users_email_unique_idx",
    )

    LoggerHelper.success("MongoDB ready")

    yield

    LoggerHelper.info("Shutting down application...")
    await close_mongo()
    LoggerHelper.info("Application shutdown complete.")
