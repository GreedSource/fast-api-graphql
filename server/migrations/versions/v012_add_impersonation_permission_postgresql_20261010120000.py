import uuid

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncConnection

version = "012_add_impersonation_permission_postgresql_20261010120000"
description = "Add the user impersonation permission and grant it to system administrators"


async def upgrade(conn: AsyncConnection) -> None:
    await conn.execute(
        text(
            """
            INSERT INTO actions (id, name, key, description, active)
            VALUES (:id, 'Impersonar', 'impersonate',
                    'Permite iniciar una sesión temporal como otro usuario', TRUE)
            ON CONFLICT (key) DO NOTHING
            """
        ),
        {"id": uuid.uuid4()},
    )
    await conn.execute(
        text(
            """
            INSERT INTO permissions (id, module_id, action_id, description)
            SELECT :permission_id, modules.id, actions.id, 'Permiso users:impersonate'
            FROM modules
            CROSS JOIN actions
            WHERE modules.key = 'users' AND actions.key = 'impersonate'
            ON CONFLICT (module_id, action_id) DO NOTHING
            """
        ),
        {"permission_id": uuid.uuid4()},
    )
    await conn.execute(
        text(
            """
            INSERT INTO role_permissions (role_id, permission_id)
            SELECT roles.id, permissions.id
            FROM roles
            CROSS JOIN modules
            JOIN actions ON actions.key = 'impersonate'
            JOIN permissions ON permissions.module_id = modules.id
                AND permissions.action_id = actions.id
            WHERE modules.key = 'users' AND roles.name IN ('admin', 'super_admin')
            ON CONFLICT DO NOTHING
            """
        )
    )
