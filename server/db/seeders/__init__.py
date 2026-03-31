import importlib
from pathlib import Path
from typing import Callable, List

from server.helpers.logger_helper import LoggerHelper

TASKS_DIR = Path(__file__).resolve().parent


def _find_seeder_modules() -> List[str]:
    files = sorted(TASKS_DIR.glob("*.py"))
    return [f.stem for f in files if f.stem != "__init__"]


def _load_seeders() -> List[Callable]:
    seeders = []
    for module_name in _find_seeder_modules():
        module = importlib.import_module(f"server.db.seeders.{module_name}")

        if not hasattr(module, "seed"):
            LoggerHelper.warning(f"Módulo de seeder ignorado (no tiene función seed): {module_name}")
            continue

        seeders.append(module.seed)

    return seeders


async def seed_all(db):
    # Orden explícito para que dependencias existan
    await seed_modules(db)
    await seed_actions(db)
    await seed_permissions(db)
    await seed_roles(db)
    await seed_users(db)


async def seed_users(db):
    from server.db.seeders.users import seed as _seed

    await _seed(db)


async def seed_modules(db):
    from server.db.seeders.modules import seed as _seed

    await _seed(db)


async def seed_actions(db):
    from server.db.seeders.actions import seed as _seed

    await _seed(db)


async def seed_permissions(db):
    from server.db.seeders.permissions import seed as _seed

    await _seed(db)


async def seed_roles(db):
    from server.db.seeders.roles import seed as _seed

    await _seed(db)
