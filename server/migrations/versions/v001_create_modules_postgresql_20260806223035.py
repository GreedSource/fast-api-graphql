from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncConnection

version = "001_create_modules_postgresql_20260806223035"
description = "Create modules table"


async def upgrade(conn: AsyncConnection) -> None:
    await conn.execute(
        text(
            """
            CREATE TABLE IF NOT EXISTS modules (
                id UUID PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                key VARCHAR(50) NOT NULL,
                description VARCHAR(255),
                active BOOLEAN NOT NULL DEFAULT TRUE
            )
            """
        )
    )
    await conn.execute(text("CREATE UNIQUE INDEX IF NOT EXISTS ix_modules_key ON modules (key)"))
