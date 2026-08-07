from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncConnection

version = "004_create_permissions_postgresql_20260806223035"
description = "Create permissions table"


async def upgrade(conn: AsyncConnection) -> None:
    await conn.execute(
        text(
            """
            CREATE TABLE IF NOT EXISTS permissions (
                id UUID PRIMARY KEY,
                module_id UUID NOT NULL REFERENCES modules(id) ON DELETE CASCADE,
                action_id UUID NOT NULL REFERENCES actions(id) ON DELETE CASCADE,
                description VARCHAR(255),
                CONSTRAINT uq_module_action UNIQUE (module_id, action_id)
            )
            """
        )
    )
