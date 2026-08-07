import asyncio
from dataclasses import dataclass
from datetime import datetime, timezone
from importlib import import_module
from pathlib import Path
from types import ModuleType

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncConnection

from server.db.session import engine
from server.helpers.logger_helper import LoggerHelper

MIGRATIONS_TABLE = "schema_migrations"


@dataclass(frozen=True)
class Migration:
    version: str
    description: str
    module: ModuleType


def _load_migrations() -> list[Migration]:
    versions_path = Path(__file__).parent / "versions"
    migrations: list[Migration] = []

    for path in sorted(versions_path.glob("v*.py")):
        if path.name == "__init__.py":
            continue

        module_name = f"server.migrations.versions.{path.stem}"
        module = import_module(module_name)
        version = getattr(module, "version", path.stem.removeprefix("v"))
        description = getattr(module, "description", "")

        if not hasattr(module, "upgrade"):
            raise RuntimeError(f"La migración {module_name} no define upgrade(conn).")

        migrations.append(Migration(version=version, description=description, module=module))

    return migrations


async def _ensure_migrations_table(conn: AsyncConnection) -> None:
    await conn.execute(
        text(
            f"""
            CREATE TABLE IF NOT EXISTS {MIGRATIONS_TABLE} (
                version VARCHAR(255) PRIMARY KEY,
                description VARCHAR(255),
                applied_at TIMESTAMP WITH TIME ZONE NOT NULL
            )
            """
        )
    )


async def _get_applied_versions(conn: AsyncConnection) -> set[str]:
    result = await conn.execute(text(f"SELECT version FROM {MIGRATIONS_TABLE}"))
    return {row[0] for row in result.fetchall()}


async def _record_migration(conn: AsyncConnection, migration: Migration) -> None:
    await conn.execute(
        text(
            f"""
            INSERT INTO {MIGRATIONS_TABLE} (version, description, applied_at)
            VALUES (:version, :description, :applied_at)
            """
        ),
        {
            "version": migration.version,
            "description": migration.description,
            "applied_at": datetime.now(timezone.utc),
        },
    )


async def async_run_migrations() -> None:
    migrations = _load_migrations()

    async with engine.begin() as conn:
        await _ensure_migrations_table(conn)
        applied_versions = await _get_applied_versions(conn)

        pending = [migration for migration in migrations if migration.version not in applied_versions]
        if not pending:
            LoggerHelper.info("No hay migraciones pendientes.")
            return

        for migration in pending:
            LoggerHelper.info(f"Aplicando migración {migration.version}...")
            await migration.module.upgrade(conn)
            await _record_migration(conn, migration)
            LoggerHelper.success(f"Migración {migration.version} aplicada.")


def run_migrations() -> None:
    asyncio.run(async_run_migrations())


__all__ = ["run_migrations"]
