import argparse
import asyncio

from server.config.settings import settings
from server.db.mongo import get_mongo_db
from server.helpers.logger_helper import LoggerHelper


async def _run_migrate():
    from server.db.migrations import run_migrations

    db = get_mongo_db()
    await run_migrations(db)


async def _run_seed_users():
    from server.db.seeders import seed_users

    db = get_mongo_db()
    await seed_users(db)


async def _run_seed_modules():
    from server.db.seeders import seed_modules

    db = get_mongo_db()
    await seed_modules(db)


async def _run_seed_actions():
    from server.db.seeders import seed_actions

    db = get_mongo_db()
    await seed_actions(db)


async def _run_seed_permissions():
    from server.db.seeders import seed_permissions

    db = get_mongo_db()
    await seed_permissions(db)


async def _run_seed_roles():
    from server.db.seeders import seed_roles

    db = get_mongo_db()
    await seed_roles(db)


async def _run_seed_all():
    if not settings.RUN_SEEDERS:
        LoggerHelper.info("RUN_SEEDERS=false, semilla global omitida.")
        return

    from server.db.seeders import seed_all

    db = get_mongo_db()
    await seed_all(db)


async def _run_status():
    db = get_mongo_db()
    migrations = await db["migrations"].find({}).to_list(length=100)
    LoggerHelper.info("Migraciones aplicadas:")
    for m in migrations:
        LoggerHelper.info(f"- {m.get('name')} @ {m.get('applied_at')}")


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
            "seed-users",
            "seed-all",
            "status",
        ],
        help="Comando a ejecutar",
    )
    args = parser.parse_args()

    if args.command == "migrate":
        asyncio.run(_run_migrate())
    elif args.command == "seed-modules":
        asyncio.run(_run_seed_modules())
    elif args.command == "seed-actions":
        asyncio.run(_run_seed_actions())
    elif args.command == "seed-permissions":
        asyncio.run(_run_seed_permissions())
    elif args.command == "seed-roles":
        asyncio.run(_run_seed_roles())
    elif args.command == "seed-users":
        asyncio.run(_run_seed_users())
    elif args.command == "seed-all":
        asyncio.run(_run_seed_all())
    elif args.command == "status":
        asyncio.run(_run_status())


if __name__ == "__main__":
    main()
