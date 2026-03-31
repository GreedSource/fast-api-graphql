import importlib
from pathlib import Path
from typing import Callable, List, Tuple

from server.helpers.logger_helper import LoggerHelper

MIGRATIONS_PACKAGE = Path(__file__).resolve().parent


def _find_migration_modules() -> List[str]:
    files = sorted(MIGRATIONS_PACKAGE.glob("*.py"))
    return [f.stem for f in files if f.stem != "__init__"]


def _load_migrations() -> List[Tuple[str, str, Callable]]:
    migrations = []
    for module_name in _find_migration_modules():
        module = importlib.import_module(f"server.db.migrations.{module_name}")

        if not hasattr(module, "MIGRATION_NAME") or not hasattr(module, "upgrade"):
            LoggerHelper.warning(f"Módulo de migración ignorado (no está bien formado): {module_name}")
            continue

        description = getattr(module, "MIGRATION_DESCRIPTION", "")
        migrations.append((module.MIGRATION_NAME, description, module.upgrade))

    # Colocar en orden por nombre (0001, 0002, ...)
    migrations.sort(key=lambda item: item[0])
    return migrations


async def run_migrations(db):
    from datetime import datetime

    migrations_collection = db["migrations"]
    await migrations_collection.create_index("name", unique=True, name="migrations_name_unique_idx")

    applied = await migrations_collection.find({}).to_list(length=1000)
    applied_names = {m["name"] for m in applied}

    for name, description, upgrade in _load_migrations():
        if name in applied_names:
            LoggerHelper.info(f"Migración ya aplicada: {name}")
            continue

        LoggerHelper.info(f"Aplicando migración: {name} - {description}")
        await upgrade(db)

        await migrations_collection.insert_one(
            {
                "name": name,
                "description": description,
                "applied_at": datetime.now(),
            }
        )

        LoggerHelper.success(f"Migración aplicada: {name}")

    LoggerHelper.success("Todas las migraciones procesadas")
