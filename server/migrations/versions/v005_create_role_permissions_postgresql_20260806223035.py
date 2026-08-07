from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncConnection

version = "005_create_role_permissions_postgresql_20260806223035"
description = "Create role permissions relation table"


async def upgrade(conn: AsyncConnection) -> None:
    await conn.execute(
        text(
            """
            CREATE TABLE IF NOT EXISTS role_permissions (
                role_id UUID NOT NULL REFERENCES roles(id) ON DELETE CASCADE,
                permission_id UUID NOT NULL REFERENCES permissions(id) ON DELETE CASCADE,
                PRIMARY KEY (role_id, permission_id)
            )
            """
        )
    )
