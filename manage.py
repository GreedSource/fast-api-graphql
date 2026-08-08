import argparse
import asyncio

from server.config.settings import settings
from server.helpers.logger_helper import LoggerHelper


async def _run_migrate():
    from server.migrations import run_migrations

    run_migrations()


async def _run_seed_users():
    from server.seeders import seed_users

    await seed_users()


async def _run_seed_modules():
    from server.seeders import seed_modules

    await seed_modules()


async def _run_seed_actions():
    from server.seeders import seed_actions

    await seed_actions()


async def _run_seed_permissions():
    from server.seeders import seed_permissions

    await seed_permissions()


async def _run_seed_roles():
    from server.seeders import seed_roles

    await seed_roles()


async def _run_seed_project_roles():
    from server.seeders import seed_project_roles

    await seed_project_roles()


async def _run_seed_all():
    if not settings.RUN_SEEDERS:
        LoggerHelper.info("RUN_SEEDERS=false, semilla global omitida.")
        return

    from server.seeders import seed_all

    await seed_all()


async def _run_status():
    from sqlalchemy import text

    from server.db.session import engine
    from server.migrations import (
        MIGRATIONS_TABLE,
        _ensure_migrations_table,
        _get_applied_versions,
        _load_migrations,
    )

    LoggerHelper.info("Verificando conexión a PostgreSQL...")
    async with engine.connect() as conn:
        result = await conn.execute(text("SELECT version()"))
        version = result.scalar()
        LoggerHelper.info(f"Conectado a: {version}")

        await _ensure_migrations_table(conn)
        applied_versions = await _get_applied_versions(conn)
        migrations = _load_migrations()
        pending = [migration.version for migration in migrations if migration.version not in applied_versions]

        LoggerHelper.info(f"Tabla de migraciones: {MIGRATIONS_TABLE}")
        LoggerHelper.info(f"Migraciones aplicadas: {len(applied_versions)}")
        LoggerHelper.info(f"Migraciones pendientes: {len(pending)}")
        for version_name in pending:
            LoggerHelper.warning(f"Pendiente: {version_name}")


def main():
    parser = argparse.ArgumentParser(description="Gestor de migraciones y seeders para FastAPI GraphQL")
    parser.add_argument(
        "command",
        choices=[
            "migrate",
            "seed-modules",
            "seed-actions",
            "seed-permissions",
            "seed-roles",
            "seed-project-roles",
            "seed-users",
            "seed-all",
            "status",
        ],
        help="Comando a ejecutar",
    )
    args = parser.parse_args()

    if args.command == "migrate":
        # run_migrations es síncrona (usa asyncio.run internamente)
        from server.migrations import run_migrations

        run_migrations()
    elif args.command == "seed-modules":
        asyncio.run(_run_seed_modules())
    elif args.command == "seed-actions":
        asyncio.run(_run_seed_actions())
    elif args.command == "seed-permissions":
        asyncio.run(_run_seed_permissions())
    elif args.command == "seed-roles":
        asyncio.run(_run_seed_roles())
    elif args.command == "seed-project-roles":
        asyncio.run(_run_seed_project_roles())
    elif args.command == "seed-users":
        asyncio.run(_run_seed_users())
    elif args.command == "seed-all":
        asyncio.run(_run_seed_all())
    elif args.command == "status":
        asyncio.run(_run_status())


if __name__ == "__main__":
    main()
