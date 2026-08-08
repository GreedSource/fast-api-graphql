from server.helpers.logger_helper import LoggerHelper
from server.seeders.actions_seeder import seed as seed_actions
from server.seeders.demo_seeder import seed as seed_demo
from server.seeders.modules_seeder import seed as seed_modules
from server.seeders.permissions_seeder import seed as seed_permissions
from server.seeders.project_roles_seeder import seed as seed_project_roles
from server.seeders.roles_seeder import seed as seed_roles
from server.seeders.users_seeder import seed as seed_users


async def seed_all():
    LoggerHelper.info("Iniciando ejecución de todos los seeders en PostgreSQL...")
    await seed_modules()
    await seed_actions()
    await seed_permissions()
    await seed_roles()
    await seed_project_roles()
    await seed_demo()
    await seed_users()
    LoggerHelper.success("Ejecución de seeders en PostgreSQL completada exitosamente.")


__all__ = [
    "seed_modules",
    "seed_actions",
    "seed_permissions",
    "seed_roles",
    "seed_project_roles",
    "seed_demo",
    "seed_users",
    "seed_all",
]
