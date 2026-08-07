from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncConnection

version = "002_create_actions_postgresql_20260806223035"
description = "Create actions table"


async def upgrade(conn: AsyncConnection) -> None:
    await conn.execute(
        text(
            """
            CREATE TABLE IF NOT EXISTS actions (
                id UUID PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                key VARCHAR(50) NOT NULL,
                description VARCHAR(255),
                active BOOLEAN NOT NULL DEFAULT TRUE
            )
            """
        )
    )
    await conn.execute(text("CREATE UNIQUE INDEX IF NOT EXISTS ix_actions_key ON actions (key)"))
