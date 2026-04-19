import importlib
from pathlib import Path
from typing import Any, Awaitable, Callable

from motor.motor_asyncio import AsyncIOMotorDatabase

from server.helpers.logger_helper import LoggerHelper

TASKS_DIR = Path(__file__).resolve().parent


def _find_seeder_modules() -> list[str]:
    files = sorted(TASKS_DIR.glob("*.py"))
    return [f.stem for f in files if f.stem != "__init__"]


SeederCallable = Callable[[AsyncIOMotorDatabase[dict[str, Any]]], Awaitable[None]]


def _load_seeders() -> list[SeederCallable]:
    seeders: list[SeederCallable] = []
    for module_name in _find_seeder_modules():
        module = importlib.import_module(f"server.db.seeders.{module_name}")

        if not hasattr(module, "seed"):
            LoggerHelper.warning(f"Módulo de seeder ignorado (no tiene función seed): {module_name}")
            continue

        seeders.append(module.seed)

    return seeders


async def seed_all(db: AsyncIOMotorDatabase[dict[str, Any]]) -> None:
    await seed_modules(db)
    await seed_actions(db)
    await seed_permissions(db)
    await seed_roles(db)
    await seed_users(db)


async def seed_users(db: AsyncIOMotorDatabase[dict[str, Any]]) -> None:
    from server.db.seeders.users import seed as _seed

    await _seed(db)


async def seed_modules(db: AsyncIOMotorDatabase[dict[str, Any]]) -> None:
    from server.db.seeders.modules import seed as _seed

    await _seed(db)


async def seed_actions(db: AsyncIOMotorDatabase[dict[str, Any]]) -> None:
    from server.db.seeders.actions import seed as _seed

    await _seed(db)


async def seed_permissions(db: AsyncIOMotorDatabase[dict[str, Any]]) -> None:
    from server.db.seeders.permissions import seed as _seed

    await _seed(db)


async def seed_roles(db: AsyncIOMotorDatabase[dict[str, Any]]) -> None:
    from server.db.seeders.roles import seed as _seed

    await _seed(db)
