from contextlib import asynccontextmanager

from fastapi import FastAPI

from server.db.session import engine
from server.helpers.logger_helper import LoggerHelper
from server.helpers.redis_helper import RedisHelper


@asynccontextmanager
async def lifespan(app: FastAPI):
    LoggerHelper.info("Starting application...")
    LoggerHelper.success("PostgreSQL engine ready")

    yield

    LoggerHelper.info("Shutting down application...")
    await RedisHelper().close()
    await engine.dispose()
    LoggerHelper.info("Application shutdown complete.")
